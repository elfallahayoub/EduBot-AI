import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MAX_FILES_PER_SESSION, SESSION_MAX_AGE_HOURS, SUPPORTED_EXTENSIONS, TEMP_SESSIONS_DIR
from module3_rag.document_parser import parse_document
from module3_rag.text_chunker import chunk_text
from module3_rag.vector_store import VectorStore
from module2_distilbert.embeddings import get_shared_model, vectorize_text


def _session_dir(session_id: str) -> Path:
    return Path(TEMP_SESSIONS_DIR) / session_id

def _index_dir(session_id: str) -> Path:
    return _session_dir(session_id) / "vector_index"

def _file_list_path(session_id: str) -> Path:
    return _session_dir(session_id) / "file_list.txt"

def _active_file_count(session_id: str) -> int:
    path = _file_list_path(session_id)
    if not path.exists():
        return 0
    return len([l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()])

def _touch_activity(session_id: str) -> None:
    (_session_dir(session_id) / "last_activity.txt").write_text(str(time.time()), encoding="utf-8")


def create_session() -> str:
    session_id = str(uuid.uuid4())
    sdir = _session_dir(session_id)
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "created_at.txt").write_text(str(time.time()), encoding="utf-8")
    _touch_activity(session_id)
    return session_id


def add_file_to_session(session_id: str, file_path: str, display_name: Optional[str] = None) -> dict:
    sdir = _session_dir(session_id)
    if not sdir.exists():
        raise FileNotFoundError(f"Session '{session_id}' introuvable.")

    path = Path(file_path)
    ext  = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Format '{ext}' non supporté. Formats acceptés : {SUPPORTED_EXTENSIONS}")

    source_name = display_name or path.name

    if source_name in list_session_files(session_id):
        return {"session_id": session_id, "file": source_name, "chunks": 0, "status": "already_indexed"}

    if _active_file_count(session_id) >= MAX_FILES_PER_SESSION:
        raise ValueError(f"Limite de {MAX_FILES_PER_SESSION} fichiers par session atteinte.")

    text   = parse_document(file_path)
    path.unlink(missing_ok=True)
    chunks = chunk_text(text)

    tokenizer, model = get_shared_model()
    embeddings = np.array([vectorize_text(chunk, tokenizer, model) for chunk in chunks])

    idir  = _index_dir(session_id)
    store = VectorStore.load_from_disk(str(idir)) if idir.exists() else VectorStore()
    store.add_chunks(chunks, embeddings, source=source_name)
    store.save_to_disk(str(idir))

    with open(_file_list_path(session_id), "a", encoding="utf-8") as f:
        f.write(source_name + "\n")

    _touch_activity(session_id)
    return {"session_id": session_id, "file": source_name, "chunks": len(chunks)}


def get_session_store(session_id: str) -> Optional[VectorStore]:
    idir = _index_dir(session_id)
    if not idir.exists():
        return None
    return VectorStore.load_from_disk(str(idir))


def list_session_files(session_id: str) -> list:
    path = _file_list_path(session_id)
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def cleanup_session(session_id: str) -> None:
    sdir = _session_dir(session_id)
    if sdir.exists():
        shutil.rmtree(sdir)


def cleanup_expired_sessions(max_age_hours: float = SESSION_MAX_AGE_HOURS) -> int:
    sessions_root = Path(TEMP_SESSIONS_DIR)
    if not sessions_root.exists():
        return 0

    max_age_seconds = max_age_hours * 3600
    now     = time.time()
    removed = 0

    for sdir in sessions_root.iterdir():
        if not sdir.is_dir():
            continue
        activity_file = sdir / "last_activity.txt"
        created_file  = sdir / "created_at.txt"
        ref = activity_file if activity_file.exists() else created_file
        age = (now - float(ref.read_text(encoding="utf-8").strip())) if ref.exists() else (now - sdir.stat().st_mtime)
        if age > max_age_seconds:
            shutil.rmtree(sdir)
            removed += 1

    return removed


if __name__ == "__main__":
    import tempfile
    import os

    sid = create_session()
    content = (
        "Introduction à Python\n\n"
        "Python est un langage de programmation interprété, orienté objet et de haut niveau. "
        "Il est très populaire en science des données, en intelligence artificielle et en développement web."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name

    result = add_file_to_session(sid, tmp_path)
    assert result["chunks"] > 0
    assert not os.path.exists(tmp_path)
    assert list_session_files(sid) == [result["file"]]

    try:
        for i in range(MAX_FILES_PER_SESSION):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(f"Fichier {i+2}. " * 10)
                add_file_to_session(sid, f.name)
        print("FAIL: limit not enforced")
    except ValueError:
        print("session_manager.py: OK")

    cleanup_session(sid)
