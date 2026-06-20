import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size}).")

    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    step  = chunk_size - overlap
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step

    return chunks


if __name__ == "__main__":
    print("=== Test text_chunker.py ===\n")

    sample = (
        "L'algorithmique est la science des algorithmes. "
        "Un algorithme est une suite finie et ordonnée d'instructions. "
        "Il permet de résoudre un problème de manière systématique. "
        "En informatique, les algorithmes sont traduits en programmes. "
        "La complexité algorithmique mesure l'efficacité d'un algorithme. "
        "La notation Big-O décrit le comportement asymptotique dans le pire cas. "
        "Le tri fusion a une complexité de O(n log n) garantie. "
        "Le tri rapide a une complexité moyenne de O(n log n) mais O(n²) dans le pire cas."
    )

    chunks = chunk_text(sample, chunk_size=20, overlap=5)
    print(f"Texte : {len(sample.split())} mots")
    print(f"Chunks générés (chunk_size=20, overlap=5) : {len(chunks)}\n")
    for i, c in enumerate(chunks):
        print(f"  Chunk {i+1} ({len(c.split())} mots) : {c[:80]}...")

    assert chunk_text("", chunk_size=10, overlap=2) == []
    assert len(chunk_text("un seul mot", chunk_size=10, overlap=2)) == 1
    try:
        chunk_text("test", chunk_size=10, overlap=10)
        assert False
    except ValueError:
        pass

    print("\nTest text_chunker.py : OK")
