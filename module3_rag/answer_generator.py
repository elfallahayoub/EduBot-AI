import os
import re
from pathlib import Path
from typing import Generator, List, Tuple

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

try:
    from google import genai
except ImportError:
    raise ImportError(
        "Package 'google-genai' requis. Installez-le avec : pip install google-genai"
    )

_client  = None
_ELISION = re.compile(r"\b\w'", re.UNICODE)
_MODEL   = "gemini-2.5-flash-lite"


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY introuvable. Vérifiez votre fichier .env.")
        _client = genai.Client(api_key=api_key)
    return _client


def _build_prompt(question: str, retrieved_chunks: List[Tuple[str, float, str]]) -> str:
    context_parts = []
    for i, (chunk, score, source) in enumerate(retrieved_chunks):
        context_parts.append(f"[Extrait {i+1} — {source}]\n{chunk}")
    context = "\n\n".join(context_parts)

    return f"""Tu es EduBot, un assistant académique intelligent qui aide les étudiants universitaires à exploiter leurs documents de cours.

Voici les extraits pertinents tirés des documents de l'étudiant :

{context}

Question de l'étudiant : {question}

Rédige une réponse en français qui :
- S'appuie sur les extraits ci-dessus comme source principale d'information
- Est bien structurée, claire et naturellement lisible
- Utilise du markdown si utile pour la mise en forme (listes à puces, **gras**, titres ##, etc.)
- Synthétise et explique l'information plutôt que de la recopier mot pour mot
- Cite précisément les données clés (dates, horaires, salles, notes, règlements, etc.)
- Répond de façon directe et utile, comme un tuteur bienveillant
- Si l'information demandée n'est pas dans les extraits, indique-le clairement et brièvement

Réponse :"""


def _fallback_answer(question: str, retrieved_chunks: List[Tuple[str, float, str]]) -> str:
    if not retrieved_chunks:
        return "Je n'ai pas pu générer une réponse. Vérifiez votre connexion et votre clé API."

    best_chunk, _, best_source = retrieved_chunks[0]
    lines = [l.strip() for l in best_chunk.split("\n") if l.strip()]

    q_clean  = _ELISION.sub("", question.lower())
    keywords = [w for w in q_clean.split() if len(w) > 3 or (w.isdigit() and 1 <= len(w) <= 3)]

    if keywords:
        relevant = [l for l in lines if any(kw in l.lower() for kw in keywords)]
        if relevant:
            lines = relevant

    body = "\n".join(f"• {l}" for l in lines) if len(lines) > 1 else (lines[0] if lines else best_chunk)
    return (
        f"_(Service de génération indisponible)_\n\n"
        f"D'après **{best_source}** :\n\n{body}"
    )


def generate_answer(question: str, retrieved_chunks: List[Tuple[str, float, str]]) -> str:
    prompt = _build_prompt(question, retrieved_chunks)
    try:
        client   = _get_client()
        response = client.models.generate_content(model=_MODEL, contents=prompt)
        if not hasattr(response, "text") or not response.text:
            raise ValueError("Gemini a retourné une réponse vide.")
        return response.text.strip()
    except Exception:
        return _fallback_answer(question, retrieved_chunks)


def generate_answer_stream(
    question: str, retrieved_chunks: List[Tuple[str, float, str]]
) -> Generator[str, None, None]:
    """Yields text chunks as Gemini streams the response."""
    prompt = _build_prompt(question, retrieved_chunks)
    try:
        client = _get_client()
        for chunk in client.models.generate_content_stream(model=_MODEL, contents=prompt):
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text
    except Exception:
        yield _fallback_answer(question, retrieved_chunks)


if __name__ == "__main__":
    chunks = [
        ("Mathématiques Avancées : Mardi 9 juin 2026, 09h00-11h00, Salle A101", 0.9, "calendrier.pdf"),
        ("Algorithmique : Jeudi 11 juin 2026, 14h00-16h00, Salle B203", 0.7, "calendrier.pdf"),
        ("Règlement : carte étudiante obligatoire, arrivée 15 min avant.", 0.5, "calendrier.pdf"),
    ]

    print("Q : quand l'exam de math ?")
    print("R :", generate_answer("quand l'exam de math ?", chunks))
    print()
    print("Q : quand l'exam de chimie ?")
    print("R :", generate_answer("quand l'exam de chimie ?", chunks))
