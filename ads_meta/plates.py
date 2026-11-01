"""Background plates (1080x1350) for the Habokdang franchise Meta ads.

Each plate = a brand photo placed on the canvas. Burned-in text is painted out (row interpolation),
the canvas outside the photo is filled with a flat wall colour sampled from clean wall in the source
(optionally blended with a blurred edge extension near the seam), and the photo's open edges are
feathered over a short distance so products near the edge stay sharp.

usage: python3 plates.py  -> plates/*.png, _plates_sheet.jpg
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'plates')
W, H = 1080, 1350

SRC = {
    'hero': f'{REPO}/site/img/hero_lineup.jpg',             # 1400x1045 big bowl + cups on pedestals
    'bingsu': f'{REPO}/assets/insta_src/habokdang_16.png',  # 1280x960 pedestals, arch, checker floor
    'ring': f'{REPO}/assets/insta_src/habokdang_17.png',    # 1280x960 overhead ring of fruit cups
    'cutfruit': f'{REPO}/site/img/line_cutfruit.jpg',       # 960x720 cream wall, cups on blocks
    'delivery': f'{REPO}/site/img/line_delivery.jpg',       # 960x720 hand-held cup + bowl
    'fruitbox': f'{REPO}/site/img/src/fruitbox_src.webp',   # 1254x1254 fruit box on a table
    'pavlova': f'{REPO}/site/img/pavlova_1.jpg',            # 1000x750 branded pavlova cup on beige
}

# burned-in text to paint out: (x0, y0, x1, y1, left sample x, right sample x)
INPAINT = {
    'bingsu': [(40, 30, 486, 545, 8, 490), (40, 545, 300, 722, 8, 304), ('mirror_arch',)],
    'cutfruit': [(25, 25, 402, 396, 6, 406), (25, 396, 330, 485, 6, 336), (25, 485, 290, 520, 6, 296)],
    'delivery': [(28, 25, 402, 336, 6, 406)],
    'ring': [('tri', 186, 380)],
}

# arch in habokdang_16 (source px): centre, outer and inner radius (measured from the cream band)
ARCH = dict(cx=947, cy=315, R=333, r=238)


def inpaint(a, rects):
    a = a.astype(np.float32)
    rng = np.random.default_rng(7)
    for r in rects:
        if r[0] == 'tri':   # flat-fill the checker corner above the line from (0, h) to (w, 0)
            _, th, tw = r
            yy, xx = np.mgrid[0:th + 40, 0:tw + 40]
            d = (th - th * xx / tw) - yy
            band = a[0:th + 40, 0:tw + 40][(d < -8) & (d > -34)]
            ok = (band[:, 0] > 200) & (band[:, 1] > 80) & (band[:, 1] < 140) & (band[:, 2] < 70)
            c = np.median(band[ok], 0)
            d = d[:th + 8, :tw + 8]
            m = np.clip((d + 7) / 12.0, 0, 1)[..., None]
            reg = a[0:th + 8, 0:tw + 8]
            a[0:th + 8, 0:tw + 8] = reg * (1 - m) + (c + rng.normal(0, 1.6, reg.shape)) * m
            continue
        if r[0] == 'mirror_arch':
            # the milk pitcher + stream overlap the right half of the symmetric arch: replace them with
            # the mirrored left half (x' = 2*cx - x), feathered at the region border
            cx = ARCH['cx']
            m = np.zeros(a.shape[:2], np.float32)
            m[0:104, 958:1205] = 1
            m[104:118, 974:1012] = 1
            m[100:122, 1150:1215] = 1
            m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
            ys, xs = np.nonzero(m > 0)
            src = a.copy()
            a[ys, xs] = src[ys, 2 * cx - xs] * m[ys, xs, None] + src[ys, xs] * (1 - m[ys, xs, None])
            # outside the arch the mirrored wall is lit differently: use this side's wall colour instead
            yy, xx = np.mgrid[0:124, 940:1260]
            dist = np.hypot(xx - cx, yy - ARCH['cy'])
            w = np.clip((dist - ARCH['R'] - 1) / 3.0, 0, 1) * (xx > cx)
            w = w * np.clip((122 - yy) / 4.0, 0, 1)                 # fade out at the bottom of the patch
            rowcol = src[0:124, 1240:1266].mean(1)                 # right-hand wall per row
            reg = a[0:124, 940:1260]
            a[0:124, 940:1260] = reg * (1 - w[..., None]) + rowcol[:, None, :] * w[..., None]
            continue
        x0, y0, x1, y1, lx, rx = r
        R = a[y0:y1, rx - 4:rx + 4].mean(1)
        L = a[y0:y1, max(0, lx - 4):lx + 4].mean(1)
        t = np.linspace(0, 1, x1 - x0)[None, :, None]
        a[y0:y1, x0:x1] = L[:, None, :] * (1 - t) + R[:, None, :] * t + rng.normal(0, 1.6, (y1 - y0, x1 - x0, 3))
    return a


def plate(key, scale, x, y, feather=40, sigma=70, out=None, crop=None, wall=None, wall_k=1, lift=0.0, arch=False):
    """wall=(left_box, right_box) in *source* px (before crop): flat left->right wall gradient outside the
    photo. wall_k = distance (px) over which the wall replaces the blurred edge extension (1 = wall only)."""
    a = np.asarray(Image.open(SRC[key]).convert('RGB')).astype(np.float32)
    if INPAINT.get(key):
        a = inpaint(a, INPAINT[key])
    full = a
    if crop:
        cx0, cy0, cx1, cy1 = crop
        a = a[cy0:cy1, cx0:cx1]
    ph = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    pw, phh = int(round(ph.width * scale)), int(round(ph.height * scale))
    P = np.asarray(ph.resize((pw, phh), Image.LANCZOS)).astype(np.float32)
    ys = np.clip(np.arange(H) - y, 0, phh - 1)
    xs = np.clip(np.arange(W) - x, 0, pw - 1)
    rep = P[ys][:, xs]
    fill = np.asarray(Image.fromarray(rep.astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    if wall == 'row':
        # extend the photo's own top rows straight up; cream (arch) columns are interpolated across
        rowc = np.median(P[2:8], 0)                                  # (pw, 3)
        cream = (rowc[:, 0] > 215) & (rowc[:, 1] > 165) & (rowc[:, 2] > 110) & (rowc[:, 1] - rowc[:, 2] < 95)
        idx = np.arange(pw)
        cream = np.convolve(cream.astype(float), np.ones(15), 'same') > 0      # include anti-aliased edges
        if cream.any() and (~cream).any():
            for c in range(3):
                rowc[cream, c] = np.interp(idx[cream], idx[~cream], rowc[~cream, c])
        k1 = np.exp(-0.5 * (np.arange(-30, 31) / 8.0) ** 2); k1 /= k1.sum()
        rowc = np.stack([np.convolve(np.pad(rowc[:, c], 30, mode='edge'), k1, 'valid') for c in range(3)], 1)
        rowc = rowc[np.clip(np.arange(W) - x, 0, pw - 1)]
        v = (1 + lift * (1 - np.arange(H) / H))[:, None, None]
        wallimg = np.broadcast_to(rowc[None], (H, W, 3)) * v
        top = (np.arange(H) < y + feather + 2)[:, None, None]      # also under the feathered seam
        fill = np.where(top, wallimg, fill)
    elif wall:
        def col(b):
            x0, y0, x1, y1 = b
            return full[y0:y1, x0:x1].reshape(-1, 3).mean(0)
        cl, cr = col(wall[0]), col(wall[1])
        t = (np.arange(W) / (W - 1))[None, :, None]
        g = cl[None, None, :] * (1 - t) + cr[None, None, :] * t
        v = (1 + lift * (1 - np.arange(H) / H))[:, None, None]
        wallimg = np.broadcast_to(g, (H, W, 3)) * v
        ry = np.arange(H)[:, None]; rx = np.arange(W)[None, :]
        out_d = np.maximum.reduce([y - ry + 0 * rx, x - rx + 0 * ry, ry - (y + phh - 1) + 0 * rx, rx - (x + pw - 1) + 0 * ry])
        k = np.clip(out_d / float(wall_k), 0, 1)[..., None]
        fill = wallimg * k + fill * (1 - k)
    yy = np.arange(H)[:, None] - y
    xx = np.arange(W)[None, :] - x
    alpha = np.ones((H, W), np.float32)
    inside = (yy >= 0) & (yy < phh) & (xx >= 0) & (xx < pw)
    alpha[~inside] = 0
    ramp = lambda d: np.clip(d / feather, 0, 1)
    if y > 0: alpha *= ramp(yy)
    if y + phh < H: alpha *= ramp(phh - 1 - yy)
    if x > 0: alpha *= ramp(xx)
    if x + pw < W: alpha *= ramp(pw - 1 - xx)
    alpha = alpha ** 1.3
    sharp = np.zeros_like(rep); sharp[inside] = rep[inside]
    fill = fill + np.random.default_rng(3).normal(0, 1.8, fill.shape)
    outa = sharp * alpha[..., None] + fill * (1 - alpha[..., None])
    img = Image.fromarray(np.clip(outa, 0, 255).astype(np.uint8))
    if arch:   # redraw the arch apex that lies just above the photo's top edge
        img = draw_arch_apex(img, full, scale, x, y)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, (out or key) + '.png')
    img.save(p)
    return p, dict(scale=scale, x=x, y=y, w=pw, h=phh)


def draw_arch_apex(img, full, s, px, py):
    cx, cy = ARCH['cx'] * s + px, ARCH['cy'] * s + py
    R, r = ARCH['R'] * s, ARCH['r'] * s
    band = full[150:300, 640:700].reshape(-1, 3).mean(0)          # left leg of the arch
    ss = 4
    m = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([(cx - R) * ss, (cy - R) * ss, (cx + R) * ss, (cy + R) * ss], fill=255)
    d.ellipse([(cx - r) * ss, (cy - r) * ss, (cx + r) * ss, (cy + r) * ss], fill=0)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    m[py + 16:, :] = 0                      # above the seam and under its feather (the photo has the rest)
    fade = np.clip((np.arange(H) - (py - 2)) / 8.0, 0, 1)[:, None]   # soft join at the seam
    m = m * (1 - fade * 0.0)
    A = np.asarray(img).astype(np.float32)
    col = band[None, None, :] + np.random.default_rng(5).normal(0, 1.6, A.shape)
    A = A * (1 - m[..., None]) + col * m[..., None]
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))


PLATES = {
    # name: (src key, scale, x, y, kwargs)
    'hero_a': ('hero', 0.80, -20, 560, {'feather': 16, 'wall': 'row'}),
    'hero_c': ('hero', 0.80, -20, 494, {'feather': 16, 'wall': 'row'}),
    'bingsu_a': ('bingsu', 0.844, 0, 540, {'feather': 10, 'wall': 'row', 'arch': True}),
    'ring_a': ('ring', 0.844, 0, 540, {'feather': 40, 'wall': ((1000, 40, 1050, 90), (1000, 40, 1050, 90))}),
    'cutfruit_a': ('cutfruit', 1.125, 0, 540, {'feather': 16, 'wall': 'row'}),
    'delivery_a': ('delivery', 1.125, 0, 540, {'feather': 150, 'sigma': 70, 'wall_k': 260, 'wall': ((420, 5, 470, 40), (700, 5, 760, 40))}),
    'fruitbox_b': ('fruitbox', 0.62, 380, 600, {'feather': 30, 'crop': (90, 260, 1180, 1254), 'wall': ((300, 40, 700, 200), (300, 40, 700, 200)), 'lift': 0.04}),
    'pavlova_a': ('pavlova', 1.08, 0, 540, {'feather': 16, 'wall': 'row'}),
    'pavlova_b': ('pavlova', 0.72, 360, 1350 - 540, {'feather': 22, 'wall': ((20, 5, 200, 40), (800, 5, 980, 40))}),
}

if __name__ == '__main__':
    for name, (key, s, x, y, kw) in PLATES.items():
        p, meta = plate(key, s, x, y, out=name, **kw)
        print(name, meta)
    ims = [Image.open(os.path.join(OUT, n + '.png')).resize((270, 338)) for n in PLATES]
    sh = Image.new('RGB', (len(ims) * 280, 338), (30, 30, 30))
    for i, im in enumerate(ims):
        sh.paste(im, (i * 280, 0))
    sh.save(os.path.join(HERE, '_plates_sheet.jpg'), quality=85)
