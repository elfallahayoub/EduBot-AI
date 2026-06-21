import os
from pathlib import Path

# Must be set before importing tensorflow or transformers
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL",  "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("CUDA_VISIBLE_DEVICES",  "")
os.environ.setdefault("OMP_NUM_THREADS",        "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

BASE_DIR = Path(__file__).parent

MODULE1_DIR = BASE_DIR / "module1_lstm"
MODULE2_DIR = BASE_DIR / "module2_distilbert"
MODULE3_DIR = BASE_DIR / "module3_rag"

STORAGE_DIR       = MODULE3_DIR / "storage"
TEMP_SESSIONS_DIR = STORAGE_DIR / "temp_sessions"

DISTILBERT_MODEL_NAME = "cmarkea/distilcamembert-base"
CHUNK_SIZE            = 60
LINES_PER_CHUNK       = 3
LINES_OVERLAP         = 1
MAX_FILES_PER_SESSION = 4
SESSION_MAX_AGE_HOURS = 24

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".pptx", ".xlsx", ".csv"]
