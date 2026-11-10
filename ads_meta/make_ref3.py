"""하복당 1:1 소재 3종 — 고객이 준 레퍼런스 3장(우지커피 2장, 일품양평해장국)의 레이아웃 구조를
하복당 실사진과 고객이 정한 문구로 바꾼 버전. 경쟁사 문구·로고는 쓰지 않는다.

R1: 매장 사진 배경 + 우상단 로고 + "아직 블루오션 과일카페 창업 / 하복당이 기회!" + 박스 문구 + 하단 상담 버튼 바
R2: 위쪽 매장 간판 사진 + 아래 어두운 그라데이션 + 2줄 숫자 헤드라인 + 각주 + 하단 로고
R3: 어두운 사진 배경 + 상단 필 + 빨간 박스 강조 3줄 헤드라인 + 각주 + 우하단 로고

usage: python3 make_ref3.py -> out/ref3_1.jpg .. out/ref3_3.jpg
"""
import json, os, subprocess
import make, make_switch

HERE = make.HERE
STORE_UP = os.path.join(HERE, 'assets', 'storefront_up.jpg')
STORE = make.u('assets/storefront_up.jpg') if os.path.exists(STORE_UP) else 'file:///home/user/123/site/img/storefront.jpg'
HERO = 'file:///home/user/123/site/img/hero_lineup.jpg'
DELIV = make.u('plates/delivery_a.png') if os.path.exists(os.path.join(HERE, 'plates', 'delivery_a.png')) else 'file:///home/user/123/site/img/line_delivery.jpg'
LOGO_W = make.LOGO_W
NOTE = '*운영 방식·상권에 따라 매장별 차이가 있을 수 있음'

CSS = '''<style>
body{background:#140A05}
.ph{left:0;top:0;width:1080px;height:1080px}
.t{left:0;right:0;text-align:center;color:#fff;font-weight:900;letter-spacing:-.045em;line-height:1.15;text-shadow:0 4px 18px rgba(0,0,0,.55)}
.fn{color:rgba(255,255,255,.85);font-size:19px;font-weight:600;letter-spacing:-.02em;line-height:1.5;text-shadow:0 2px 6px rgba(0,0,0,.6)}
</style>'''

# ---------------------------------------------------------------- 1. 하복당이 기회
R1 = make_switch.BASE(1080) + CSS + f'''<style>
.bg1{{background:url('{HERO}') 50% 60%/auto 1180px no-repeat;filter:saturate(1.05)}}
.dim1{{background:linear-gradient(rgba(30,12,4,.82) 0%,rgba(30,12,4,.62) 38%,rgba(30,12,4,.2) 62%,rgba(30,12,4,.55) 100%)}}
.blue{{display:inline-block;padding:0 22px 8px;border-radius:16px;background:linear-gradient(135deg,#3AA0FF,#1556E0);color:#fff;box-shadow:0 6px 0 #0B3A9E,0 10px 26px rgba(20,90,255,.45)}}
.box{{display:inline-block;padding:6px 18px 10px;margin:0 4px;border-radius:10px;background:#fff;color:#2A1206;font-size:52px;font-weight:900;letter-spacing:-.04em;line-height:1.15}}
.box.o{{background:#FF8A1E;color:#fff}}
.cbar{{left:0;right:0;top:984px;height:96px;background:#1E0D05;display:flex;align-items:center;justify-content:center;gap:16px}}
.cbar span{{font-size:46px;font-weight:900;letter-spacing:-.045em;color:#fff}}
.cbar b{{color:#FF9A3C}}
</style>
<div class="a ph bg1"></div><div class="a ph dim1"></div>
<img class="a" src="{LOGO_W}" style="right:44px;top:34px;width:92px">
<div class="a t k" style="top:96px;font-size:70px;font-weight:900;line-height:1.3">아직 <span class="blue">블루오션</span> <span style="color:#FFB15C">과일카페 창업</span></div>
<div class="a t k" style="top:206px;font-size:132px">하복당이 <span style="color:#FF9A3C">기회!</span></div>
<div class="a k" style="left:0;right:0;top:384px;text-align:center"><span class="box" style="font-size:62px">보증금 포함 총 창업비</span><span class="box o" style="font-size:62px">2500만원</span></div>
<div class="a cbar k"><span>하복당 <b>30초 창업상담</b> 바로가기</span>
<svg width="34" height="34" viewBox="0 0 34 34"><path d="M8 4 L28 17 L8 30 Z" fill="#fff"/></svg></div>'''

# ---------------------------------------------------------------- 2. 월세 80만원 매장 월매출 8200만원
R2 = make_switch.BASE(1080) + CSS + f'''<style>
.bg2{{left:0;top:0;width:1080px;height:660px;background:url('{STORE}') -220px 0/auto 660px no-repeat}}
.dim2{{background:linear-gradient(rgba(20,10,5,0) 0%,rgba(20,10,5,0) 44%,rgba(20,10,5,.78) 58%,#1A0C05 66%)}}
.y{{color:#FFB13C}}
</style>
<div class="a bg2"></div><div class="a ph dim2"></div>
<div class="a t k" style="top:690px;font-size:60px">보증금 1000만원 · 월세 80만원 매장에서</div>
<div class="a t k" style="top:776px;font-size:118px">월매출 <span class="y">8200만원?</span></div>
<img class="a" src="{LOGO_W}" style="left:494px;top:968px;width:92px">'''

# ---------------------------------------------------------------- 3. 월세 60만원 공실에서 월매출 5300만원
R3 = make_switch.BASE(1080) + CSS + f'''<style>
.bg3{{background:url('{DELIV}') 50% 60%/1260px auto no-repeat}}
.dim3{{background:linear-gradient(rgba(16,8,4,.86) 0%,rgba(16,8,4,.72) 45%,rgba(16,8,4,.35) 75%,rgba(16,8,4,.6) 100%)}}
.pill{{display:inline-block;padding:12px 30px;border-radius:44px;background:#E2361B;color:#fff;font-size:34px;font-weight:800;letter-spacing:-.03em}}
.hl{{left:64px;color:#fff;font-weight:900;letter-spacing:-.05em;line-height:1.05;font-size:96px;text-shadow:0 4px 18px rgba(0,0,0,.5)}}
.hl .r{{display:inline-block;padding:2px 16px 8px;background:#E2361B;color:#fff}}
</style>
<div class="a ph bg3"></div><div class="a ph dim3"></div>
<div class="a k" style="left:64px;top:56px"><span class="pill">과일디저트 전문점 하복당</span></div>
<div class="a hl k" style="top:160px">월세 60만원</div>
<div class="a hl k" style="top:280px"><span class="r">공실</span>에서</div>
<div class="a hl k" style="top:400px"><span class="r">월매출 5300만원</span> 달성</div>
<img class="a" src="{LOGO_W}" style="right:48px;top:950px;width:92px">'''


if __name__ == '__main__':
    from PIL import Image
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k, html in (('1', R1), ('2', R2), ('3', R3)):
        hp = os.path.join(out, f'ref3_{k}.html'); open(hp, 'w').write(html)
        jobs.append({'html': hp, 'out': os.path.join(out, f'ref3_{k}.png'), 'width': 1080, 'height': 1080})
    jp = os.path.join(HERE, '_jobs_ref3.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    ims = []
    for j in jobs:
        im = Image.open(j['out']).convert('RGB'); im.save(j['out'][:-4] + '.jpg', quality=93); ims.append(im)
    sh = Image.new('RGB', (3 * 540 + 24, 540), (28, 28, 28))
    for i, im in enumerate(ims):
        sh.paste(im.resize((540, 540)), (i * 552, 0))
    sh.save(os.path.join(HERE, '_sheet_ref3.jpg'), quality=90)
