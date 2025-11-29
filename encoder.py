import time
import numpy as np
from PIL import Image
import os
import functions as F

def _to_ints(*vals):
    return [int(np.int32(v)) for v in vals]

def _make_unified(funcs_dict, weights=None):
    if weights is None:
        weights = {k: 1.0 for k in funcs_dict.keys()}
    def unified(a, b, c):
        a, b, c = _to_ints(a, b, c)
        candidates = {}
        for name, fn in funcs_dict.items():
            try:
                p = int(fn(a, b, c))
            except Exception:
                p = 0
            candidates[name] = int(np.clip(p, 0, 255))
        total_w = sum(weights.get(k, 0.0) for k in candidates.keys())
        if total_w <= 0:
            return candidates.get("med", 0)
        weighted = sum(weights.get(k, 0.0) * v for k, v in candidates.items()) / total_w
        return int(np.clip(int(round(weighted)), 0, 255))
    return unified

def apply_predictor(img: np.ndarray, func) -> np.ndarray:
    h, w = img.shape
    out = np.zeros((h, w), dtype=np.int16)
    for i in range(h):
        for j in range(w):
            a = int(img[i, j-1]) if j > 0 else 0
            b = int(img[i-1, j]) if i > 0 else 0
            c = int(img[i-1, j-1]) if i > 0 and j > 0 else 0
            p = int(func(a, b, c))
            out[i, j] = np.int16(int(img[i, j]) - p)
    return out

def entropy(arr: np.ndarray) -> float:
    vals, counts = np.unique(arr.flatten(), return_counts=True)
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())

def _safe_preview(residual: np.ndarray) -> np.ndarray:
    r = residual.astype(np.int32) - int(residual.min())
    maxv = int(r.max()) if r.size > 0 else 0
    if maxv == 0:
        return np.zeros_like(r, dtype=np.uint8)
    scaled = (r * 255) // maxv
    return scaled.astype(np.uint8)

def predictor(image_path: str, weights: dict | None = None):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.uint8)
    funcs_dict = getattr(F, "funcs", {})
    unified_fn = getattr(F, "unified_predictor", None)
    if unified_fn is None:
        unified_fn = _make_unified(funcs_dict, weights)
    start = time.perf_counter()
    pred = apply_predictor(arr, unified_fn)
    run_time = time.perf_counter() - start
    e = entropy(pred)
    bpp = e / 8.0
    np.savez_compressed(f"residual_unified.npz", pred.astype(np.int16))
    preview = _safe_preview(pred)
    Image.fromarray(preview).save(f"preview_unified.png")
    return {
        "method": "unified",
        "entropy": float(round(e, 6)),
        "bpp": float(round(bpp, 6)),
        "residual": f"residual_unified.npz",
        "preview": f"preview_unified.png",
        "runtime_s": float(round(run_time, 6))
    }
