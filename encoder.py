import numpy as np
from PIL import Image
import os
from functions import funcs

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

def predictor(image_path: str):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.uint8)

    best_entropy_name = None
    best_entropy_val = float("inf")
    best_entropy_output = None

    best_bpp_name = None
    best_bpp_val = float("inf")
    best_bpp_output = None

    for name, f in funcs.items():
        pred = apply_predictor(arr, f)
        e = entropy(pred)
        bpp = e / 8.0

        if e < best_entropy_val:
            best_entropy_val = e
            best_entropy_output = pred.copy()
            best_entropy_name = name

        if bpp < best_bpp_val:
            best_bpp_val = bpp
            best_bpp_output = pred.copy()
            best_bpp_name = name

    np.savez_compressed(f"residual_entropy_{best_entropy_name}.npz", best_entropy_output.astype(np.int16))
    np.savez_compressed(f"residual_bpp_{best_bpp_name}.npz", best_bpp_output.astype(np.int16))

    entropy_preview = _safe_preview(best_entropy_output)
    bpp_preview = _safe_preview(best_bpp_output)
    Image.fromarray(entropy_preview).save(f"preview_entropy_{best_entropy_name}.png")
    Image.fromarray(bpp_preview).save(f"preview_bpp_{best_bpp_name}.png")

    return {
        "best_entropy": (best_entropy_name, best_entropy_val, f"residual_entropy_{best_entropy_name}.npz"),
        "best_bpp": (best_bpp_name, best_bpp_val, f"residual_bpp_{best_bpp_name}.npz")
    }
