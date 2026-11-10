"""11월 한정 5개 지점 모집 소재 — 4:5 / 1:1 / 9:16 (GPT Image 배경) + 상담 버튼 오버레이.

usage: python3 make_cta_sizes.py <dir with raw_41.png raw_42.png raw_43.png> <out dir>
"""
import json, os, subprocess, sys
import make

SIZES = {  # name: (raw file, width, height, button top)
    '4x5': ('raw_41.png', 1080, 1350, 1254),
    '1x1': ('raw_42.png', 1080, 1080, 982),
    '9x16': ('raw_43.png', 1080, 1920, 1014),
}
BASE_AREA = 1080 * 1350  # the 4:5 is the master; other sizes scale the button by sqrt(area ratio)


def page(src, w, h, top):
    k = (w * h / BASE_AREA) ** .5
    z = lambda n: round(n * k)
    head = make.HEAD.replace('html,body{width:1080px;height:1350px;overflow:hidden}', f'html,body{{width:{w}px;height:{h}px;overflow:hidden}}')
    return head + f'''<style>
body{{background:#C43C02}}
.bg{{left:0;top:0;width:{w}px;height:{h}px;background:url('file://{src}') 0 0/{w}px {h}px no-repeat}}
.cta{{left:0;right:0;top:{top}px;display:flex;justify-content:center}}
.cta a{{display:flex;align-items:center;gap:{z(14)}px;padding:{z(13)}px {z(40)}px {z(13)}px {z(46)}px;border-radius:80px;background:#FFF3E4;color:#B53F06;
  font-size:{z(38)}px;font-weight:900;letter-spacing:-.04em;box-shadow:0 {z(6)}px 0 #8E2E02,0 {z(14)}px {z(26)}px rgba(70,20,0,.35)}}
</style>
<div class="a bg"></div>
<div class="a cta k"><a>소자본 창업상담 바로가기
<svg width="{z(34)}" height="{z(34)}" viewBox="0 0 34 34"><circle cx="17" cy="17" r="17" fill="#E0560C"/><path d="M13 9 L22 17 L13 25" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div>'''


if __name__ == '__main__':
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    jobs = []
    for name, (raw, w, h, top) in SIZES.items():
        hp = os.path.join(make.HERE, 'out', f'cta_{name}.html')
        open(hp, 'w').write(page(os.path.join(src_dir, raw), w, h, top))
        jobs.append({'html': hp, 'out': os.path.join(make.HERE, 'out', f'cta_{name}.png'), 'width': w, 'height': h, 'name': name})
    jp = os.path.join(make.HERE, '_jobs_ctas.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(make.HERE, 'render.js'), jp], check=True)
    from PIL import Image
    for j in jobs:
        Image.open(j['out']).convert('RGB').save(os.path.join(out_dir, f"하복당_11월한정5개지점_3천만원_상담버튼_{j['name']}.jpg"), quality=93)
