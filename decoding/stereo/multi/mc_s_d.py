import os
import numpy as np
from PIL import Image

def ycbcr_to_rgb(x):
    y, cb, cr = x[...,0], x[...,1], x[...,2]
    r = y + 1.402*cr
    g = y - 0.344136*cb - 0.714136*cr
    b = y + 1.772*cb
    return np.clip(np.stack([r,g,b], axis=-1), 0, 255).astype(np.uint8)

def spatial_predict(img):
    h, w, ch = img.shape
    p = np.zeros_like(img)
    a = img[:, :-1]
    b = img[:-1, :]
    c = img[:-1, :-1]
    p[1:, 1:] = np.where(c[1:] >= np.maximum(a[1:], b[:, 1:]), np.minimum(a[1:], b[:, 1:]),
                         np.where(c[1:] <= np.minimum(a[1:], b[:, 1:]), np.maximum(a[1:], b[:, 1:]),
                                  a[1:] + b[:, 1:] - c[1:]))
    return p

def multicolor_stereo_decode(path_l, path_r, properties):
    base = os.path.dirname(path_l)
    E_L = np.load(os.path.join(base, "left_encoded.npz"))['arr_0']
    E_R = np.load(os.path.join(base, "right_encoded.npz"))['arr_0']

    P_L = spatial_predict(E_L + 0)
    L_recon = P_L + E_L
    L_rgb = ycbcr_to_rgb(L_recon)

    P_R2 = spatial_predict(E_R + 0)
    R_recon = P_R2 + E_R
    R_rgb = ycbcr_to_rgb(R_recon)

    left_path = os.path.join(base, "left_decoded.png")
    right_path = os.path.join(base, "right_decoded.png")

    Image.fromarray(L_rgb).save(left_path)
    Image.fromarray(R_rgb).save(right_path)

    return {
        "Left_Decoded": left_path,
        "Right_Decoded": right_path,
        "properties": properties
    }
