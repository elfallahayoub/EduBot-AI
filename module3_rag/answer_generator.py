import os
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

try:
    from google import genai
except ImportError:
    raise ImportError(
        "Package 'google-genai' requis. Installez-le avec : pip install google-genai"
    )

_client   = None
_ELISION  = re.compile(r"\b\w'", re.UNICODE)


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY introuvable. Vérifiez votre fichier .env.")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_answer(question: str, retrieved_chunks: List[Tuple[str, float, str]]) -> str:
    context_parts = []
    for i, (chunk, score, source) in enumerate(retrieved_chunks):
        context_parts.append(f"[Extrait {i+1} — {source}]\n{chunk}")
    context = "\n\n".join(context_parts)

    prompt = f"""Tu es EduBot, un assistant académique qui aide les étudiants universitaires.

Réponds à la question ci-dessous en te basant UNIQUEMENT sur les extraits du document fournis.

Règles strictes :
- Réponds en français, de façon concise et directe
- Si la réponse est une date, une heure ou une salle, cite-la exactement comme dans le document
- Si l'information demandée n'est PAS dans les extraits, réponds uniquement : "Je n'ai pas trouvé cette information dans vos documents."
- N'invente rien, ne complète pas avec tes propres connaissances
- Ne répète pas la question dans ta réponse

Extraits du document :
{context}

Question de l'étudiant : {question}

Réponse :"""

    try:
        client   = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        if not hasattr(response, "text") or not response.text:
            raise ValueError("Gemini a retourné une réponse vide.")

        return response.text.strip()

    except Exception as exc:
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
