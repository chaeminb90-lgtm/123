"""Background plates (1080x1350) for the Habokdang franchise Meta ads.

Each plate = a brand photo placed on the canvas; burned-in text is painted out by row
interpolation; the uncovered canvas is filled by a blurred edge extension and the photo's open
edges are feathered into it.

usage: python3 plates.py  -> plates/*.png
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'plates')
W, H = 1080, 1350

SRC = {
    'hero': f'{REPO}/site/img/hero_lineup.jpg',          # 1400x1045 big bowl + cups on pedestals
    'bingsu': f'{REPO}/assets/insta_src/habokdang_16.png',  # 1280x960 pedestals + checker floor
    'ring': f'{REPO}/assets/insta_src/habokdang_17.png',    # 1280x960 overhead ring of fruit cups
    'cutfruit': f'{REPO}/site/img/line_cutfruit.jpg',     # 960x720 cream wall, cups on blocks
    'delivery': f'{REPO}/site/img/line_delivery.jpg',     # 960x720 hand-held cup + bowl
    'fruitbox': f'{REPO}/site/img/src/fruitbox_src.webp',  # 1254x1254 box on cream
}

# rectangles of burned-in text to paint out: (x0, y0, x1, y1, left sample x, right sample x)
INPAINT = {
    'bingsu': [(40, 30, 486, 545, 8, 490), (40, 545, 300, 722, 8, 304)],
    'cutfruit': [(25, 25, 402, 396, 6, 406), (25, 396, 330, 485, 6, 336), (25, 485, 290, 520, 6, 296)],
    'delivery': [(28, 25, 402, 336, 6, 406)],
    'ring': [('tri', 186, 380, (300, 300, 330, 330))],
}


def inpaint(a, rects):
    a = a.astype(np.float32)
    rng = np.random.default_rng(7)
    for r in rects:
        if r[0] == 'tri':   # flat-fill the corner above the line from (0, h) to (w, 0)
            _, th, tw, (bx0, by0, bx1, by1) = r
            yy, xx = np.mgrid[0:th + 40, 0:tw + 40]
            d = (th - th * xx / tw) - yy            # >0 above the line
            band = a[0:th + 40, 0:tw + 40][(d < -8) & (d > -34)]
            ok = (band[:, 0] > 200) & (band[:, 1] > 80) & (band[:, 1] < 140) & (band[:, 2] < 70)
            c = np.median(band[ok], 0)
            yy, xx, d = yy[:th + 8, :tw + 8], xx[:th + 8, :tw + 8], d[:th + 8, :tw + 8]
            m = np.clip((d + 7) / 12.0, 0, 1)[..., None]
            reg = a[0:th + 8, 0:tw + 8]
            a[0:th + 8, 0:tw + 8] = reg * (1 - m) + (c + rng.normal(0, 1.6, reg.shape)) * m
            continue
        x0, y0, x1, y1, lx, rx = r
        if lx == 'box':   # flat fill with the mean colour of a plain sample box
            bx0, by0, bx1, by1 = rx
            c = a[by0:by1, bx0:bx1].reshape(-1, 3).mean(0)
            a[y0:y1, x0:x1] = c[None, None, :] + rng.normal(0, 1.6, (y1 - y0, x1 - x0, 3))
            continue
        R = a[y0:y1, rx - 4:rx + 4].mean(1)
        L = a[y0:y1, max(0, lx - 4):lx + 4].mean(1)        # (h, 3)
        t = np.linspace(0, 1, x1 - x0)[None, :, None]
        fill = L[:, None, :] * (1 - t) + R[:, None, :] * t
        fill = fill + rng.normal(0, 1.6, fill.shape)
        a[y0:y1, x0:x1] = fill
    return a


def plate(key, scale, x, y, feather=150, sigma=70, out=None, crop=None, wall=None):
    """wall=(left_box, right_box) in source px: fill the open top with a smooth left->right gradient
    of those two wall colours instead of extending the photo's top row."""
    im = Image.open(SRC[key]).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    if INPAINT.get(key):
        a = inpaint(a, INPAINT[key])
    if crop:
        cx0, cy0, cx1, cy1 = crop
        a = a[cy0:cy1, cx0:cx1]
    ph = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    pw, phh = int(round(ph.width * scale)), int(round(ph.height * scale))
    ph = ph.resize((pw, phh), Image.LANCZOS)
    P = np.asarray(ph).astype(np.float32)
    # edge-replicated canvas
    ys = np.clip(np.arange(H) - y, 0, phh - 1)
    xs = np.clip(np.arange(W) - x, 0, pw - 1)
    rep = P[ys][:, xs]
    blur = np.asarray(Image.fromarray(rep.astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    if wall:
        def col(b):
            x0, y0, x1, y1 = b
            return a[y0:y1, x0:x1].reshape(-1, 3).mean(0)
        cl, cr = col(wall[0]), col(wall[1])
        t = (np.arange(W) / (W - 1))[None, :, None]
        g = cl[None, None, :] * (1 - t) + cr[None, None, :] * t
        v = (1 + 0.05 * (1 - np.arange(H) / H))[:, None, None]   # a touch lighter toward the top
        wallimg = np.broadcast_to(g, (H, W, 3)) * v
        # blend: wall outside the photo, fading into the edge-extension near the seam
        ry = np.arange(H)[:, None]; rx = np.arange(W)[None, :]
        out_d = np.maximum.reduce([y - ry + 0 * rx, x - rx + 0 * ry, ry - (y + phh - 1) + 0 * rx, rx - (x + pw - 1) + 0 * ry])
        k = np.clip(out_d / 260.0, 0, 1)[..., None]
        blur = wallimg * k + blur * (1 - k)
    # alpha: 1 inside photo, ramps to 0 over `feather` px at edges that face open canvas
    yy = np.arange(H)[:, None] - y
    xx = np.arange(W)[None, :] - x
    alpha = np.ones((H, W), np.float32)
    inside = (yy >= 0) & (yy < phh) & (xx >= 0) & (xx < pw)
    alpha[~inside] = 0
    def ramp(d):
        return np.clip(d / feather, 0, 1)
    if y > 0:
        alpha *= ramp(yy)
    if y + phh < H:
        alpha *= ramp(phh - 1 - yy)
    if x > 0:
        alpha *= ramp(xx)
    if x + pw < W:
        alpha *= ramp(pw - 1 - xx)
    alpha = alpha ** 1.3
    sharp = np.zeros_like(rep)
    sharp[inside] = rep[inside]
    rng = np.random.default_rng(3)
    blur = blur + rng.normal(0, 1.8, blur.shape)
    outa = sharp * alpha[..., None] + blur * (1 - alpha[..., None])
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, (out or key) + '.png')
    Image.fromarray(np.clip(outa, 0, 255).astype(np.uint8)).save(p)
    return p, dict(scale=scale, x=x, y=y, w=pw, h=phh)


PLATES = {
    # name: (src key, scale, x, y, kwargs)
    'hero_a': ('hero', 0.80, -20, 1350 - 836, {}),            # products in lower 62%
    'hero_b': ('hero', 1.00, -230, 1350 - 1045, {}),          # tighter, big bowl
    'bingsu_a': ('bingsu', 0.844, 0, 1350 - 810, {'feather': 230, 'wall': ((60, 120, 440, 300), (1215, 150, 1275, 330))}),
    'ring_a': ('ring', 0.844, 0, 1350 - 810, {'feather': 60, 'wall': ((20, 300, 120, 420), (1180, 240, 1270, 330))}),
    'cutfruit_a': ('cutfruit', 1.125, 0, 1350 - 810, {}),
    'delivery_a': ('delivery', 1.125, 0, 1350 - 810, {}),
    'fruitbox_a': ('fruitbox', 0.86, 0, 1350 - 1078, {}),
    'fruitbox_b': ('fruitbox', 0.64, 413, 1350 - 675, {'feather': 45, 'crop': (160, 200, 1254, 1254), 'wall': ((950, 5, 1060, 70), (950, 5, 1060, 70))}),
}

if __name__ == '__main__':
    info = {}
    for name, (key, s, x, y, kw) in PLATES.items():
        p, meta = plate(key, s, x, y, out=name, **kw)
        info[name] = meta
        print(name, meta)
    # contact sheet
    ims = [Image.open(os.path.join(OUT, n + '.png')).resize((270, 338)) for n in PLATES]
    sh = Image.new('RGB', (len(ims) * 280, 338), (30, 30, 30))
    for i, im in enumerate(ims):
        sh.paste(im, (i * 280, 0))
    sh.save(os.path.join(HERE, '_plates_sheet.jpg'), quality=85)
