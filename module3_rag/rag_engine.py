import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from module2_distilbert.embeddings import get_shared_model, vectorize_text
from module3_rag.session_manager import get_session_store, list_session_files
from module3_rag.answer_generator import generate_answer

_SEMANTIC_W  = 0.4
_KEYWORD_W   = 0.6
_MIN_SCORE   = 0.50

# Strips French elisions (l', d', j'...) so "l'examen" becomes "examen"
_ELISION_RE = re.compile(r"\b\w'", re.UNICODE)


def _normalize_query(query: str) -> str:
    return _ELISION_RE.sub("", query.lower())


def _keyword_score(query: str, chunk: str) -> float:
    words = [w for w in _normalize_query(query).split()
             if len(w) > 3 or (w.isdigit() and 1 <= len(w) <= 3)]
    if not words:
        return 0.0
    chunk_lower = chunk.lower()
    return sum(1.0 for w in words if w in chunk_lower) / len(words)


def answer_question(question: str, session_id: Optional[str] = None, top_k: int = 3) -> dict:
    if not session_id:
        return {
            "answer": (
                "Pour répondre à votre question, j'ai besoin de documents. "
                "Veuillez uploader un fichier (PDF, Word, TXT...) "
                "contenant les informations relatives à votre université."
            ),
            "source": None,
            "confidence": 0.0,
        }

    if not list_session_files(session_id):
        return {
            "answer": (
                "Vous n'avez encore uploadé aucun document. "
                "Veuillez joindre un fichier (PDF, DOCX, TXT, PPTX...) "
                "et je répondrai à vos questions à partir de son contenu."
            ),
            "source": None,
            "confidence": 0.0,
        }

    tokenizer, model = get_shared_model()
    query_vector     = vectorize_text(question, tokenizer, model)

    session_store = get_session_store(session_id)
    if session_store is None or len(session_store) == 0:
        return {
            "answer": "Une erreur s'est produite avec vos fichiers. Veuillez les uploader à nouveau.",
            "source": None,
            "confidence": 0.0,
        }

    candidates = session_store.search(query_vector, top_k=max(top_k * 3, len(session_store)))
    if not candidates:
        return {
            "answer": "Je n'ai pas trouvé de réponse dans vos documents. Essayez de reformuler votre question.",
            "source": None,
            "confidence": 0.0,
        }

    ranked = sorted(
        candidates,
        key=lambda r: _SEMANTIC_W * r[1] + _KEYWORD_W * _keyword_score(question, r[0]),
        reverse=True,
    )

    top_chunks = ranked[:top_k]
    best_chunk, best_sem, best_source = top_chunks[0]
    best_score = _SEMANTIC_W * best_sem + _KEYWORD_W * _keyword_score(question, best_chunk)

    if best_score < _MIN_SCORE:
        return {
            "answer": (
                "Je n'ai pas trouvé cette information dans vos documents. "
                "Essayez de reformuler votre question ou vérifiez que le document "
                "contenant cette information a bien été uploadé."
            ),
            "source": None,
            "confidence": round(best_score, 4),
        }

    return {
        "answer":     generate_answer(question, top_chunks),
        "source":     best_source,
        "confidence": round(best_score, 4),
    }


if __name__ == "__main__":
    import tempfile
    from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session

    session_id = create_session()
    content = (
        "Calendrier des examens\n"
        "Mathematiques : Mardi 9 juin 2026, 09h00, Salle A101\n"
        "Algorithmique : Jeudi 11 juin 2026, 14h00, Salle B203\n"
        "Bases de Donnees : Vendredi 12 juin 2026, 09h00, Labo Info\n"
        "Reglement : carte etudiante obligatoire. Arrivee 15 min avant."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp = f.name

    add_file_to_session(session_id, tmp)

    for q in ["quand l'exam de math ?", "quelle salle pour bases de donnees ?", "quand est l'examen de chimie ?"]:
        r = answer_question(q, session_id=session_id)
        print(f"Q: {q}")
        print(f"R: {r['answer'][:120]}")
        print(f"   conf={r['confidence']}  src={r['source']}\n")

    cleanup_session(session_id)
