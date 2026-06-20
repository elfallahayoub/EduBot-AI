import sys
import pickle
import warnings
from pathlib import Path
from typing import Optional

import numpy as np

# config must be imported before tensorflow so env vars are set before TF initialises
sys.path.insert(0, str(Path(__file__).parent))
from config import MODULE1_DIR

import tensorflow as tf
tf.get_logger().setLevel("ERROR")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from tensorflow.keras.preprocessing.sequence import pad_sequences
from module3_rag.rag_engine import answer_question
from module3_rag.session_manager import cleanup_expired_sessions

_lstm_model    = None
_tokenizer     = None
_label_encoder = None

_MODEL_PATH = MODULE1_DIR / "best_model.keras"
_TOK_PATH   = MODULE1_DIR / "tokenizer.pkl"
_ENC_PATH   = MODULE1_DIR / "label_encoder.pkl"
_MAX_LEN    = 20


def _load_lstm() -> None:
    global _lstm_model, _tokenizer, _label_encoder
    if _lstm_model is None:
        _lstm_model = tf.keras.models.load_model(str(_MODEL_PATH))
        with open(_TOK_PATH, "rb") as f:
            _tokenizer = pickle.load(f)
        with open(_ENC_PATH, "rb") as f:
            _label_encoder = pickle.load(f)


SIMPLE_INTENTS: dict = {
    "SALUTATION": (
        "Bonjour ! Je suis EduBot, votre assistant académique personnel. "
        "Je peux répondre à vos questions à partir de vos propres documents. "
        "Uploadez un fichier (PDF, Word, TXT...) contenant les informations "
        "de votre université, et posez-moi vos questions !"
    ),
    "AU_REVOIR": (
        "Au revoir ! J'espère avoir pu vous aider. "
        "Bonne continuation dans vos études et n'hésitez pas à revenir "
        "si vous avez d'autres questions. Bon courage !"
    ),
}


def classify_intent(question: str) -> str:
    _load_lstm()
    seq    = _tokenizer.texts_to_sequences([question])
    padded = pad_sequences(seq, maxlen=_MAX_LEN, padding="post")
    probs  = _lstm_model.predict(padded, verbose=0)
    idx    = int(np.argmax(probs, axis=1)[0])
    return _label_encoder.inverse_transform([idx])[0]


def process_message(question: str, session_id: Optional[str] = None) -> dict:
    intent = classify_intent(question)

    if intent in SIMPLE_INTENTS:
        return {
            "intent":     intent,
            "answer":     SIMPLE_INTENTS[intent],
            "source":     None,
            "confidence": 1.0,
        }

    result = answer_question(question, session_id=session_id)
    result["intent"] = intent
    return result


if __name__ == "__main__":
    import tempfile
    from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session

    print("=" * 60)
    print("  Test complet EduBot")
    print("=" * 60)

    cleanup_expired_sessions()

    print("\n[1] Salutation / Au revoir\n")
    for question, desc in [
        ("Bonjour !",          "salutation"),
        ("Au revoir, merci !", "au revoir"),
    ]:
        print(f"  [{desc}]  Q : {question}")
        r = process_message(question)
        print(f"  R : {r['answer'][:120]}")
        print()

    print("\n[2] Question sans fichier uploadé\n")
    q = "Quand est l'examen de mathématiques ?"
    print(f"  Q : {q}")
    r = process_message(q, session_id=None)
    print(f"  Intention : {r['intent']}")
    print(f"  R : {r['answer']}")
    print()

    print("\n[3] Question avec fichier uploadé\n")
    session_id = create_session()
    upload_content = (
        "Calendrier des examens - Faculté des Sciences\n\n"
        "Mathématiques Avancées : Mardi 9 juin 2026, 09h00-11h00, Salle A101\n"
        "Algorithmique          : Jeudi 11 juin 2026, 14h00-16h00, Salle B203\n"
        "Bases de Données       : Vendredi 12 juin 2026, 09h00-12h00, Labo Informatique\n\n"
        "Rappel : la carte étudiante est obligatoire. Arrivée 15 minutes avant le début."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(upload_content)
        tmp_path = f.name

    print("  Traitement du fichier uploadé...")
    add_file_to_session(session_id, tmp_path)

    for q in [
        "Quand est l'examen de mathématiques ?",
        "Quelle salle pour l'examen de bases de données ?",
    ]:
        print(f"\n  Q : {q}")
        r = process_message(q, session_id=session_id)
        print(f"  Intention : {r['intent']}")
        print(f"  R : {r['answer'][:200]}")
        print(f"  Source : {r['source']}  |  Confiance : {r['confidence']}")

    cleanup_session(session_id)
    print("\n\nTest router.py : OK")
