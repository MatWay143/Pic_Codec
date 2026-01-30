from PIL import Image, ExifTags
import numpy as np
import os
from encode import enc_func
from decode import dec_func

def analyze_image(image_path):
    if not os.path.exists(image_path):
        print("No file exists with this address.")
        return

    img = Image.open(image_path)

    print("====== Image General Info ======")
    print(f"File path        : {image_path}")
    print(f"File format      : {img.format}")
    print(f"File size (KB)   : {os.path.getsize(image_path) / 1024:.2f}")

    print("\n====== Image Geometry ======")
    print(f"Width            : {img.width}")
    print(f"Height           : {img.height}")
    print(f"Resolution       : {img.size}")

    print("\n====== Pixel & Color Info ======")
    print(f"Color mode       : {img.mode}")

    if img.mode == "RGB":
        channels = ["Red", "Green", "Blue"]
    elif img.mode == "RGBA":
        channels = ["Red", "Green", "Blue", "Alpha"]
    elif img.mode == "L":
        channels = ["Grayscale"]
    elif img.mode == "CMYK":
        channels = ["Cyan", "Magenta", "Yellow", "Black"]
    else:
        channels = list(img.getbands())

    print(f"Number of channels: {len(channels)}")
    print(f"Channel types    : {channels}")

    img_np = np.array(img)

    print("\n====== Numerical Info ======")
    print(f"Numpy shape      : {img_np.shape}")
    print(f"Data type        : {img_np.dtype}")
    print(f"Bit depth        : {img_np.dtype.itemsize * 8} bits")

    print("\n====== Pixel Statistics ======")
    print(f"Min pixel value  : {img_np.min()}")
    print(f"Max pixel value  : {img_np.max()}")
    print(f"Mean pixel value : {img_np.mean():.2f}")

    print("\n====== EXIF Metadata ======")
    exif_data = img._getexif()
    if exif_data:
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            print(f"{tag:25}: {value}")
    else:
        print("No EXIF metadata found.")

    print("\n✅ Analysis completed.")

def analyze_image_main(image_path):
    img = Image.open(image_path)
    img_np = np.array(img)
    main_properties["width"] = img.width
    main_properties["height"] = img.height
    if img.mode == "RGB":
        channels = ["Red", "Green", "Blue"]
    elif img.mode == "RGBA":
        channels = ["Red", "Green", "Blue", "Alpha"]
    elif img.mode == "L":
        channels = ["Grayscale"]
    elif img.mode == "CMYK":
        channels = ["Cyan", "Magenta", "Yellow", "Black"]
    else:
        channels = list(img.getbands())
    main_properties["num_of_channels"] = len(channels)
    main_properties["type_of_channels"] = channels
    main_properties["depth_per_channel"] = img_np.dtype.itemsize * 8

if __name__ == "__main__":
    cycle = True
    main_properties = {"width": "", "height": "", "num_of_channels": "", "type_of_channels": "", "depth_per_channel": ""}
    while cycle:
        image_path = input("Specify the address/ URL of the image:\n").strip()
        operation = input("Choose an operation:\n1)Encode 2)Decode 3)Details 4)Exit\n").strip()
        if operation == "1":
            analyze_image_main(image_path)
            enc_func(image_path, main_properties)
        elif operation == "2":
            dec_func(image_path)
        elif operation == "3":
            analyze_image(image_path)
        elif operation == "4":
            print("Exiting the program.")
            cycle = False
        else:
            print("Invalid option.\n")