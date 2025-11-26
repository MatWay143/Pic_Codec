import os
import numpy as np
from functions import diffuse

def encoder_manager(file_det, mean_val, std_val, image):
    arr = np.array(image.convert("L"))
    image_path = getattr(image, "filename", None)
    if image_path and os.path.isfile(image_path):
        out_dir = os.path.dirname(image_path)
        base = os.path.splitext(os.path.basename(image_path))[0]
        out_path = os.path.join(out_dir, base + ".txt")
    else:
        out_path = os.path.join(os.getcwd(), "output.txt")

    with open(out_path, "w", encoding="utf-8") as out_file:
        for h in range(file_det["Height"]):
            for w in range(file_det["Width"]):
                x = int(arr[h, w])
                U = int(arr[h-1, w]) if h > 0 else 0
                L = int(arr[h, w-1]) if w > 0 else 0
                UL = int(arr[h-1, w-1]) if (h > 0 and w > 0) else 0

                pred = diffuse(U, L, UL, x, std_val)
                

                print(f"Row={h}, Col={w}, x={x}, U={U}, L={L}, UL={UL}, predicted={pred_val}")
