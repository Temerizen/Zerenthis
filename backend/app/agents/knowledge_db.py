# knowledge_db.py
from chromadb.utils import embedding_functions
import chromadb

client = chromadb.Client()
collection_name = "ai_knowledge"

if collection_name not in [c.name for c in client.list_collections()]:
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    )
else:
    collection = client.get_collection(collection_name)

def add_document(text, source="unknown", page=0, doc_id=None):
    if not doc_id:
        doc_id = f"{source}_{page}"
    collection.add(documents=[text], metadatas=[{"source": source, "page": page}], ids=[doc_id])

def query_documents(query_text, n_results=3):
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results['documents'][0], results['metadatas'][0]
