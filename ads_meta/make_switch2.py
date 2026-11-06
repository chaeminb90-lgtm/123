"""카페 업종변경 500만원부터?! — 배경을 '커피 → 컷팅과일' 전환 장면(GPT Image 2.6 생성)으로 바꾼 1:1 버전.

usage: python3 make_switch2.py -> out/sw2_a.jpg, out/sw2_b.jpg
"""
import json, os, subprocess
import make, make_switch

HERE = make.HERE
BHS = make.u('fonts/BlackHanSans-Regular.ttf')


def page(bg):
    return make_switch.BASE(1080) + f'''<style>
@font-face{{font-family:BHS;src:url('{BHS}')}}
body{{background:#120B07}}
.bg{{left:0;top:0;width:1080px;height:1080px;background:url('{make.u(bg)}') 0 0/1080px 1080px no-repeat}}
.shade{{left:0;top:0;width:1080px;height:1080px;background:linear-gradient(rgba(18,11,7,0) 0%,rgba(18,11,7,0) 44%,rgba(18,11,7,.6) 56%,rgba(18,11,7,.85) 66%,rgba(18,11,7,.6) 100%)}}
.l1{{left:0;right:0;top:582px;text-align:center;color:#fff;font-family:BHS;font-size:112px;letter-spacing:-.01em;line-height:1;text-shadow:0 6px 18px rgba(0,0,0,.6)}}
.l2{{left:0;right:0;top:706px;display:flex;justify-content:center;align-items:flex-end;gap:14px}}
.l2 .n{{font-family:BHS;font-size:220px;line-height:.92;color:#FF8A1E;letter-spacing:-.02em;transform:skewX(-8deg);text-shadow:0 8px 0 #6b2600}}
.l2 .b{{font-family:BHS;font-size:112px;line-height:1;color:#fff;margin-bottom:12px;transform:skewX(-8deg)}}
.brush{{left:120px;top:918px}}
.sbar{{left:34px;right:34px;top:958px;height:88px;background:#FF8A1E;transform:skewX(-12deg);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}}
.sbar span{{transform:skewX(12deg);font-size:39px;font-weight:900;font-style:italic;color:#2A1206;letter-spacing:-.045em;white-space:nowrap}}
.sbar b{{font-size:46px;font-weight:900}}
</style>
<div class="a bg"></div><div class="a shade"></div>
<div class="a l1 k">카페 업종변경</div>
<div class="a l2 k"><span class="n">500만원</span><span class="b">부터?!</span></div>
<svg class="a brush" width="840" height="40" viewBox="0 0 840 40"><path d="M8 30 C 220 8, 560 4, 832 16" stroke="#FFB15C" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M90 36 C 320 22, 560 22, 780 30" stroke="#FF8A1E" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a sbar k"><span>배달로만 <b>8900만원</b> 매출 달성 + 2인 운영 가능 업종</span></div>'''


if __name__ == '__main__':
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k in ('a', 'b'):
        hp = os.path.join(out, f'sw2_{k}.html'); open(hp, 'w').write(page(f'assets/gpt_switch_bg_{k}.jpg'))
        jobs.append({'html': hp, 'out': os.path.join(out, f'sw2_{k}.png'), 'width': 1080, 'height': 1080})
    jp = os.path.join(HERE, '_jobs_sw2.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    for j in jobs:
        Image.open(j['out']).convert('RGB').save(j['out'][:-4] + '.jpg', quality=93)
