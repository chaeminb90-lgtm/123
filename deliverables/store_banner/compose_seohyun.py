"""Compose the 서현점 banner: empty table base + individually photographed products + original panel/text."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
D = '/tmp/claude-0/-home-user-123/95f16457-453a-5fac-9901-17b12c6ad84d/scratchpad/seohyun/'
W, H = 1925, 817
BOX = {  # product index: (x0, y0, x1, y1) in the original banner
    2: (707, 152, 897, 468), 1: (515, 200, 728, 505), 4: (895, 183, 1225, 455), 5: (1200, 203, 1462, 428),
    6: (1415, 270, 1787, 517), 3: (662, 355, 860, 560), 7: (1045, 433, 1345, 620), 9: (1602, 398, 1900, 670),
    8: (1253, 515, 1578, 712), 11: (530, 458, 748, 640), 10: (690, 498, 1168, 732),
}
ORDER = [2, 1, 4, 5, 6, 3, 7, 9, 8, 11, 10]
ADJ = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}

base = Image.open(D + 'p/0.png').convert('RGB')
bh = round(base.height * W / base.width)
base = base.resize((W, bh), Image.LANCZOS)
dy = (bh - H) // 2
canvas = base.crop((0, dy, W, dy + H)).convert('RGBA')

def shadow_layer(cx, by, ow, oh):
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
    # soft cast shadow to the lower right, then a tight contact shadow
    rw, rh = ow * .50, max(18, oh * .07)
    d.ellipse((cx - rw + ow * .05, by - rh * .6, cx + rw + ow * .05, by + rh * 1.1), fill=95)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    c = Image.new('L', (W, H), 0); d2 = ImageDraw.Draw(c)
    cw = ow * .42
    d2.ellipse((cx - cw, by - 9, cx + cw, by + 7), fill=120)
    c = c.filter(ImageFilter.GaussianBlur(5))
    return Image.fromarray(np.maximum(np.array(sh), np.array(c)))

for k in ORDER:
    im = Image.open(D + f'p/{k}.png').convert('RGBA')
    a = im.getchannel('A').point(lambda v: 255 if v > 24 else 0)
    im = im.crop(a.getbbox())
    x0, y0, x1, y1 = BOX[k]
    adj = ADJ.get(str(k), {})
    s = min((x1 - x0) / im.width, (y1 - y0) / im.height) * adj.get('s', 1)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    cx = (x0 + x1) / 2 + adj.get('dx', 0); by = y1 + adj.get('dy', 0)
    px, py = round(cx - im.width / 2), round(by - im.height)
    sh = shadow_layer(cx, by - 4, im.width, im.height)
    dark = Image.new('RGBA', (W, H), (110, 40, 6, 255)); dark.putalpha(sh)
    canvas = Image.alpha_composite(canvas, dark)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.paste(im, (px, py), im)
    canvas = Image.alpha_composite(canvas, layer)

out = np.array(canvas.convert('RGB')).astype(float)
o = np.array(Image.open(D + 'banner_ref.png').convert('RGB')).astype(float)
m = np.ones(W); m[500:520] = np.linspace(1, 0, 20); m[520:] = 0
out = out * (1 - m[None, :, None]) + o * m[None, :, None]
for x0, y0, x1, y1 in ((465, 38, 1705, 132), (1478, 736, 1900, 802), (1705, 18, 1918, 192)):
    G = o[y0:y1, x0:x1, 1]
    a = np.clip((G - 110) / (225 - 110), 0, 1)
    col = np.array([255., 229., 201.])
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a[..., None]) + col * a[..., None]
im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
im.save(D + 'seohyun_v2.png'); im.save(D + 'seohyun_v2.jpg', quality=95)
im.resize((1100, 467), Image.LANCZOS).save(D + 'v2_view.jpg', quality=88)
