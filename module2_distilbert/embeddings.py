import sys
import struct
import json
import gc
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel, AutoConfig
import transformers

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DISTILBERT_MODEL_NAME

# cmarkea/distilcamembert-base is a masked-LM checkpoint; MISSING/UNEXPECTED key warnings are expected
transformers.logging.set_verbosity_error()


def _find_safetensors_in_hf_cache(model_name: str) -> Optional[str]:
    try:
        import huggingface_hub
        cache_root = Path(huggingface_hub.constants.HF_HUB_CACHE)
        folder = "models--" + model_name.replace("/", "--")
        snapshots_dir = cache_root / folder / "snapshots"
        if not snapshots_dir.exists():
            return None
        for snapshot in snapshots_dir.iterdir():
            candidate = snapshot / "model.safetensors"
            if candidate.exists():
                return str(candidate)
    except Exception:
        pass
    return None


def _load_weights_streaming(safetensors_path: str, model) -> None:
    # Reads one tensor at a time to avoid Windows OSError 1455 (paging file too small for mmap).
    # Peak RAM = model_size (~270MB) + largest tensor (~100MB) instead of model + full file (~540MB).
    _DTYPE_TO_NUMPY = {
        "F32": np.float32, "F16": np.float16,
        "I64": np.int64,   "I32": np.int32, "I16": np.int16,
        "I8":  np.int8,    "U8":  np.uint8,
    }
    _DTYPE_TO_TORCH = {
        "F64": torch.float64, "F32": torch.float32, "F16": torch.float16,
        "BF16": torch.bfloat16,
        "I64": torch.int64,   "I32": torch.int32,  "I16": torch.int16,
        "I8":  torch.int8,    "U8":  torch.uint8,  "BOOL": torch.bool,
    }

    params  = {n: p for n, p in model.named_parameters()}
    buffers = {n: b for n, b in model.named_buffers()}

    with open(safetensors_path, "rb") as f:
        header_len = struct.unpack("<Q", f.read(8))[0]
        header     = json.loads(f.read(header_len).decode("utf-8"))
        data_start = 8 + header_len

        for name, info in header.items():
            if name == "__metadata__":
                continue

            dtype_str    = info["dtype"]
            shape        = info["shape"]
            start, end   = info["data_offsets"]

            f.seek(data_start + start)
            raw = f.read(end - start)

            np_dtype = _DTYPE_TO_NUMPY.get(dtype_str)
            if np_dtype is not None:
                src = torch.from_numpy(np.frombuffer(raw, dtype=np_dtype).reshape(shape))
            else:
                src = torch.frombuffer(bytearray(raw), dtype=_DTYPE_TO_TORCH[dtype_str]).reshape(shape)

            if name in params:
                params[name].data.copy_(src)
            elif name in buffers:
                buffers[name].copy_(src)

            del raw, src

    gc.collect()


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(DISTILBERT_MODEL_NAME)

    try:
        model = AutoModel.from_pretrained(DISTILBERT_MODEL_NAME, low_cpu_mem_usage=True)
    except OSError as exc:
        if "1455" not in str(exc) and "pagination" not in str(exc).lower():
            raise

        print("  [warning] mmap failed (paging file too small), switching to streaming loader...")
        gc.collect()

        weights_path = _find_safetensors_in_hf_cache(DISTILBERT_MODEL_NAME)
        if weights_path is None:
            raise RuntimeError(
                "Weights not found in HuggingFace cache. "
                "Check your internet connection or re-download the model."
            ) from exc

        config = AutoConfig.from_pretrained(DISTILBERT_MODEL_NAME)
        model  = AutoModel.from_config(config)
        _load_weights_streaming(weights_path, model)
        gc.collect()

    model.eval()
    return tokenizer, model


def vectorize_text(text: str, tokenizer, model) -> np.ndarray:
    # Mean pooling over all token hidden states — more discriminative than CLS
    # for models not fine-tuned on semantic similarity tasks.
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)

    token_embeddings = outputs.last_hidden_state
    attention_mask   = inputs["attention_mask"]
    mask_expanded    = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

    sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
    sum_mask       = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
    mean_pooled    = (sum_embeddings / sum_mask).squeeze()

    return mean_pooled.numpy().astype(np.float32)


def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vector1, vector2) / (norm1 * norm2))


_shared_tokenizer = None
_shared_model     = None


def get_shared_model():
    global _shared_tokenizer, _shared_model
    if _shared_tokenizer is None:
        _shared_tokenizer, _shared_model = load_model()
    return _shared_tokenizer, _shared_model


if __name__ == "__main__":
    print("Chargement du modèle DistilCamemBERT...")
    tok, mdl = load_model()
    print(f"Modèle chargé : {DISTILBERT_MODEL_NAME}\n")

    phrase1 = "Quand est l'examen de mathématiques ?"
    phrase2 = "L'examen de maths se déroule le 12 janvier 2026 à 9h00."
    phrase3 = "Je voudrais m'inscrire à l'université."

    v1 = vectorize_text(phrase1, tok, mdl)
    v2 = vectorize_text(phrase2, tok, mdl)
    v3 = vectorize_text(phrase3, tok, mdl)

    print(f"Dimension du vecteur : {v1.shape}")
    print(f"Similarité (question / réponse pertinente) : {cosine_similarity(v1, v2):.4f}")
    print(f"Similarité (question / hors-sujet)         : {cosine_similarity(v1, v3):.4f}")
    print("\nTest embeddings.py : OK")
