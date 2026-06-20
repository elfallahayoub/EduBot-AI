import pickle
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        # L2-normalized vectors + inner-product index = cosine similarity search
        self.index   = faiss.IndexFlatIP(dimension)
        self.chunks  : List[str] = []
        self.sources : List[str] = []

    def add_chunks(self, chunks: List[str], embeddings: np.ndarray, source: str = "unknown") -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must match.")
        self.index.add(self._normalize(embeddings))
        self.chunks.extend(chunks)
        self.sources.extend([source] * len(chunks))

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Tuple[str, float, str]]:
        if self.index.ntotal == 0:
            return []
        q = self._normalize(query_vector.reshape(1, -1))
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, k)
        return [
            (self.chunks[idx], float(score), self.sources[idx])
            for score, idx in zip(scores[0], indices[0])
            if idx >= 0
        ]

    def save_to_disk(self, path: str) -> None:
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(save_dir / "index.faiss"))
        with open(save_dir / "metadata.pkl", "wb") as f:
            pickle.dump({"chunks": self.chunks, "sources": self.sources, "dimension": self.dimension}, f)

    @classmethod
    def load_from_disk(cls, path: str) -> "VectorStore":
        load_dir = Path(path)
        if not load_dir.exists():
            raise FileNotFoundError(f"VectorStore directory not found: {path}")
        with open(load_dir / "metadata.pkl", "rb") as f:
            meta = pickle.load(f)
        store = cls(dimension=meta["dimension"])
        store.index   = faiss.read_index(str(load_dir / "index.faiss"))
        store.chunks  = meta["chunks"]
        store.sources = meta["sources"]
        return store

    @staticmethod
    def _normalize(matrix: np.ndarray) -> np.ndarray:
        mat   = matrix.astype(np.float32)
        norms = np.linalg.norm(mat, axis=-1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return mat / norms

    def __len__(self) -> int:
        return self.index.ntotal


if __name__ == "__main__":
    import tempfile, shutil

    print("=== Test vector_store.py ===\n")

    store = VectorStore(dimension=4)
    chunks = ["Le cours commence à 9h.", "L'examen est en janvier.", "Bonjour à tous !"]
    embeddings = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.7, 0.7, 0.0, 0.0],
    ], dtype=np.float32)

    store.add_chunks(chunks, embeddings, source="test_doc.txt")
    print(f"Vecteurs indexés : {len(store)}")

    query   = np.array([0.1, 0.9, 0.0, 0.0], dtype=np.float32)
    results = store.search(query, top_k=2)
    print("Résultats (top-2) :")
    for text, score, src in results:
        print(f"  [{score:.4f}] ({src}) {text}")

    tmp_dir = tempfile.mkdtemp()
    store.save_to_disk(tmp_dir)
    store2   = VectorStore.load_from_disk(tmp_dir)
    results2 = store2.search(query, top_k=2)
    shutil.rmtree(tmp_dir)

    assert results == results2
    print("\nTest vector_store.py : OK")
