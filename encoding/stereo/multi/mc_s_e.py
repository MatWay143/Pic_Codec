import numpy as np
import cv2
from collections import Counter
import heapq
import os
import struct

def rgb_to_ycbcr(img):
    R=img[:,:,0].astype(np.float32)
    G=img[:,:,1].astype(np.float32)
    B=img[:,:,2].astype(np.float32)
    Y=0.299*R+0.587*G+0.114*B
    Cb=-0.168736*R-0.331264*G+0.5*B+128
    Cr=0.5*R-0.418688*G-0.081312*B+128
    return np.stack([Y,Cb,Cr],axis=2).astype(np.uint8)

def med(a,b,c):
    return np.where(c>=np.maximum(a,b), np.minimum(a,b),
           np.where(c<=np.minimum(a,b), np.maximum(a,b), a+b-c))

def first_order_pred(img):
    h,w=img.shape
    pred=np.zeros_like(img)
    pred[:,1:]=img[:,:-1]
    return pred

def second_order_pred(img):
    h,w=img.shape
    pred=np.zeros_like(img)
    pred[:,2:]=2*img[:,1:-1]-img[:,:-2]
    return pred

def third_order_pred(img):
    h,w=img.shape
    pred=np.zeros_like(img)
    pred[:,3:]=3*img[:,2:-1]-3*img[:,1:-2]+img[:,:-3]
    return pred

def med_predict(img):
    h,w=img.shape
    pred=np.zeros_like(img)
    for y in range(h):
        for x in range(w):
            a=img[y,x-1] if x>0 else 0
            b=img[y-1,x] if y>0 else 0
            c0=img[y-1,x-1] if x>0 and y>0 else 0
            pred[y,x]=med(a,b,c0)
    return pred

def compute_entropy(residual):
    data=residual.flatten()
    freq=Counter(data)
    total=sum(freq.values())
    probs=np.array([v/total for v in freq.values()])
    return -np.sum(probs*np.log2(probs+1e-9))

def best_predictor(img):
    h,w,c=img.shape
    best_preds=[]
    for k in range(c):
        channel=img[:,:,k].astype(np.int32)
        candidates=[first_order_pred(channel),
                    second_order_pred(channel),
                    third_order_pred(channel),
                    med_predict(channel)]
        entropies=[compute_entropy(channel-p) for p in candidates]
        best_preds.append(candidates[np.argmin(entropies)])
    return np.stack(best_preds,axis=2)

def remap_errors(residual):
    return np.where(residual>=0,2*residual,-2*residual-1)

def bias_cancellation(residual):
    mean=np.mean(residual)
    return (residual-int(mean)).astype(np.int32)

def huffman_encode(arr):
    data=arr.flatten()
    freq=Counter(data)
    heap=[[wt,[sym,'']] for sym,wt in freq.items()]
    heapq.heapify(heap)
    while len(heap)>1:
        lo=heapq.heappop(heap); hi=heapq.heappop(heap)
        for pair in lo[1:]: pair[1]='0'+pair[1]
        for pair in hi[1:]: pair[1]='1'+pair[1]
        heapq.heappush(heap,[lo[0]+hi[0]]+lo[1:]+hi[1:])
    code=dict(sorted(heapq.heappop(heap)[1:],key=lambda x:x[0]))
    bits=''.join(code[v] for v in data)
    pad=(8-len(bits)%8)%8
    bits+='0'*pad
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8)), pad, code

def block_match_right(L,R,bs=4,search=4):
    h,w,_=L.shape
    mv=[]
    pred=np.zeros_like(R)
    for y in range(0,h,bs):
        for x in range(0,w,bs):
            bh=min(bs,h-y)
            bw=min(bs,w-x)
            blk=R[y:y+bh,x:x+bw,0]
            best_dx=0
            for dx in range(1,search+1):
                xx=x+dx
                if xx+bw>w: break
                ref=L[y:y+bh,xx:xx+bw,0]
                err=np.sum(np.abs(blk-ref))
                if dx==1 or err<best_err: best_err=err; best_dx=dx
            mv.append(best_dx)
            pred[y:y+bh,x:x+bw]=L[y:y+bh,x+best_dx:x+best_dx+bw]
    return np.array(mv,dtype=np.int16), pred

def right_residual_mask(R_actual,R_pred):
    mask = R_actual[:,:,0] != R_pred[:,:,0]
    return mask

def encode_left_final(L_ycbcr):
    predictor=best_predictor(L_ycbcr)
    residual=L_ycbcr.astype(np.int32)-predictor.astype(np.int32)
    residual=remap_errors(residual)
    residual=bias_cancellation(residual)
    bits,pad,code=huffman_encode(residual)
    return bits,pad,code

def encode_right_remained(R_ycbcr,R_pred,L_ycbcr):
    mask=right_residual_mask(R_ycbcr,R_pred)
    residual=R_ycbcr[:,:,0].astype(np.int32)-R_pred[:,:,0].astype(np.int32)
    residual=remap_errors(residual)
    residual=bias_cancellation(residual[mask])
    bits,pad,code=huffman_encode(residual)
    return bits,pad,code,mask

def multicolor_stereo_encode(path_l,path_r):
    folder=os.path.dirname(path_l)
    L=cv2.imread(path_l)
    R=cv2.imread(path_r)
    L_ycbcr=rgb_to_ycbcr(L)
    R_ycbcr=rgb_to_ycbcr(R)

    bitsL,padL,codeL=encode_left_final(L_ycbcr)

    mv,R_pred=block_match_right(L_ycbcr,R_ycbcr)
    bitsR,padR,codeR,mask=encode_right_remained(R_ycbcr,R_pred,L_ycbcr)

    with open(os.path.join(folder,'left.bin'),'wb') as f:
        f.write(struct.pack('IIIb',*L_ycbcr.shape,padL))
        f.write(bitsL)

    with open(os.path.join(folder,'right.bin'),'wb') as f:
        f.write(struct.pack('IIIb',*R_ycbcr.shape,padR))
        f.write(struct.pack('I',len(mv)))
        f.write(mv.tobytes())
        f.write(bitsR)