"""Put the original banner's left panel, menu text, bottom-right text and icons onto a new 21:9 scene."""
import sys
import numpy as np
from PIL import Image
D = '/tmp/claude-0/-home-user-123/95f16457-453a-5fac-9901-17b12c6ad84d/scratchpad/seohyun/'
src, name = sys.argv[1], sys.argv[2]
W, H = 1925, 817
g = Image.open(src).convert('RGB')
gh = round(g.height * W / g.width)
g = g.resize((W, gh), Image.LANCZOS)
dy = (gh - H) // 2
out = np.array(g.crop((0, dy, W, dy + H))).astype(float)
o = np.array(Image.open(D + 'banner_ref.png').convert('RGB')).astype(float)
m = np.ones(W); m[500:520] = np.linspace(1, 0, 20); m[520:] = 0
out = out * (1 - m[None, :, None]) + o * m[None, :, None]
col = np.array([255., 229., 201.])
for x0, y0, x1, y1 in ((465, 38, 1705, 132), (1478, 736, 1900, 802), (1705, 18, 1918, 192)):
    a = np.clip((o[y0:y1, x0:x1, 1] - 110) / (225 - 110), 0, 1)
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a[..., None]) + col * a[..., None]
im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
im.save(D + name + '.png'); im.save(D + name + '.jpg', quality=95)
im.resize((1100, 467), Image.LANCZOS).save(D + name + '_view.jpg', quality=88)
