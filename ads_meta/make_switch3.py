"""카페 업종변경 500만원부터?! — 실사 버전. 왼쪽: 고객이 준 빈 카페 사진(업스케일만, 내용 그대로),
오른쪽: 하복당 실제 제품 사진. AI로 새로 그린 이미지는 쓰지 않는다.

usage: python3 make_switch3.py -> out/sw3_a.jpg (제품 라인업), out/sw3_b.jpg (컵 진열)
"""
import json, os, subprocess
import make, make_switch

HERE = make.HERE
BHS = make.u('fonts/BlackHanSans-Regular.ttf')
CAFE = make.u('assets/real_empty_cafe.jpg')
HERO = 'file:///home/user/123/site/img/hero_lineup.jpg'
CUT = 'file:///home/user/123/site/img/line_cutfruit.jpg'

RIGHT = {
    # background for the 하복당 half: (url, size, position, fill colour)
    'a': (HERO, '1000px auto', '509px -14px', '#F07A2C'),
    'b': (CUT, 'auto 760px', '67px -10px', '#FBF3EA'),
}


SPOT = '''<div class="a" style="left:0;top:0;width:1080px;height:660px;clip-path:polygon(620px 0,1080px 0,1080px 660px,460px 660px);
  background:radial-gradient(ellipse 46% 62% at 74% 40%,rgba(255,200,140,0) 0%,rgba(255,128,30,.34) 50%,rgba(225,88,8,.86) 100%);mix-blend-mode:multiply"></div>
<div class="a" style="left:0;top:0;width:1080px;height:660px;clip-path:polygon(700px 0,880px 0,1080px 620px,560px 620px);
  background:linear-gradient(rgba(255,178,92,.55),rgba(255,150,60,.18) 70%,rgba(255,150,60,0));mix-blend-mode:screen;filter:blur(18px)"></div>
<div class="a" style="left:0;top:0;width:1080px;height:660px;clip-path:polygon(620px 0,1080px 0,1080px 660px,460px 660px);
  background:radial-gradient(ellipse 30% 40% at 77% 46%,rgba(255,190,110,.28),rgba(255,190,110,0) 70%);mix-blend-mode:screen"></div>'''


def page(k):
    url, size, pos, fill = RIGHT[k]
    spot = SPOT if k == 'b' else ''
    return make_switch.BASE(1080) + f'''<style>
@font-face{{font-family:BHS;src:url('{BHS}')}}
body{{background:#120B07}}
.cafe{{left:0;top:0;width:1080px;height:660px;background:url('{CAFE}') -170px 0/auto 660px no-repeat;
  filter:brightness(.72) saturate(.5) contrast(1.05);clip-path:polygon(0 0,620px 0,460px 660px,0 660px)}}
.fruit{{left:0;top:0;width:1080px;height:660px;background:{fill} url('{url}') {pos}/{size} no-repeat;
  clip-path:polygon(620px 0,1080px 0,1080px 660px,460px 660px)}}
.shade{{left:0;top:0;width:1080px;height:1080px;background:linear-gradient(rgba(18,11,7,0) 0%,rgba(18,11,7,0) 46%,rgba(18,11,7,.7) 56%,#120B07 64%)}}
.lab{{top:34px;padding:10px 24px;border-radius:40px;font-size:30px;font-weight:900;letter-spacing:-.03em}}
.lab.c{{left:36px;background:rgba(30,30,30,.82);color:#e6e6e6}}
.lab.h{{left:660px;background:#FF8A1E;color:#2A1206}}
.l1{{left:0;right:0;top:582px;text-align:center;color:#fff;font-family:BHS;font-size:112px;letter-spacing:-.01em;line-height:1;text-shadow:0 6px 18px rgba(0,0,0,.6)}}
.l2{{left:0;right:0;top:706px;display:flex;justify-content:center;align-items:flex-end;gap:14px}}
.l2 .n{{font-family:BHS;font-size:220px;line-height:.92;color:#FF8A1E;letter-spacing:-.02em;transform:skewX(-8deg);text-shadow:0 8px 0 #6b2600}}
.l2 .b{{font-family:BHS;font-size:112px;line-height:1;color:#fff;margin-bottom:12px;transform:skewX(-8deg)}}
.brush{{left:120px;top:918px}}
.sbar{{left:34px;right:34px;top:958px;height:88px;background:#FF8A1E;transform:skewX(-12deg);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}}
.sbar span{{transform:skewX(12deg);font-size:39px;font-weight:900;font-style:italic;color:#2A1206;letter-spacing:-.045em;white-space:nowrap}}
.sbar b{{font-size:46px;font-weight:900}}
</style>
<div class="a cafe"></div><div class="a fruit"></div>{spot}
<svg class="a" style="left:0;top:0" width="1080" height="660"><defs><filter id="g"><feGaussianBlur stdDeviation="6"/></filter></defs>
<line x1="620" y1="0" x2="460" y2="660" stroke="#FF8A1E" stroke-width="18" filter="url(#g)" opacity=".9"/>
<line x1="620" y1="0" x2="460" y2="660" stroke="#FFD2A1" stroke-width="5"/></svg>
<div class="a shade"></div>
<div class="a k" style="left:0;right:0;top:30px;display:flex;justify-content:center;align-items:center;gap:14px">
<span style="padding:12px 30px;border-radius:44px;background:rgba(28,28,28,.88);color:#eaeaea;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">기존 카페</span>
<svg width="74" height="52" viewBox="0 0 74 52" style="filter:drop-shadow(0 4px 8px rgba(0,0,0,.45))"><path d="M4 26 H56" stroke="#fff" stroke-width="9" stroke-linecap="round"/><path d="M42 8 L64 26 L42 44" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
<span style="padding:12px 34px;border-radius:44px;background:#FF8A1E;color:#2A1206;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">하복당</span></div>
<div class="a l1 k">카페 업종변경</div>
<div class="a l2 k"><span class="n">300만원</span><span class="b">부터?!</span></div>
<svg class="a brush" width="840" height="40" viewBox="0 0 840 40"><path d="M8 30 C 220 8, 560 4, 832 16" stroke="#FFB15C" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M90 36 C 320 22, 560 22, 780 30" stroke="#FF8A1E" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a sbar k"><span>배달로만 <b>8900만원</b> 매출 달성 + 2인 운영 가능 업종</span></div>'''


if __name__ == '__main__':
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k in RIGHT:
        hp = os.path.join(out, f'sw3_{k}.html'); open(hp, 'w').write(page(k))
        jobs.append({'html': hp, 'out': os.path.join(out, f'sw3_{k}.png'), 'width': 1080, 'height': 1080})
    jp = os.path.join(HERE, '_jobs_sw3.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    ims = []
    for j in jobs:
        im = Image.open(j['out']).convert('RGB'); im.save(j['out'][:-4] + '.jpg', quality=93); ims.append(im)
    sh = Image.new('RGB', (1110, 540), (28, 28, 28))
    for i, im in enumerate(ims):
        sh.paste(im.resize((540, 540)), (i * 570, 0))
    sh.save(os.path.join(HERE, '_sheet_sw3.jpg'), quality=90)


def page916(plain=False):
    """9:16 (1080x1920). Meta safe zone: key text within y 269-1248 and 65px from the sides;
    the bottom 35% holds imagery only (product photo)."""
    url, size, pos, fill = CUT, 'auto 900px', '-80px 0', '#FBF3EA'
    L, R, Hs = 640, 440, 900   # split line from (L,0) to (R,Hs)
    right_poly = f'polygon({L}px 0,1080px 0,1080px {Hs}px,{R}px {Hs}px)'
    return make_switch.BASE(1920) + f'''<style>
@font-face{{font-family:BHS;src:url('{BHS}')}}
body{{background:#120B07}}
.cafe{{left:0;top:0;width:1080px;height:{Hs}px;background:url('{CAFE}') -250px 0/auto {Hs}px no-repeat;
  filter:brightness(.72) saturate(.5) contrast(1.05);clip-path:polygon(0 0,{L}px 0,{R}px {Hs}px,0 {Hs}px)}}
.fruit{{left:0;top:0;width:1080px;height:{Hs}px;background:{fill} url('{url}') {pos}/{size} no-repeat;clip-path:{right_poly}}}
.sp{{left:0;top:0;width:1080px;height:{Hs}px;clip-path:{right_poly}}}
.shade{{left:0;top:0;width:1080px;height:1920px;background:linear-gradient(rgba(18,11,7,0) 0%,rgba(18,11,7,0) 36%,rgba(18,11,7,.75) 43%,#120B07 48%)}}
.glow{{left:90px;top:1300px;width:900px;height:620px;border-radius:50%;background:radial-gradient(ellipse,rgba(255,120,30,.45),rgba(255,120,30,0) 68%)}}
.bowl{{left:200px;top:1290px;width:680px;height:620px;background:url('{HERO}') -45px -184px/1300px auto no-repeat;
  -webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 52%,#000 66%,transparent 96%)}}
.l1{{left:0;right:0;top:800px;text-align:center;color:#fff;font-family:BHS;font-size:112px;letter-spacing:-.01em;line-height:1;text-shadow:0 6px 18px rgba(0,0,0,.6)}}
.l2{{left:0;right:0;top:934px;display:flex;justify-content:center;align-items:flex-end;gap:14px}}
.l2 .n{{font-family:BHS;font-size:180px;line-height:.92;color:#FF8A1E;letter-spacing:-.02em;transform:skewX(-8deg);text-shadow:0 8px 0 #6b2600}}
.l2 .b{{font-family:BHS;font-size:92px;line-height:1;color:#fff;margin-bottom:10px;transform:skewX(-8deg)}}
.brush{{left:150px;top:1112px}}
.sbar{{left:64px;right:64px;top:1150px;height:84px;background:#FF8A1E;transform:skewX(-12deg);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}}
.sbar span{{transform:skewX(12deg);font-size:35px;font-weight:900;font-style:italic;color:#2A1206;letter-spacing:-.045em;white-space:nowrap}}
.sbar b{{font-size:41px;font-weight:900}}
</style>
<div class="a cafe"></div><div class="a fruit"></div>
<div class="a sp" style="background:radial-gradient(ellipse 46% 60% at 74% 40%,rgba(255,200,140,0) 0%,rgba(255,128,30,.34) 50%,rgba(225,88,8,.86) 100%);mix-blend-mode:multiply"></div>
<div class="a" style="left:0;top:0;width:1080px;height:{Hs}px;clip-path:polygon(720px 0,900px 0,1080px 860px,560px 860px);
  background:linear-gradient(rgba(255,178,92,.55),rgba(255,150,60,.18) 70%,rgba(255,150,60,0));mix-blend-mode:screen;filter:blur(18px)"></div>
<div class="a sp" style="background:radial-gradient(ellipse 30% 40% at 77% 46%,rgba(255,190,110,.28),rgba(255,190,110,0) 70%);mix-blend-mode:screen"></div>
<svg class="a" style="left:0;top:0" width="1080" height="{Hs}"><defs><filter id="g"><feGaussianBlur stdDeviation="6"/></filter></defs>
<line x1="{L}" y1="0" x2="{R}" y2="{Hs}" stroke="#FF8A1E" stroke-width="18" filter="url(#g)" opacity=".9"/>
<line x1="{L}" y1="0" x2="{R}" y2="{Hs}" stroke="#FFD2A1" stroke-width="5"/></svg>
<div class="a shade"></div>
{'' if plain else '<div class="a glow"></div><div class="a bowl"></div>'}
<div class="a k" style="left:0;right:0;top:290px;display:flex;justify-content:center;align-items:center;gap:14px">
<span style="padding:12px 30px;border-radius:44px;background:rgba(28,28,28,.88);color:#eaeaea;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">기존 카페</span>
<svg width="74" height="52" viewBox="0 0 74 52" style="filter:drop-shadow(0 4px 8px rgba(0,0,0,.45))"><path d="M4 26 H56" stroke="#fff" stroke-width="9" stroke-linecap="round"/><path d="M42 8 L64 26 L42 44" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
<span style="padding:12px 34px;border-radius:44px;background:#FF8A1E;color:#2A1206;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">하복당</span></div>
<div class="a l1 k">카페 업종변경</div>
<div class="a l2 k"><span class="n">300만원</span><span class="b">부터?!</span></div>
<svg class="a brush" width="780" height="40" viewBox="0 0 840 40"><path d="M8 30 C 220 8, 560 4, 832 16" stroke="#FFB15C" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M90 36 C 320 22, 560 22, 780 30" stroke="#FF8A1E" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a sbar k"><span>배달로만 <b>8900만원</b> 매출 달성 + 2인 운영 가능 업종</span></div>'''


if __name__ == '__main__' and os.environ.get('SW916'):
    hp = os.path.join(HERE, 'out', 'sw3_b_916.html'); open(hp, 'w').write(page916())
    jp = os.path.join(HERE, '_jobs_sw3.json')
    json.dump([{'html': hp, 'out': os.path.join(HERE, 'out', 'sw3_b_916.png'), 'width': 1080, 'height': 1920}], open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    Image.open(os.path.join(HERE, 'out', 'sw3_b_916.png')).convert('RGB').save(os.path.join(HERE, 'out', '하복당_업종변경_9x16_실사_카페에서하복당_300만원.jpg'), quality=93)


def page169():
    """16:9 (1920x1080): the 1:1 design unchanged, photos widened to fill the frame."""
    url, size, pos, fill = make.u('assets/cutfruit_clean.jpg'), 'auto 820px', '827px -30px', '#FBF3EA'
    L, R, Hs, W = 1040, 880, 660, 1920
    rp = f'polygon({L}px 0,{W}px 0,{W}px {Hs}px,{R}px {Hs}px)'
    return make_switch.BASE(1080).replace('width:1080px;height:1080px', f'width:{W}px;height:1080px') + f'''<style>
@font-face{{font-family:BHS;src:url('{BHS}')}}
body{{background:#120B07}}
.cafe{{left:0;top:0;width:{W}px;height:{Hs}px;background:url('{CAFE}') 0 -20px/1050px auto no-repeat;
  filter:brightness(.72) saturate(.5) contrast(1.05);clip-path:polygon(0 0,{L}px 0,{R}px {Hs}px,0 {Hs}px)}}
.fruit{{left:0;top:0;width:{W}px;height:{Hs}px;background:{fill} url('{url}') {pos}/{size} no-repeat;clip-path:{rp}}}
.sp{{left:0;top:0;width:{W}px;height:{Hs}px;clip-path:{rp}}}
.shade{{left:0;top:0;width:{W}px;height:1080px;background:linear-gradient(rgba(18,11,7,0) 0%,rgba(18,11,7,0) 46%,rgba(18,11,7,.7) 56%,#120B07 64%)}}
.l1{{left:0;right:0;top:582px;text-align:center;color:#fff;font-family:BHS;font-size:112px;letter-spacing:-.01em;line-height:1;text-shadow:0 6px 18px rgba(0,0,0,.6)}}
.l2{{left:0;right:0;top:706px;display:flex;justify-content:center;align-items:flex-end;gap:14px}}
.l2 .n{{font-family:BHS;font-size:220px;line-height:.92;color:#FF8A1E;letter-spacing:-.02em;transform:skewX(-8deg);text-shadow:0 8px 0 #6b2600}}
.l2 .b{{font-family:BHS;font-size:112px;line-height:1;color:#fff;margin-bottom:12px;transform:skewX(-8deg)}}
.brush{{left:540px;top:918px}}
.sbar{{left:454px;right:454px;top:958px;height:88px;background:#FF8A1E;transform:skewX(-12deg);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}}
.sbar span{{transform:skewX(12deg);font-size:39px;font-weight:900;font-style:italic;color:#2A1206;letter-spacing:-.045em;white-space:nowrap}}
.sbar b{{font-size:46px;font-weight:900}}
</style>
<div class="a cafe"></div><div class="a fruit"></div>
<div class="a sp" style="background:radial-gradient(ellipse 40% 62% at 74% 40%,rgba(255,200,140,0) 0%,rgba(255,128,30,.34) 50%,rgba(225,88,8,.86) 100%);mix-blend-mode:multiply"></div>
<div class="a" style="left:0;top:0;width:{W}px;height:{Hs}px;clip-path:polygon(1240px 0,1520px 0,1820px 620px,1000px 620px);
  background:linear-gradient(rgba(255,178,92,.55),rgba(255,150,60,.18) 70%,rgba(255,150,60,0));mix-blend-mode:screen;filter:blur(18px)"></div>
<div class="a sp" style="background:radial-gradient(ellipse 22% 40% at 74% 46%,rgba(255,190,110,.28),rgba(255,190,110,0) 70%);mix-blend-mode:screen"></div>
<svg class="a" style="left:0;top:0" width="{W}" height="{Hs}"><defs><filter id="g"><feGaussianBlur stdDeviation="6"/></filter></defs>
<line x1="{L}" y1="0" x2="{R}" y2="{Hs}" stroke="#FF8A1E" stroke-width="18" filter="url(#g)" opacity=".9"/>
<line x1="{L}" y1="0" x2="{R}" y2="{Hs}" stroke="#FFD2A1" stroke-width="5"/></svg>
<div class="a shade"></div>
<div class="a k" style="left:0;right:0;top:30px;display:flex;justify-content:center;align-items:center;gap:14px">
<span style="padding:12px 30px;border-radius:44px;background:rgba(28,28,28,.88);color:#eaeaea;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">기존 카페</span>
<svg width="74" height="52" viewBox="0 0 74 52" style="filter:drop-shadow(0 4px 8px rgba(0,0,0,.45))"><path d="M4 26 H56" stroke="#fff" stroke-width="9" stroke-linecap="round"/><path d="M42 8 L64 26 L42 44" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
<span style="padding:12px 34px;border-radius:44px;background:#FF8A1E;color:#2A1206;font-size:36px;font-weight:900;letter-spacing:-.03em;box-shadow:0 6px 18px rgba(0,0,0,.35)">하복당</span></div>
<div class="a l1 k">카페 업종변경</div>
<div class="a l2 k"><span class="n">300만원</span><span class="b">부터?!</span></div>
<svg class="a brush" width="840" height="40" viewBox="0 0 840 40"><path d="M8 30 C 220 8, 560 4, 832 16" stroke="#FFB15C" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M90 36 C 320 22, 560 22, 780 30" stroke="#FF8A1E" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a sbar k"><span>배달로만 <b>8900만원</b> 매출 달성 + 2인 운영 가능 업종</span></div>'''


if __name__ == '__main__' and os.environ.get('SW169'):
    from PIL import Image
    for name, html, w, h in (('169', page169(), 1920, 1080), ('916plain', page916(plain=True), 1080, 1920)):
        hp = os.path.join(HERE, 'out', f'sw3_b_{name}.html'); open(hp, 'w').write(html)
        jp = os.path.join(HERE, '_jobs_sw3.json')
        json.dump([{'html': hp, 'out': os.path.join(HERE, 'out', f'sw3_b_{name}.png'), 'width': w, 'height': h}], open(jp, 'w'))
        subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
        Image.open(os.path.join(HERE, 'out', f'sw3_b_{name}.png')).convert('RGB').save(os.path.join(HERE, 'out', f'하복당_업종변경_{name}_실사_300만원.jpg'), quality=93)
