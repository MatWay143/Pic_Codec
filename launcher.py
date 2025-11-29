from PIL import Image, UnidentifiedImageError
import numpy as np
import os
import math
from encoder import predictor
from decoder import reconstruct

batch_dir = "/home/matt/Documents/HomeWorks/AMS/HW2/Images"
batch_files = [
    "Baboon.tif", "Cells.png", "CLIC_2025_2.png", "Kodak_23.png", "MRI_1.tif", "Peppers.bmp",
    "Bridge.tif", "CLIC_2025_1.png", "Kodak_01.png", "Livingroom.tif", "MRI_2.tif", "Retina.tif"
]

path = input("Locate the picture or residual (URL/Address) or type 'batch':\n").strip()
if path.lower() == "batch":
    for fname in batch_files:
        p = os.path.join(batch_dir, fname)
        if not os.path.isfile(p):
            print("Missing:", p)
            continue
        try:
            print("Processing:", fname)
            predictor(p)
            print("Done:", fname)
        except Exception as e:
            print("Error processing", fname, ":", e)
    raise SystemExit

if not os.path.exists(path):
    print("File not found:", path)
    raise SystemExit

ext = os.path.splitext(path)[1].lower()
is_image = ext in (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
is_npz = ext == ".npz"

image = None
if is_image:
    try:
        image = Image.open(path)
    except UnidentifiedImageError:
        print("Cannot identify image file:", path)
        raise SystemExit

while True:
    method = input("Specify the operation:\n1. <E>ncode\n2. <D>ecode\n3. <P>roperties\n").strip()
    if method.lower() in ('e', '1'):
        operation = 1
        break
    elif method.lower() in ('d', '2'):
        operation = 2
        break
    elif method.lower() in ('p', '3'):
        operation = 3
        break

if operation == 1:
    if not is_image:
        print("Encode requires an image file.")
        raise SystemExit
    try:
        res = predictor(path)
        print("Predictor result:", res)
    except Exception as e:
        print("Error during predictor:", e)

elif operation == 2:
    if not is_npz:
        print("Decode requires a .npz residual file.")
        raise SystemExit
    try:
        out = reconstruct(path)
        print("Reconstructed saved to:", out)
    except Exception as e:
        print("Error during reconstruct:", e)

elif operation == 3:
    if not is_image:
        print("Properties require an image file.")
        raise SystemExit

    file_w, file_h = image.size
    file_m = image.mode
    file_f = image.format
    file_c = len(file_m)
    file_d = file_w * file_h
    file_s = os.path.getsize(path) * 8

    arr = np.array(image.convert("L"))
    hist, _ = np.histogram(arr, bins=256, range=(0,256))
    probs = hist / hist.sum()
    entropy_val = float(-np.sum([p * math.log2(p) for p in probs if p > 0]))
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))

    if file_m in ["L", "P"]:
        bit_depth = 8
    elif file_m in ["RGB", "RGBA", "CMYK"]:
        bit_depth = 8
    elif file_m.startswith("I;16"):
        bit_depth = 16
    else:
        bit_depth = 8

    file_bpp = file_s / (file_d * file_c) if file_d > 0 else 0
    file_det = {
        "Width": file_w,
        "Height": file_h,
        "Mode": file_m,
        "Format": file_f,
        "Channels": file_c,
        "Pixels": file_d,
        "Size (bits)": file_s,
        "Entropy": entropy_val,
        "Bit Depth": bit_depth,
        "Bits Per Pixel": file_bpp
    }

    print("\nFile properties:")
    for k, v in file_det.items():
        print(f"{k:<15}: {v}")
    print()

    check_1 = input("Display the picture? 1. <Y>es  2. <N>o\n").strip()
    if check_1.lower() in ('y', '1'):
        try:
            image.show()
        except Exception as e:
            print("Cannot show image:", e)

    check_2 = input("Display pixels value matrix (10x10 sample)? 1. <Y>es  2. <N>o\n").strip()
    if check_2.lower() in ('y', '1'):
        sample_h = min(10, image.height)
        sample_w = min(10, image.width)
        channels = list(image.mode)

        print(f"{'x':<5}|{'y':<5}|", end="")
        for ch in channels:
            print(f"{ch:<5}|", end="")
        print()
        print("=" * ((len(channels) + 2) * 6))

        for y in range(sample_h):
            for x in range(sample_w):
                pixel = image.getpixel((x, y))
                print(f"{x+1:<5}|{y+1:<5}|", end="")
                if isinstance(pixel, tuple):
                    for val in pixel:
                        print(f"{val:<5}|", end="")
                else:
                    print(f"{pixel:<5}|", end="")
                print()
