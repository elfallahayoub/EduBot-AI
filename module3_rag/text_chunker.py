import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNK_SIZE, LINES_PER_CHUNK, LINES_OVERLAP


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    lines_per_chunk: int = LINES_PER_CHUNK,
    lines_overlap: int = LINES_OVERLAP,
) -> List[str]:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return []

    expanded: List[str] = []
    for line in lines:
        words = line.split()
        if len(words) <= chunk_size:
            expanded.append(line)
        else:
            for i in range(0, len(words), chunk_size):
                expanded.append(" ".join(words[i : i + chunk_size]))

    chunks: List[str] = []
    step = max(1, lines_per_chunk - lines_overlap)
    i = 0

    while i < len(expanded):
        chunks.append("\n".join(expanded[i : i + lines_per_chunk]))
        i += step

    return chunks


if __name__ == "__main__":
    sample = (
        "Calendrier des examens\n\n"
        "Mathematiques : 9 juin 2026, 09h00, Salle A101\n"
        "Algorithmique : 11 juin 2026, 14h00, Salle B203\n"
        "Bases de Donnees : 12 juin 2026, 09h00, Labo Info\n\n"
        "Reglement : carte etudiante obligatoire."
    )

    chunks = chunk_text(sample)
    for i, c in enumerate(chunks):
        print(f"[{i+1}] {c!r}")

    assert chunk_text("") == []
    assert len(chunk_text("une seule ligne")) == 1
    print("text_chunker.py: OK")
