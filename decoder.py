import os
import re
import numpy as np
from PIL import Image
from functions import funcs

def _to_int32_array(maybe_obj):
    arr = np.asarray(maybe_obj)
    if arr.dtype == object:
        if arr.size == 1 and isinstance(arr.flat[0], (np.ndarray, list, tuple)):
            arr = np.asarray(arr.flat[0])
        else:
            try:
                arr = np.asarray([int(x) for x in arr.flat]).reshape(arr.shape)
            except Exception:
                raise ValueError("Residual array has object dtype and cannot be converted automatically.")
    return arr.astype(np.int32)

def reconstruct(residual_path: str) -> str:
    if not os.path.isfile(residual_path):
        raise FileNotFoundError(f"File not found: {residual_path}")
    data = np.load(residual_path, allow_pickle=True)
    arr_keys = [k for k in data.files]
    if not arr_keys:
        raise ValueError("NPZ file contains no arrays")
    key = "arr_0" if "arr_0" in arr_keys else arr_keys[0]
    raw = data[key]
    residual = _to_int32_array(raw)
    match = re.search(r'_([A-Za-z0-9_-]+)\.npz$', os.path.basename(residual_path))
    if not match:
        raise ValueError("Cannot detect predictor name from filename. Expected pattern _<predictor>.npz")
    predictor_name = match.group(1)
    f = funcs.get(predictor_name)
    if f is None:
        raise KeyError(f"Predictor '{predictor_name}' not found in funcs")
    if residual.ndim != 2:
        raise ValueError("Residual array must be 2D (height x width)")
    h, w = residual.shape
    out = np.zeros((h, w), dtype=np.int32)
    for i in range(h):
        for j in range(w):
            a = int(out[i, j-1]) if j > 0 else 0
            b = int(out[i-1, j]) if i > 0 else 0
            c = int(out[i-1, j-1]) if i > 0 and j > 0 else 0
            p = int(f(a, b, c))
            out[i, j] = np.clip(int(residual[i, j]) + p, 0, 255)
    out_u8 = out.astype(np.uint8)
    save_path = f"decoded_{predictor_name}.png"
    Image.fromarray(out_u8, mode="L").save(save_path)
    return save_path
