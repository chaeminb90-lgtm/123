"""하복당 업종변경 소재 2종 — 고객이 준 레퍼런스 2장의 레이아웃 구조를 하복당 내용으로 바꾼 버전.

S1 (1:1): 매장 간판 사진 위 + 어두운 그라데이션, "카페 업종변경 / 500만원부터?!", 사선 바, 각주
S2 (4:5): 흰 배경 작은 문구 + 큰 "업종변경", 매장 사진, 제품, 주황 밴드 문구 + 상담 필, 하단 조건 띠

Copy rules from the plan: 500만원 = 가맹비+교육비 only, exclusions (간판 포함) on the same image;
no distress framing ("포기하기 전", "폐업"), no unverified promos ("무료 진단", "10월 한정 혜택").

usage: python3 make_switch.py -> out/sw_1.jpg, out/sw_2.jpg, _sheet_sw.jpg
"""
import json, os, subprocess
import make

HERE = make.HERE
STORE = 'file:///home/user/123/site/img/storefront.jpg'
HERO = 'file:///home/user/123/site/img/hero_lineup.jpg'
def BASE(h):
    return make.HEAD.replace('html,body{width:1080px;height:1350px;overflow:hidden}', f'html,body{{width:1080px;height:{h}px;overflow:hidden}}')
BHS = make.u('fonts/BlackHanSans-Regular.ttf')

S1 = BASE(1080) + f'''<style>
@font-face{{font-family:BHS;src:url('{BHS}')}}
body{{background:#120B07}}
.store{{left:0;top:0;width:1080px;height:600px;background:url('{STORE}') -150px 0/1520px auto no-repeat}}
.shade{{left:0;top:0;width:1080px;height:1080px;background:linear-gradient(rgba(18,11,7,0) 0%,rgba(18,11,7,0) 26%,rgba(18,11,7,.55) 42%,#120B07 58%)}}
.l1{{left:0;right:0;top:500px;text-align:center;color:#fff;font-family:BHS;font-size:112px;letter-spacing:-.01em;line-height:1;text-shadow:0 6px 18px rgba(0,0,0,.5)}}
.l2{{left:0;right:0;top:628px;display:flex;justify-content:center;align-items:flex-end;gap:14px}}
.l2 .n{{font-family:BHS;font-size:220px;line-height:.92;color:#FF8A1E;letter-spacing:-.02em;transform:skewX(-8deg);text-shadow:0 8px 0 #6b2600}}
.l2 .b{{font-family:BHS;font-size:112px;line-height:1;color:#fff;margin-bottom:12px;transform:skewX(-8deg)}}
.brush{{left:120px;top:842px}}
.sbar{{left:58px;right:58px;top:886px;height:92px;background:#FF8A1E;transform:skewX(-12deg);display:flex;align-items:center;justify-content:center}}
.sbar span{{transform:skewX(12deg);font-size:46px;font-weight:900;font-style:italic;color:#2A1206;letter-spacing:-.04em}}
.fn1{{left:0;right:0;top:1000px;text-align:center;color:rgba(255,255,255,.88);font-size:25px;font-weight:600;letter-spacing:-.02em;line-height:1.4}}
</style>
<div class="a store"></div><div class="a shade"></div>
<div class="a l1 k">카페 업종변경</div>
<div class="a l2 k"><span class="n">500만원</span><span class="b">부터?!</span></div>
<svg class="a brush" width="840" height="40" viewBox="0 0 840 40"><path d="M8 30 C 220 8, 560 4, 832 16" stroke="#FFB15C" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M90 36 C 320 22, 560 22, 780 30" stroke="#FF8A1E" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a sbar k"><span>인테리어·집기, 본사가 정하지 않는 이유?</span></div>
<div class="a fn1 k">* 가맹비 300만원 + 교육비 200만원 기준 / 임대료·보증금·간판·인테리어·장비 비용 별도</div>'''

S2 = BASE(1350) + f'''<style>
body{{background:#fff;color:var(--ink)}}
.top{{left:0;right:0;top:46px;text-align:center;font-size:42px;font-weight:900;color:#C9500A;letter-spacing:-.04em}}
.big{{left:0;right:0;top:96px;text-align:center;font-size:262px;font-weight:900;color:var(--or);letter-spacing:-.06em;line-height:1}}
.band{{left:0;top:650px;width:1080px;height:596px;background:#EE6A16}}
.store{{left:110px;top:342px;width:860px;height:322px;background:url('{STORE}') 0 0/860px auto no-repeat;
  box-shadow:0 18px 30px rgba(80,30,0,.25)}}
.bowl{{left:270px;top:636px;width:540px;height:410px;background:url('{HERO}') 60px -126px/840px auto no-repeat;
  -webkit-mask-image:radial-gradient(ellipse 47% 50% at 50% 50%,#000 70%,transparent 96%)}}
.band{{background:linear-gradient(90deg,#F27A2C,#EE6A16 50%,#E45F0E)!important}}
.t1{{left:0;right:0;top:1044px;text-align:center;color:#fff;font-size:42px;font-weight:500;letter-spacing:-.04em}}
.t2{{left:0;right:0;top:1098px;text-align:center;color:#fff;font-size:50px;font-weight:900;letter-spacing:-.05em}}
.cpill{{left:0;right:0;top:1170px;display:flex;justify-content:center}}
.cpill span{{padding:10px 30px;background:#fff;color:var(--ink);font-size:36px;font-weight:600;letter-spacing:-.04em;border-radius:6px}}
.cpill b{{color:#C9500A;font-weight:900}}
.strip{{left:0;top:1246px;width:1080px;height:104px;background:#FFF4E8;text-align:center;padding-top:14px}}
.strip .o{{font-size:38px;font-weight:900;color:#C9500A;letter-spacing:-.04em}}
.strip .f{{margin-top:6px;font-size:22px;font-weight:600;color:#7a4a2a;letter-spacing:-.02em}}
</style>
<div class="a top k">간판 바꾸기 전에, 메뉴의 가능성을 확인하세요!</div>
<div class="a big k">업종변경</div>
<div class="a band"></div>
<div class="a store"></div>
<div class="a bowl"></div>
<div class="a t1 k">카페 다음 메뉴가 고민일 때,</div>
<div class="a t2 k">하복당 업종변경이라는 선택지가 있습니다.</div>
<div class="a cpill k"><span>전환 가능 여부, <b>상담에서 확인</b>해 드립니다!</span></div>
<div class="a strip k"><div class="o">가맹비 300 + 교육비 200만원 · 인테리어·집기 지정업체 없음</div>
<div class="f">임대료·보증금·간판·인테리어·장비 비용 별도</div></div>'''

if __name__ == '__main__':
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k, html, h in (('sw_1', S1, 1080), ('sw_2', S2, 1350)):
        hp = os.path.join(out, f'{k}.html'); open(hp, 'w').write(html)
        jobs.append({'html': hp, 'out': os.path.join(out, f'{k}.png'), 'width': 1080, 'height': h})
    jp = os.path.join(HERE, '_jobs_sw.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    ims = []
    for j in jobs:
        im = Image.open(j['out']).convert('RGB'); im.save(j['out'][:-4] + '.jpg', quality=93); ims.append(im)
    sh = Image.new('RGB', (432 + 432 + 12, 540), (28, 28, 28))
    sh.paste(ims[0].resize((432, 432)), (0, 54)); sh.paste(ims[1].resize((432, 540)), (444, 0))
    sh.save(os.path.join(HERE, '_sheet_sw.jpg'), quality=90)
