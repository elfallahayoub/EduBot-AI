import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from module2_distilbert.embeddings import get_shared_model, vectorize_text
from module3_rag.session_manager import get_session_store, list_session_files


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

    results = session_store.search(query_vector, top_k=top_k)
    if not results:
        return {
            "answer": "Je n'ai pas trouvé de réponse dans vos documents. Essayez de reformuler votre question.",
            "source": None,
            "confidence": 0.0,
        }

    best_chunk, best_score, best_source = results[0]
    return {
        "answer":     best_chunk,
        "source":     best_source,
        "confidence": round(float(best_score), 4),
    }


if __name__ == "__main__":
    import tempfile
    from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session

    print("=" * 60)
    print("  Test du moteur RAG")
    print("=" * 60)

    print("\n[1] Question sans fichier uploadé\n")
    r = answer_question("Quand est l'examen de maths ?", session_id=None)
    print(f"  R : {r['answer']}")

    print("\n[2] Question avec fichier uploadé\n")
    session_id = create_session()

    upload_content = (
        "Calendrier des examens - Université Al Akhawayn\n\n"
        "Mathématiques Avancées : Lundi 8 juin 2026, 09h00 - 11h00, Salle A101\n"
        "Algorithmique         : Mercredi 10 juin 2026, 14h00 - 16h00, Salle B203\n"
        "Bases de Données      : Jeudi 11 juin 2026, 09h00 - 12h00, Labo Info\n"
        "Réseaux               : Vendredi 12 juin 2026, 09h00 - 11h00, Salle A205\n\n"
        "Règles : carte étudiante obligatoire, arrivée 15 min avant."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(upload_content)
        tmp_path = f.name

    print("  Traitement du fichier uploadé...")
    add_file_to_session(session_id, tmp_path)

    for q in ["Quand est l'examen de mathématiques ?", "Quelle salle pour l'examen de bases de données ?"]:
        print(f"\n  Q : {q}")
        r = answer_question(q, session_id=session_id)
        print(f"  R : {r['answer'][:200]}")
        print(f"  Source : {r['source']}  |  Confiance : {r['confidence']}")

    cleanup_session(session_id)
    print("\n\nTest rag_engine.py : OK")
