import os
from services.rag_services import search_documents
from services.llm_services import ask_llm
from services.intent_services import classify_intent
from services.prompt_services import load_prompt

# Import kebutuhan database
from database import SessionLocal, User, ChatHistory


def answer_question(question: str, user_id: str = "UNKNOWN_USER", name: str = "Tamu", session_id: str = "DEFAULT_SESSION"):
    # 1. Buka session database
    db = SessionLocal()
    
    # Siapkan variabel fallback default
    fallback_text = (
        "Pertanyaan Anda berada di luar basis pengetahuan SAPA PUSTAKA. "
        "Silakan hubungi pustakawan +62 881-0821-52119."
    )
    
    try:
        # 2. OTOMATIS DAFTAR/CEK USER
        existing_user = db.query(User).filter(User.user_id == user_id).first()
        if not existing_user:
            existing_user = User(
                user_id=user_id,
                name=name,
                library_type="UNKNOWN"  # Akan diupdate jika terdeteksi dari dokumen RAG
            )
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)

        # 3. KLASIFIKASI INTENT
        intent = classify_intent(question)

        # ====================================
        # GREETING
        # ====================================
        if intent == "greeting":
            prompt = load_prompt("greeting_prompt.txt")
            answer = ask_llm(prompt)
            
            # Simpan chat ke database sebelum return
            _save_chat_pair(db, session_id, user_id, question, answer)
            return {"answer": answer}

        # ====================================
        # CLARIFICATION
        # ====================================
        if intent == "clarification":
            prompt_template = load_prompt("clarification_prompt.txt")
            prompt = prompt_template.format(question=question)
            answer = ask_llm(prompt)
            
            # Simpan chat ke database sebelum return
            _save_chat_pair(db, session_id, user_id, question, answer)
            return {"answer": answer}

        # ====================================
        # RAG RETRIEVAL
        # ====================================
        results = search_documents(question)

        docs = results["documents"]
        metadata = results["metadata"]
        scores = results["distances"]

        if not docs:
            _save_chat_pair(db, session_id, user_id, question, fallback_text)
            return {"answer": fallback_text, "sources": []}

        # ====================================
        # VALIDASI THRESHOLD (Hanya Cek Best Score)
        # ====================================
        best_score = scores[0]

        print("\nQUESTION:", question)
        print("BEST RERANK SCORE:", best_score)

        if metadata:
            print("\nTOP SOURCE:")
            print("SOURCE:", metadata[0].get("source"))
            print("COMPONENT:", metadata[0].get("component"))
            print("INDICATOR:", metadata[0].get("indicator"))
            
            # Otomatis perbarui tipe perpustakaan user berdasarkan dokumen RAG teratas
            rag_lib_type = metadata[0].get("library_type", "UNKNOWN")
            if rag_lib_type != "UNKNOWN" and existing_user.library_type != rag_lib_type:
                existing_user.library_type = rag_lib_type
                db.commit()

        # Jika kecocokan dokumen teratas sangat buruk, langsung tolak di awal
        if best_score < 0.50:
            _save_chat_pair(db, session_id, user_id, question, fallback_text)
            return {"answer": fallback_text, "sources": []}

        # ====================================
        # AKOMODASI PENDEKATAN 2 (Konteks Komponen Utuh)
        # ====================================
        if len(docs) > 0 and metadata[0].get("component") != "UNKNOWN_COMPONENT":
            filtered_docs = docs[:12]  
            filtered_metadata = metadata[:12]
        else:
            filtered_docs = []
            filtered_metadata = []
            for doc, meta, score in zip(docs, metadata, scores):
                if score < 0.60:
                    continue
                filtered_docs.append(doc)
                filtered_metadata.append(meta)

            if not filtered_docs:
                filtered_docs = docs[:5]
                filtered_metadata = metadata[:5]

        # ====================================
        # BUILD CONTEXT
        # ====================================
        context_parts = []
        for doc, meta in zip(filtered_docs, filtered_metadata):
            source = meta.get("source", "-")
            component = meta.get("component", "-")
            subcomponent = meta.get("subcomponent", "-")
            indicator = meta.get("indicator", "-")

            context_parts.append(
                f"SUMBER: {source}\nKOMPONEN: {component}\nSUBKOMPONEN: {subcomponent}\nINDIKATOR: {indicator}\nISI INSTRUMEN:\n{doc}"
            )

        context = "\n\n".join(context_parts)

        print("\n" + "=" * 80)
        print(f"CONTEXT SENT TO LLM ({len(filtered_docs)} CHUNKS)")
        print("=" * 80)
        print(context[:3000])
        print("=" * 80)

        # ====================================
        # GENERATE JAWABAN VIA LLM
        # ====================================
        prompt_template = load_prompt("rag_prompt.txt")
        prompt = prompt_template.format(context=context, question=question)

        answer = ask_llm(prompt)
        answer = answer.replace("**", "")  

        print("\nLLM ANSWER:")
        print(answer)

        # Validasi jawaban penolakan dari LLM
        if answer.strip() == "NOT_FOUND" or fallback_text.lower() in answer.lower():
            _save_chat_pair(db, session_id, user_id, question, fallback_text)
            return {"answer": fallback_text, "sources": []}

        # ====================================
        # DEDUPLIKASI & BERSIHKAN SUMBER PDF
        # ====================================
        unique_sources = []
        seen_files = set()

        for meta in filtered_metadata:
            file_name = meta.get("source", "-")
            if file_name not in seen_files and file_name != "-":
                seen_files.add(file_name)
                unique_sources.append({
                    "source": file_name,
                    "component": meta.get("component", "-"),
                    "library_type": meta.get("library_type", "-")
                })

        if not unique_sources and metadata:
            unique_sources = [{"source": metadata[0].get("source", "-")}]

        # Simpan sukses chat ke database sebelum return
        _save_chat_pair(db, session_id, user_id, question, answer)
        return {"answer": answer, "sources": unique_sources}

    except Exception as e:
        db.rollback()
        print(f"❌ Error Sistem Database: {e}")
        return {"answer": fallback_text, "sources": []}
        
    finally:
        # Selalu tutup session database
        db.close()


def _save_chat_pair(db, session_id, user_id, question, answer):
    """Helper function untuk menyimpan pesan User dan Assistant sekaligus"""
    try:
        chat_user = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            role="user",
            message=question
        )
        chat_bot = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            message=answer
        )
        db.add(chat_user)
        db.add(chat_bot)
        db.commit()
    except Exception as db_err:
        db.rollback()
        print(f"⚠️ Gagal menyimpan log chat: {db_err}")