import chromadb
from chromadb.utils import embedding_functions
from typing import List

class ChromaRAG:
    def __init__(self, db_path="./rag_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("docs")
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    def add_documents(self, docs: List[str], metadatas=None):
        metadatas = metadatas or [{} for _ in docs]
        ids = [f"doc_{i}" for i in range(len(docs))]
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def query(self, query: str, top_k=3):
        results = self.collection.query(query_texts=[query], n_results=top_k, embedding_function=self.embedder)
        return [doc for doc in results["documents"][0]]
