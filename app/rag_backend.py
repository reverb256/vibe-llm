import os
from typing import List, Dict, Any
from transformers import pipeline
import torch

class RAGBackend:
    """
    Simple RAG (Retrieval-Augmented Generation) backend using HuggingFace pipelines and local corpus.
    """
    def __init__(self, model_name: str, corpus: List[str]):
        self.model_name = model_name
        self.corpus = corpus
        self.device = 0 if torch.cuda.is_available() else -1
        self.generator = pipeline("text-generation", model=model_name, device=self.device)
        # For demo: use a simple embedding model for retrieval
        self.embedder = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2", device=self.device)

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        # Embed query and corpus, return top_k most similar
        import numpy as np
        query_emb = self.embedder(query)[0][0]
        corpus_embs = [self.embedder(doc)[0][0] for doc in self.corpus]
        sims = [np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)) for doc_emb in corpus_embs]
        top_indices = np.argsort(sims)[-top_k:][::-1]
        return [self.corpus[i] for i in top_indices]

    def chat(self, messages: List[Dict[str, Any]], max_new_tokens: int = 128, temperature: float = 0.7):
        # Use last user message as query
        query = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                query = m.get("content", "")
                break
        context_docs = self.retrieve(query)
        context = "\n".join(context_docs)
        prompt = f"Context:\n{context}\n\nUser: {query}\nAssistant:"
        response = self.generator(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True)[0]["generated_text"]
        return response[len(prompt):].strip()
