import os
import numpy as np
from PIL import Image
from math import log2, ceil

def rgb_to_ycbcr(x):
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    y = 0.299*r + 0.587*g + 0.114*b
    cb = -0.168736*r - 0.331264*g + 0.5*b
    cr = 0.5*r - 0.418688*g - 0.081312*b
    return np.clip(np.stack([y, cb, cr], axis=-1), -128, 127).astype(np.int8)

def ycbcr_to_rgb(x):
    y, cb, cr = x[...,0], x[...,1], x[...,2]
    r = y + 1.402*cr
    g = y - 0.344136*cb - 0.714136*cr
    b = y + 1.772*cb
    return np.clip(np.stack([r,g,b], axis=-1), 0, 255).astype(np.uint8)

def med(a, b, c):
    return np.where(c >= np.maximum(a, b), np.minimum(a, b),
           np.where(c <= np.minimum(a, b), np.maximum(a, b), a + b - c))

def spatial_predict(img):
    h, w, ch = img.shape
    p = np.zeros_like(img)
    a = img[:, :-1]
    b = img[:-1, :]
    c = img[:-1, :-1]
    p[1:, 1:] = med(a[1:], b[:, 1:], c)
    return p

def error_map(e):
    return np.where(e >= 0, 2*e, -2*e-1)

def optimal_k(x):
    mean = np.mean(x) + 1e-9
    return max(0, int(ceil(log2(mean))))

def golomb_rice_bits(x, k):
    q = x >> k
    return np.sum(q + 1 + k)

def encode_entropy(x):
    x = error_map(x.flatten())
    k = optimal_k(x)
    return golomb_rice_bits(x, k), k

def block_match(L, R, bs=8, sr=6):
    h, w, _ = L.shape
    mv = np.zeros((h, w, 2), dtype=np.int16)
    for y in range(0, h-bs, bs):
        for x in range(0, w-bs, bs):
            ref = R[y:y+bs, x:x+bs]
            best = 1e18
            dyx = (0, 0)
            for dy in range(-sr, sr+1):
                for dx in range(-sr, sr+1):
                    yy, xx = y+dy, x+dx
                    if yy < 0 or xx < 0 or yy+bs >= h or xx+bs >= w:
                        continue
                    cand = L[yy:yy+bs, xx:xx+bs]
                    d = np.sum(np.abs(ref-cand))
                    if d < best:
                        best = d
                        dyx = (dy, dx)
            mv[y:y+bs, x:x+bs] = dyx
    return mv

def multicolor_stereo_encode(path_l, path_r, properties):
    L = np.array(Image.open(path_l))
    R = np.array(Image.open(path_r))
    properties["width"] = L.shape[1]
    properties["height"] = L.shape[0]
    properties["num_of_channels"] = 3
    properties["type_of_channels"] = "YCbCr"
    properties["depth_per_channel"] = 8

    L = rgb_to_ycbcr(L)
    R = rgb_to_ycbcr(R)

    P_L = spatial_predict(L)
    E_L = L - P_L

    bits_L = 0
    for c in range(3):
        b, _ = encode_entropy(E_L[..., c])
        bits_L += b

    MV = block_match(L, R)
    P_R = np.zeros_like(R)
    h, w, _ = R.shape
    for y in range(h):
        for x in range(w):
            dy, dx = MV[y, x]
            yy, xx = y+dy, x+dx
            if 0 <= yy < h and 0 <= xx < w:
                P_R[y, x] = L[yy, xx]

    E_inter = R - P_R
    P_R2 = spatial_predict(E_inter)
    E_R = E_inter - P_R2

    bits_R = 0
    for c in range(3):
        b, _ = encode_entropy(E_R[..., c])
        bits_R += b

    base = os.path.dirname(path_l)
    np.savez_compressed(os.path.join(base, "left_encoded.npz"), E_L)
    np.savez_compressed(os.path.join(base, "right_encoded.npz"), E_R)

    L_recon = P_L + E_L
    R_recon = P_R + P_R2 + E_R

    L_rgb = ycbcr_to_rgb(L_recon)
    R_rgb = ycbcr_to_rgb(R_recon)

    Image.fromarray(L_rgb).save(os.path.join(base, "left_reconstructed.png"))
    Image.fromarray(R_rgb).save(os.path.join(base, "right_reconstructed.png"))

    bpp_L = bits_L / (properties["width"] * properties["height"])
    bpp_R = bits_R / (properties["width"] * properties["height"])

    return {
        "Left_BPP": bpp_L,
        "Right_BPP": bpp_R,
        "Total_BPP": bpp_L + bpp_R,
        "properties": properties
    }
