import os
import numpy as np
from PIL import Image
from math import log2, ceil

def rgb_to_ycbcr(x):
    r, g, b = x[...,0], x[...,1], x[...,2]
    y  = 0.299*r + 0.587*g + 0.114*b
    cb = -0.168736*r - 0.331264*g + 0.5*b
    cr = 0.5*r - 0.418688*g - 0.081312*b
    return np.clip(np.stack([y, cb, cr], axis=-1), -128, 127).astype(np.int16)

def med(a, b, c):
    from numpy import maximum, minimum, where
    return where(c >= maximum(a, b), minimum(a, b),
           where(c <= minimum(a, b), maximum(a, b), a + b - c))

def spatial_predict(img):
    h, w, ch = img.shape
    p = np.zeros_like(img)
    a = img[:, :-1]
    b = img[:-1, :]
    c = img[:-1, :-1]
    p[1:,1:] = med(a[1:], b[:,1:], c)
    return p

def golomb_rice_encode(x, k):
    from numpy import right_shift
    bits = []
    for val in x.flatten():
        q = val >> k
        r = val & ((1 << k) - 1)
        bits.extend([1]*q + [0])  # unary code for q
        for i in reversed(range(k)):
            bits.append((r >> i) & 1)  # binary for r
    return bits, k

def bits_to_bytes(bits):
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i+j < len(bits):
                byte = (byte << 1) | bits[i+j]
            else:
                byte <<= 1
        b.append(byte)
    return b

def block_match(L, R, bs=8, sr=6):
    h, w, _ = L.shape
    mv = np.zeros((h, w, 2), dtype=np.int16)
    for y in range(0, h-bs+1, bs):
        for x in range(0, w-bs+1, bs):
            ref = R[y:y+bs, x:x+bs]
            best = 1e18
            dyx = (0,0)
            for dy in range(-sr, sr+1):
                for dx in range(-sr, sr+1):
                    yy, xx = y+dy, x+dx
                    if yy < 0 or xx < 0 or yy+bs > h or xx+bs > w:
                        continue
                    cand = L[yy:yy+bs, xx:xx+bs]
                    d = np.sum(np.abs(ref-cand))
                    if d < best:
                        best = d
                        dyx = (dy, dx)
            mv[y:y+bs, x:x+bs] = dyx
    return mv

def multicolor_stereo_encode(path_l, path_r, properties):
    base = os.path.dirname(path_l)
    L = np.array(Image.open(path_l))
    R = np.array(Image.open(path_r))

    properties["width"] = L.shape[1]
    properties["height"] = L.shape[0]
    properties["num_of_channels"] = 3
    properties["type_of_channels"] = "YCbCr"
    properties["depth_per_channel"] = 8

    L_ycbcr = rgb_to_ycbcr(L)
    R_ycbcr = rgb_to_ycbcr(R)

    P_L = spatial_predict(L_ycbcr)
    E_L = L_ycbcr - P_L
    k_L = max(0, int(ceil(log2(np.mean(np.abs(E_L))+1e-9))))
    bits_L, k_L = golomb_rice_encode(E_L, k_L)
    with open(os.path.join(base,"left_encoded.bin"),"wb") as f:
        f.write(bits_to_bytes(bits_L))

    MV = block_match(L_ycbcr, R_ycbcr)
    h, w, _ = R_ycbcr.shape
    P_R = np.zeros_like(R_ycbcr)
    for y in range(h):
        for x in range(w):
            dy, dx = MV[y, x]
            yy, xx = y+dy, x+dx
            if 0<=yy<h and 0<=xx<w:
                P_R[y,x] = L_ycbcr[yy,xx]

    E_R = R_ycbcr - P_R
    k_R = max(0, int(ceil(log2(np.mean(np.abs(E_R))+1e-9))))
    bits_R, k_R = golomb_rice_encode(E_R, k_R)
    with open(os.path.join(base,"right_encoded.bin"),"wb") as f:
        f.write(bits_to_bytes(bits_R))

    return {"properties":properties,"k_L":k_L,"k_R":k_R}