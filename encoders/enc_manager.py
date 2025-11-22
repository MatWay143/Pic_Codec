import numpy as np

def predict_med(W, N, NW):
    if NW >= max(N, W):
        return min(N, W)
    elif NW <= min(N, W):
        return max(N, W)
    else:
        return N + W - NW

def encode_residuals(img):
    # img: uint8 یا uint16؛ خروجی: residuals همان اندازه با نوع signed
    h, w = img.shape
    # نوع signed بزرگتر برای جلوگیری از سرریز هنگام محاسبه r
    residuals = np.zeros_like(img, dtype=np.int16 if img.dtype == np.uint8 else np.int32)

    for i in range(h):
        for j in range(w):
            x = int(img[i, j])
            if i == 0 and j == 0:
                x_hat = 0  # قرار اولیه ساده؛ lossless است چون r = x - 0
            elif i == 0:
                W = int(img[i, j-1])
                N = 0
                NW = 0
                x_hat = W  # در سطر اول، از چپ استفاده کنید
            elif j == 0:
                W = 0
                N = int(img[i-1, j])
                NW = 0
                x_hat = N  # در ستون اول، از بالا استفاده کنید
            else:
                W = int(img[i, j-1])
                N = int(img[i-1, j])
                NW = int(img[i-1, j-1])
                x_hat = predict_med(W, N, NW)

            residuals[i, j] = x - x_hat
    return residuals

def decode_from_residuals(residuals):
    # بازسازی دقیق img از residuals با همان پیش‌بینی
    h, w = residuals.shape
    # نوع بزرگتر برای تجمع و سپس برش به دامنه اصلی در انتها (اگر نیاز باشد)
    recon = np.zeros((h, w), dtype=np.int32)

    for i in range(h):
        for j in range(w):
            if i == 0 and j == 0:
                x_hat = 0
            elif i == 0:
                W = recon[i, j-1]
                N = 0
                NW = 0
                x_hat = W
            elif j == 0:
                W = 0
                N = recon[i-1, j]
                NW = 0
                x_hat = N
            else:
                W = recon[i, j-1]
                N = recon[i-1, j]
                NW = recon[i-1, j-1]
                x_hat = predict_med(W, N, NW)

            recon[i, j] = x_hat + int(residuals[i, j])

    # اگر دامنه اصلی uint8 بود:
    # بازگشت به دامنه بدون کلیپ لازم نیست چون مقدار دقیقاً برابر نمونه اصلی است،
    # با این حال برای ایمنی نوع را تبدیل می‌کنیم.
    return recon.astype(np.int32)
