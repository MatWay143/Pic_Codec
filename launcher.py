from PIL import Image
import numpy as np
import os
from decoders.dec_manager import decode
from encoders.enc_manager import encode

path = input("Locate the picture (URL/Address):\n")
image = Image.open(path)

while True:
    method = input("Specify the operation:\n1. <E>ncode\n2. <D>ecode\n3. <P>roperties\n")
    if method.lower() == 'e' or method == 1:
        operation = 1
        break
    elif method.lower() == 'd' or method == 2:
        operation = 2
        break
    elif method.lower() == 'p' or method == 3:
        operation = 3
        break

if operation == 1:
    encode(str)
elif operation == 2:
    decode(str)
elif operation == 3:
    file_show = Image.open(path)
    file_w, file_h = image.size
    file_m = image.mode
    file_f = image.format
    file_c = len(file_m)
    file_d = file_w * file_h
    file_s = os.path.getsize(path)*8
    file_e = image.entropy
    file_bpp = file_s / file_d
    file = {
        "Width": file_w,
        "Height": file_h,
        "Mode": file_m,
        "Format": file_f,
        "Channels": file_c,
        "Pixels": file_d,
        "Size": file_s,
        "Entropy": file_e,
        "Bits Per Pixel": file_bpp
    }
    print(file, "\n")
    check_1 = input("Display the picture?\n1. <Y>es\n2. <N>o\n")
    if check_1.lower() == 'y' or check_1 == 1:
        file_show.show()
    
check_2 = input("Display pixels value matrix?\n1. <Y>es\n2. <N>o\n")
if check_2.lower() == 'y' or check_1 == 1:
    channels = list(file_m)   # مثلا ['R','G','B']

    # چاپ هدر
    print(f"{'x':<9}|{'y':<9}|", end="")
    for ch in channels:
        print(f"{ch:<9}|", end="")
    print()  # رفتن به خط بعد

    # چاپ خط جداکننده
    print("=" * ((len(channels) + 2) * 10))

    # چاپ داده‌های پیکسل‌ها
    for y in range(file_h):
        for x in range(file_w):
            pixel = file_show.getpixel((x, y))
            print(f"{x+1:<9}|{y+1:<9}|", end="")
            # اگر RGB یا RGBA باشه → tuple
            if isinstance(pixel, tuple):
                for val in pixel:
                    print(f"{val:<9}|", end="")
            else:
                print(f"{pixel:<9}|", end="")
            print()  # خط بعد برای هر پیکسل
