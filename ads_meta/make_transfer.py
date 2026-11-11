"""하복당 구의점 양도양수 소재 3종 (1:1). 사진: 고객이 준 사옥 사진(간판 오타 HKBOKDANG -> HABOKDANG 보정).

T1: 조건 (보증금 0 · 관리비 0 · 월세 150 · 권리금 1천) + 몸만 들어오세요
T2: 2026년 8~10월 매출·순이익률 막대그래프
T3: 1층 매장 / 2층 본사 슈퍼바이저 + 양도 이유 + 1년 계약 구조

usage: python3 make_transfer.py -> out/tr_1..3.jpg, _sheet_tr.jpg
"""
import json, os, subprocess
import make, make_switch

HERE = make.HERE
B = make.u('assets/guui_building.png')
LOGO_W = make.LOGO_W
H = make_switch.BASE(1080)

CSS = '''<style>
body{background:#1A0C05}
.k{letter-spacing:-.045em}
.pill{display:inline-block;padding:12px 28px;border-radius:50px;background:#FF8A1E;color:#fff;font-size:38px;font-weight:900;letter-spacing:-.04em;box-shadow:0 6px 18px rgba(0,0,0,.3)}
.tag{display:inline-block;padding:9px 22px;border-radius:50px;background:rgba(26,12,5,.82);color:#fff;font-size:30px;font-weight:800;letter-spacing:-.03em}
.o{color:#FF9A3C}
</style>'''

T1 = H + CSS + f'''<style>
.ph{{left:0;top:0;width:1080px;height:660px;background:url('{B}') 50% -110px/1080px auto no-repeat}}
.fade{{left:0;top:440px;width:1080px;height:230px;background:linear-gradient(rgba(26,12,5,0),#1A0C05 92%)}}
.chips{{left:36px;right:36px;top:800px;display:flex;gap:12px}}
.chip{{flex:1;height:156px;border-radius:20px;background:#2A1609;border:3px solid rgba(255,138,30,.55);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}}
.chip .l{{font-size:30px;font-weight:700;color:#FFCB97;letter-spacing:-.03em}}
.chip .v{{font-size:58px;font-weight:900;color:#fff;letter-spacing:-.05em;line-height:1.05}}
.chip .v.z{{color:#FF9A3C}}
</style>
<div class="a ph"></div><div class="a fade"></div>
<div class="a k" style="left:44px;top:40px"><span class="pill">하복당 구의점 양도양수</span></div>
<div class="a k" style="left:44px;top:120px"><span class="tag">본사 사옥 1층 · 운영 중인 매장</span></div>
<div class="a k" style="left:0;right:0;top:604px;text-align:center;font-size:104px;font-weight:900;line-height:1.1;text-shadow:0 4px 18px rgba(0,0,0,.5)"><span class="o">몸만</span> 들어오세요</div>
<div class="a k" style="left:0;right:0;top:728px;text-align:center;font-size:40px;font-weight:700;color:#FFE2C4">집기·장비 세팅 완료, 바로 운영 가능</div>
<div class="a chips k">
<div class="chip"><span class="l">보증금</span><span class="v z">0원</span></div>
<div class="chip"><span class="l">관리비</span><span class="v z">0원</span></div>
<div class="chip"><span class="l">월세</span><span class="v">150만원</span></div>
<div class="chip"><span class="l">권리금</span><span class="v">1천만원</span></div></div>
<img class="a" src="{LOGO_W}" style="left:498px;top:986px;width:84px">'''

MONTHS = (('8월', 4000, 18), ('9월', 4000, 15), ('10월', 3500, 19))
bars = ''
for i, (m, rev, pct) in enumerate(MONTHS):
    h = round(rev / 4000 * 392)
    x = 120 + i * 300
    profit = round(rev * pct / 100)
    bars += f'''<div class="a k" style="left:{x}px;top:{880 - h - 66}px;width:240px;text-align:center;font-size:46px;font-weight:900;color:#2A1206">{rev:,}만원</div>
<div class="a bar3 k" style="left:{x}px;top:{880 - h}px;width:240px;height:{h}px"><span class="pc">순이익률</span><span class="pv">{pct}%</span><span class="pp">순이익 {profit:,}만원</span></div>
<div class="a k" style="left:{x}px;top:894px;width:240px;text-align:center;font-size:40px;font-weight:800;color:#2A1206">{m}</div>'''

T2 = H + CSS + f'''<style>
body{{background:linear-gradient(170deg,#FFF6EC,#FFE6CC)}}
.bar3{{border-radius:22px 22px 6px 6px;background:linear-gradient(#FF9A3C,#F06A0F);display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:34px;box-shadow:0 12px 24px rgba(160,60,0,.22)}}
.bar3 .pc{{font-size:30px;font-weight:700;color:#FFF1E2;letter-spacing:-.03em}}
.bar3 .pv{{font-size:84px;font-weight:900;color:#fff;letter-spacing:-.05em;line-height:1.05}}
.bar3 .pp{{margin-top:10px;padding:6px 14px;border-radius:30px;background:rgba(42,18,6,.28);font-size:27px;font-weight:800;color:#fff;letter-spacing:-.04em}}
.base{{left:90px;right:90px;top:880px;height:4px;background:#2A1206;border-radius:4px}}
.band{{left:0;top:968px;width:1080px;height:112px;background:#1A0C05;display:flex;align-items:center;justify-content:center;gap:18px}}
</style>
<div class="a k" style="left:60px;top:46px"><span class="pill">하복당 구의점 양도양수</span></div>
<div class="a k" style="left:60px;top:136px;font-size:88px;font-weight:900;color:#2A1206;line-height:1.12">매출이 증명된<br>직영점, <span style="color:#F06A0F">그대로 인수</span></div>
<div class="a k" style="left:62px;top:352px;font-size:34px;font-weight:700;color:#7A3E14">구의점 2026년 8~10월 월 매출 · 순이익률</div>
<div class="a base"></div>
{bars}
<div class="a band k"><span style="font-size:36px;font-weight:800;color:#fff">보증금 <b class="o">0원</b> · 관리비 <b class="o">0원</b> · 월세 150만원 · 권리금 1천만원</span></div>'''

T3 = H + CSS + f'''<style>
.ph{{background:url('{B}') 50% 0/1080px auto no-repeat}}
.top{{left:0;top:0;width:1080px;height:330px;background:linear-gradient(rgba(26,12,5,.9) 0%,rgba(26,12,5,.75) 55%,rgba(26,12,5,0) 100%)}}
.bot{{left:0;top:640px;width:1080px;height:440px;background:linear-gradient(rgba(26,12,5,0) 0%,rgba(26,12,5,.88) 30%,#1A0C05 52%)}}
.call{{display:flex;align-items:center;gap:0}}
.call .dot{{width:22px;height:22px;border-radius:50%;background:#FF8A1E;border:5px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.4)}}
.call .ln{{width:46px;height:4px;background:#fff}}
.call .bx{{padding:10px 20px;border-radius:12px;background:rgba(26,12,5,.86);font-size:30px;font-weight:800;color:#fff;letter-spacing:-.04em;line-height:1.25}}
.call .bx b{{color:#FF9A3C}}
.row{{left:52px;right:52px;display:flex;align-items:center;gap:20px;padding:16px 26px;border-radius:18px;background:rgba(255,255,255,.07);border:2px solid rgba(255,138,30,.45)}}
.row .n{{flex:none;width:58px;height:58px;border-radius:50%;background:#FF8A1E;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:900;color:#fff}}
.row .t{{font-size:38px;font-weight:800;color:#fff;letter-spacing:-.045em;line-height:1.2}}
</style>
<div class="a ph" style="left:0;top:0;width:1080px;height:1080px"></div><div class="a top"></div><div class="a bot"></div>
<div class="a k" style="left:52px;top:44px"><span class="pill">하복당 구의점 양도양수</span></div>
<div class="a k" style="left:52px;top:128px;font-size:62px;font-weight:900;line-height:1.18;text-shadow:0 3px 12px rgba(0,0,0,.4)">브랜드가 커져서,<br><span class="o">직영점을 넘깁니다</span></div>
<div class="a call k" style="left:436px;top:452px"><span class="dot"></span><span class="ln"></span><span class="bx"><b>2층</b> 하복당 본사 슈퍼바이저 상주</span></div>
<div class="a call k" style="left:560px;top:586px"><span class="dot"></span><span class="ln"></span><span class="bx"><b>1층</b> 하복당 구의점 (양도 매장)</span></div>
<div class="a row k" style="top:800px"><span class="n">1</span><span class="t">1년 계약 · 1년간 운영 수익 <span class="o">100% 양수인 몫</span></span></div>
<div class="a row k" style="top:920px"><span class="n">2</span><span class="t">계약 종료 후 <span class="o">하복당 브랜드 사용권</span> 제공</span></div>'''

if __name__ == '__main__':
    from PIL import Image
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k, html in (('1', T1), ('2', T2), ('3', T3)):
        hp = os.path.join(out, f'tr_{k}.html'); open(hp, 'w').write(html)
        jobs.append({'html': hp, 'out': os.path.join(out, f'tr_{k}.png'), 'width': 1080, 'height': 1080})
    jp = os.path.join(HERE, '_jobs_tr.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    ims = []
    for j in jobs:
        im = Image.open(j['out']).convert('RGB'); im.save(j['out'][:-4] + '.jpg', quality=93); ims.append(im)
    sh = Image.new('RGB', (3 * 540 + 24, 540), (28, 28, 28))
    for i, im in enumerate(ims):
        sh.paste(im.resize((540, 540)), (i * 552, 0))
    sh.save(os.path.join(HERE, '_sheet_tr.jpg'), quality=90)
