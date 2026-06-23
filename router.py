import sys
import pickle
import warnings
from pathlib import Path
from typing import Optional

import numpy as np

# config must be imported before tensorflow to set env vars first
sys.path.insert(0, str(Path(__file__).parent))
from config import MODULE1_DIR

import tensorflow as tf
tf.get_logger().setLevel("ERROR")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from tensorflow.keras.preprocessing.sequence import pad_sequences
from module3_rag.rag_engine import answer_question, retrieve
from module3_rag.answer_generator import generate_answer_stream
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
        for p in (_MODEL_PATH, _TOK_PATH, _ENC_PATH):
            if not p.exists():
                raise FileNotFoundError(
                    f"Fichier LSTM manquant : {p}\n"
                    "Entraînez le modèle d'abord avec module1_lstm/train.py"
                )
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


def process_message(question: str, session_id: Optional[str] = None, stream: bool = False) -> dict:
    intent = classify_intent(question)

    if intent in SIMPLE_INTENTS:
        return {
            "intent":     intent,
            "answer":     SIMPLE_INTENTS[intent],
            "source":     None,
            "confidence": 1.0,
            "stream":     None,
        }

    if stream:
        retrieval = retrieve(question, session_id=session_id)
        if "error" in retrieval:
            return {
                "intent":     intent,
                "answer":     retrieval["error"],
                "source":     retrieval["source"],
                "confidence": retrieval["confidence"],
                "stream":     None,
            }
        return {
            "intent":     intent,
            "answer":     None,
            "source":     retrieval["source"],
            "confidence": retrieval["confidence"],
            "stream":     generate_answer_stream(question, retrieval["chunks"]),
        }

    result = answer_question(question, session_id=session_id)
    result["intent"] = intent
    result["stream"] = None
    return result


if __name__ == "__main__":
    import tempfile
    from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session

    cleanup_expired_sessions()

    for question in ["Bonjour !", "Au revoir, merci !"]:
        r = process_message(question)
        print(f"Q: {question}")
        print(f"R: {r['answer'][:100]}\n")

    session_id = create_session()
    content = (
        "Calendrier des examens\n"
        "Mathématiques : 9 juin 2026, 09h00, Salle A101\n"
        "Algorithmique : 11 juin 2026, 14h00, Salle B203\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name

    add_file_to_session(session_id, tmp_path)

    for q in ["Quand est l'examen de mathématiques ?", "Quelle salle pour algorithmique ?"]:
        r = process_message(q, session_id=session_id)
        print(f"Q: {q}")
        print(f"R: {r['answer'][:150]}")
        print(f"   conf={r['confidence']}  src={r['source']}\n")

    cleanup_session(session_id)
