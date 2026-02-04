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
    from numpy import maximum, minimum, where
    p[1:,1:] = where(c >= maximum(a[1:], b[:,1:]), minimum(a[1:], b[:,1:]),
                where(c <= minimum(a[1:], b[:,1:]), maximum(a[1:], b[:,1:]), a[1:] + b[:,1:] - c))
    return p

def bytes_to_bits(b):
    bits=[]
    for byte in b:
        for i in reversed(range(8)):
            bits.append((byte>>i)&1)
    return bits

def golomb_rice_decode(bits, shape, k):
    x = np.zeros(np.prod(shape),dtype=np.int16)
    i = 0
    idx = 0
    while idx < x.size:
        q = 0
        while i<len(bits) and bits[i]==1:
            q+=1
            i+=1
        i+=1
        r = 0
        for j in range(k):
            r = (r<<1) | bits[i]
            i+=1
        val = (q<<k)|r
        x[idx]=val
        idx+=1
    return x.reshape(shape)

def multicolor_stereo_decode(path_l_encoded, path_r_encoded, shape_L=(None,None,3), shape_R=(None,None,3), k_L=0, k_R=0):
    base = os.path.dirname(path_l_encoded)

    with open(path_l_encoded,"rb") as f:
        bits_L = bytes_to_bits(f.read())
    L_data = golomb_rice_decode(bits_L, shape_L, k_L)
    P_L = spatial_predict(L_data)
    L_recon = P_L + L_data
    L_rgb = ycbcr_to_rgb(L_recon)
    Image.fromarray(L_rgb).save(os.path.join(base,"left_reconstructed_decoded.png"))

    with open(path_r_encoded,"rb") as f:
        bits_R = bytes_to_bits(f.read())
    R_data = golomb_rice_decode(bits_R, shape_R, k_R)
    P_R2 = spatial_predict(R_data)
    R_recon = P_R2 + R_data
    R_rgb = ycbcr_to_rgb(R_recon)
    Image.fromarray(R_rgb).save(os.path.join(base,"right_reconstructed_decoded.png"))

    return {
        "Left_reconstructed": os.path.join(base,"left_reconstructed_decoded.png"),
        "Right_reconstructed": os.path.join(base,"right_reconstructed_decoded.png")
    }