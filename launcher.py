from PIL import Image
import numpy as np
import os
import math
from encoder import encoder_manager
from decoder import decoder_manager

path = input("Locate the picture (URL/Address):\n")
image = Image.open(path)
while True:
    method = input("Specify the operation:\n1. <E>ncode\n2. <D>ecode\n3. <P>roperties\n")
    if method.lower() == 'e' or method == '1':
        operation = 1
        break
    elif method.lower() == 'd' or method == '2':
        operation = 2
        break
    elif method.lower() == 'p' or method == '3':
        operation = 3
        break

file_show = Image.open(path)
file_w, file_h = image.size
file_m = image.mode
file_f = image.format
file_c = len(file_m)
file_d = file_w * file_h
file_s = os.path.getsize(path)*8

arr = np.array(image.convert("L"))
hist, _ = np.histogram(arr, bins=256, range=(0,256))
probs = hist / hist.sum()
entropy = float(-np.sum([p * math.log2(p) for p in probs if p > 0]))

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

file_bpp = file_s / file_d
file_det = {
    "Width": file_w,
    "Height": file_h,
    "Mode": file_m,
    "Format": file_f,
    "Channels": file_c,
    "Pixels": file_d,
    "Size (bits)": file_s,
    "Entropy": entropy,
    "Bit Depth": bit_depth,
    "Bits Per Pixel": file_bpp
}

if operation == 1:
    arr = np.array(image.convert("L"))
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    encoder_manager(file_det, mean_val, std_val, image)
elif operation == 2:
    print(mean_val, std_val)
elif operation == 3:
    print(file_det, "\n")

    check_1 = input("Display the picture?\n1. <Y>es\n2. <N>o\n")
    if check_1.lower() == 'y' or check_1 == '1':
        file_show.show()

    check_2 = input("Display pixels value matrix?\n1. <Y>es\n2. <N>o\n")
    if check_2.lower() == 'y' or check_2 == '1':
        channels = list(image.mode)

    print(f"{'x':<9}|{'y':<9}|", end="")
    for ch in channels:
        print(f"{ch:<9}|", end="")
    print()
    print("=" * ((len(channels) + 2) * 10))

    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            print(f"{x+1:<9}|{y+1:<9}|", end="")
            if isinstance(pixel, tuple):
                for val in pixel:
                    print(f"{val:<9}|", end="")
            else:
                print(f"{pixel:<9}|", end="")
            print()
