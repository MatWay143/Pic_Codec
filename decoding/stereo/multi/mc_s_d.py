import numpy as np
import cv2
import os
import struct

def ycbcr_to_rgb(img):
    Y = img[:,:,0].astype(np.float32)
    Cb = img[:,:,1].astype(np.float32)-128
    Cr = img[:,:,2].astype(np.float32)-128
    R = Y + 1.402*Cr
    G = Y - 0.344136*Cb - 0.714136*Cr
    B = Y + 1.772*Cb
    return np.clip(np.stack([R,G,B], axis=2), 0, 255).astype(np.uint8)

def undo_remap(residual):
    return np.where(residual%2==0,residual//2,-(residual+1)//2)

def undo_bias(residual, mean):
    return residual + int(mean)

def huffman_decode(bits, code, shape):
    inv_code = {v:k for k,v in code.items()}
    bitstr = ''.join(f'{b:08b}' for b in bits)
    out = []
    buffer = ''
    for b in bitstr:
        buffer += b
        if buffer in inv_code:
            out.append(inv_code[buffer])
            buffer = ''
        if len(out) == np.prod(shape):
            break
    return np.array(out, dtype=np.int32).reshape(shape)

def block_reconstruct_right(L_ycbcr, mv, bs=4):
    h,w,_ = L_ycbcr.shape
    pred = np.zeros_like(L_ycbcr)
    idx = 0
    for y in range(0,h,bs):
        for x in range(0,w,bs):
            bh = min(bs,h-y)
            bw = min(bs,w-x)
            dx = mv[idx]
            pred[y:y+bh, x:x+bw, 0] = L_ycbcr[y:y+bh, x+dx:x+dx+bw, 0]
            pred[y:y+bh, x:x+bw, 1] = L_ycbcr[y:y+bh, x:x+bw, 1]
            pred[y:y+bh, x:x+bw, 2] = L_ycbcr[y:y+bh, x:x+bw, 2]
            idx += 1
    return pred

def multicolor_stereo_decode(path_l_encoded, path_r_encoded):
    folder = os.path.dirname(path_l_encoded)

    # Left
    with open(path_l_encoded,'rb') as f:
        h,w,c,pad = struct.unpack('IIIb', f.read(13))
        bits_len = struct.unpack('I', f.read(4))[0]
        bitsL = f.read(bits_len)
        code_len = struct.unpack('I', f.read(4))[0]
        code_raw = f.read(code_len)
        codeL = {i: code_raw[i:i+8].decode() for i in range(0, code_len,8)}
    L_ycbcr = huffman_decode(bitsL, codeL, (h,w,c))
    L_ycbcr = undo_bias(undo_remap(L_ycbcr), 0).astype(np.uint8)

    # Right
    with open(path_r_encoded,'rb') as f:
        hR,wR,cR,padR = struct.unpack('IIIb', f.read(13))
        mv_len = struct.unpack('I', f.read(4))[0]
        mv = np.frombuffer(f.read(mv_len*2), dtype=np.int16)
        bits_lenR = struct.unpack('I', f.read(4))[0]
        bitsR = f.read(bits_lenR)
        code_lenR = struct.unpack('I', f.read(4))[0]
        code_rawR = f.read(code_lenR)
        codeR = {i: code_rawR[i:i+8].decode() for i in range(0, code_lenR,8)}

    R_pred = block_reconstruct_right(L_ycbcr, mv)
    residualR = huffman_decode(bitsR, codeR, (hR,wR,1))[:,:,0]
    residualR = undo_bias(undo_remap(residualR),0).astype(np.uint8)
    # Remained Pixels جایگذاری
    mask = (R_pred[:,:,0] != residualR)
    R_ycbcr = R_pred.copy()
    R_ycbcr[:,:,0][mask] = residualR[mask]

    cv2.imwrite(os.path.join(folder,'left_reconstructed.png'), ycbcr_to_rgb(L_ycbcr))
    cv2.imwrite(os.path.join(folder,'right_reconstructed.png'), ycbcr_to_rgb(R_ycbcr))