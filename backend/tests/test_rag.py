from services.rag_services import search_documents

question = """
Apa kualifikasi pendidikan kepala perpustakaan?
"""

results = search_documents(question)

print("="*50)

for i, doc in enumerate(results["documents"]):

    print(f"\nHASIL {i+1}")

    print("\nMETADATA:")
    print(results["metadata"][i])

    print("\nDOKUMEN:")
    print(doc[:1000])