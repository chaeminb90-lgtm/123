"""하복당 1:1 가맹모집 소재 2종 — 고객이 준 레퍼런스 2장의 레이아웃 구조를 하복당 내용으로 바꾼 버전.

R1: 밝은 배경 + 상단 로고 + 질문 필 + 2줄 헤드라인(브랜드명 박스 강조) + 좌측 카드 2개 + 우하단 제품 + 하단 CTA 바
R2: 어두운 배경 + 큰 숫자 훅과 기준 태그 + 따옴표 강조 헤드라인 + 중앙 제품 + 불릿 2줄 + 하단 브랜드 바

Copy follows the plan's rules (no unverified claims such as 1인 운영 / 초보 가능 / 매출 수치;
cost exclusions and sources on the same image).

usage: python3 make_sq.py -> out/sq_r1.jpg, out/sq_r2.jpg
"""
import json, os, subprocess
import make

HERE = make.HERE
HERO = 'file:///home/user/123/site/img/hero_lineup.jpg'
HEAD = make.HEAD.replace('html,body{{width:1080px;height:1350px;overflow:hidden}}'.replace('{{', '{').replace('}}', '}'),
                         'html,body{width:1080px;height:1080px;overflow:hidden}')

R1 = HEAD + f'''<style>
body{{background:linear-gradient(160deg,#FFF6EA 0%,#FFE9D2 55%,#FFD9B5 100%);color:var(--ink)}}
.bgblur{{left:-60px;top:380px;width:760px;height:640px;background:url('{HERO}') 10% 60%/1100px auto;filter:blur(18px) saturate(.9);opacity:.28;
  -webkit-mask-image:radial-gradient(ellipse at 40% 55%,#000 30%,transparent 72%)}}
.photo{{left:510px;top:500px;width:600px;height:480px;background:url('{HERO}') 0 -150px/1000px auto no-repeat;
  -webkit-mask-image:radial-gradient(ellipse 62% 78% at 50% 58%,#000 58%,transparent 84%)}}
.lg{{left:0;right:0;top:44px;display:flex;justify-content:center}}
.lg img{{width:96px}}
.q{{left:0;right:0;top:186px;display:flex;justify-content:center}}
.q span{{padding:12px 36px;border-radius:44px;background:var(--or);color:#fff;font-size:36px;font-weight:800;letter-spacing:-.03em}}
.h1{{left:0;right:0;top:270px;text-align:center;font-size:54px;font-weight:800;letter-spacing:-.04em}}
.h1 b{{font-weight:900;color:var(--or)}}
.h2{{left:0;right:0;top:342px;text-align:center;font-size:96px;font-weight:900;letter-spacing:-.05em;line-height:1.15}}
.h2 span{{display:inline-block;padding:0 22px 4px;margin-right:16px;background:#fff;color:var(--or);border-radius:16px;box-shadow:0 8px 0 var(--or)}}
.fnx{{left:0;right:0;top:478px;text-align:center;font-size:23px;font-weight:700;color:#7a4a2a}}
.cardw{{left:44px;width:410px;padding:26px 24px;border-radius:24px;background:rgba(255,255,255,.96);border:4px solid var(--or);
  text-align:center;box-shadow:0 10px 24px rgba(120,50,0,.14)}}
.cardw .t{{font-size:36px;font-weight:700;letter-spacing:-.04em;line-height:1.3}}
.cardw .b{{margin-top:6px;font-size:40px;font-weight:900;letter-spacing:-.045em;color:var(--or);line-height:1.25}}
.cta{{left:0;right:0;top:980px;height:100px;background:#FFF1DC;display:flex;align-items:center;justify-content:center;gap:22px;
  font-size:44px;font-weight:900;color:var(--or);letter-spacing:-.04em;border-top:2px solid rgba(240,106,15,.25)}}
</style>
<div class="a bgblur"></div><div class="a photo"></div>
<div class="a lg"><img src="{make.LOGO_O}"></div>
<div class="a q k"><span>창업 비용, 얼마부터 필요할까?</span></div>
<div class="a h1 k">가맹비·교육비 <b>500만원</b>으로 시작하는</div>
<div class="a h2 k"><span>하복당</span>이 답이다!</div>
<div class="a fnx k">임대료·보증금·인테리어·장비 비용 별도</div>
<div class="a cardw k" style="top:560px"><div class="t">인테리어·집기</div><div class="b">지정업체 없이 자율공사</div></div>
<div class="a cardw k" style="top:768px"><div class="t">과일은 본사 공급</div><div class="b">경매 원가 전표 공개</div></div>
<div class="a cta k">가맹 상담 신청하기 <span style="font-size:40px;letter-spacing:-.1em">&gt;&gt;</span></div>'''

R2 = HEAD + f'''<style>
body{{background:radial-gradient(ellipse 70% 60% at 50% 58%,#7A2E06 0%,#3A1504 55%,#1A0A03 100%)}}
.glow{{left:140px;top:360px;width:800px;height:560px;border-radius:50%;background:radial-gradient(ellipse,rgba(255,120,30,.55),rgba(255,120,30,0) 70%);filter:blur(10px)}}
.photo{{left:150px;top:330px;width:780px;height:600px;background:url('{HERO}') 6% 72%/1000px auto;
  -webkit-mask-image:radial-gradient(ellipse 50% 50% at 46% 58%,#000 55%,transparent 100%)}}
.hook{{left:56px;top:40px;display:flex;align-items:center;gap:20px}}
.hook .n{{font-family:BHS2,PT;font-size:132px;font-weight:900;color:#FF5A1F;letter-spacing:-.04em;transform:skewX(-9deg);
  text-shadow:0 6px 0 #6b1a00,0 0 30px rgba(255,90,31,.35)}}
.hook .tag{{padding:10px 16px;border-radius:8px;background:#E23B0E;color:#fff;font-size:24px;font-weight:800;line-height:1.3;letter-spacing:-.03em}}
.hl1{{left:0;right:0;top:206px;text-align:center;color:#fff;font-size:64px;font-weight:800;letter-spacing:-.04em;line-height:1.25}}
.hl1 em{{font-style:normal;color:#FFB46B;font-weight:900}}
.brush{{left:330px;top:340px}}
.bul{{left:60px;right:60px;top:820px;color:#fff;font-size:33px;font-weight:700;letter-spacing:-.035em;line-height:1.6;text-shadow:0 2px 8px rgba(0,0,0,.6)}}
.fnd{{left:60px;right:60px;top:946px;color:rgba(255,255,255,.82);font-size:19px;font-weight:600;letter-spacing:-.02em}}
.bbar{{left:0;right:0;top:988px;height:92px;background:#C9430A;display:flex;align-items:center;justify-content:center;gap:22px}}
.bbar img{{height:62px}}
.bbar span{{color:#fff;font-size:34px;font-weight:900;letter-spacing:-.04em}}
</style>
<style>@font-face{{font-family:BHS2;src:url('{make.u("fonts/BlackHanSans-Regular.ttf") if os.path.exists(os.path.join(HERE, "fonts/BlackHanSans-Regular.ttf")) else ""}')}}</style>
<div class="a glow"></div><div class="a photo"></div>
<div class="a hook k"><div class="n">가맹점 20곳!</div><div class="tag">서울·경기 계약·오픈<br>2026.6 본사 발표</div></div>
<div class="a hl1 k">경매 원가가 보이면<br>“<em>수익 계산</em>”이 달라집니다</div>
<svg class="a brush" width="440" height="34" viewBox="0 0 440 34"><path d="M6 22 C 120 8, 300 6, 434 16" stroke="#FF5A1F" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M40 28 C 170 18, 300 18, 410 24" stroke="#FFB46B" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
<div class="a bul k">· 과일은 가락시장 경매 원가 전표를 공개합니다.<br>· 인테리어·집기는 지정업체 없이 점주가 고릅니다.</div>
<div class="a fnd k">20곳: 2026년 6월 본사 발표(이넷뉴스 보도) 기준 · 매장·상권별로 차이가 있으며 수익을 보장하지 않습니다</div>
<div class="a bbar k"><img src="{make.LOGO_W}"><span>가맹점 모집</span></div>'''

if __name__ == '__main__':
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    jobs = []
    for k, html in (('sq_r1', R1), ('sq_r2', R2)):
        hp = os.path.join(out, f'{k}.html'); open(hp, 'w').write(html)
        jobs.append({'html': hp, 'out': os.path.join(out, f'{k}.png'), 'width': 1080, 'height': 1080})
    jp = os.path.join(HERE, '_jobs_sq.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    ims = []
    for j in jobs:
        im = Image.open(j['out']).convert('RGB'); im.save(j['out'][:-4] + '.jpg', quality=93); ims.append(im)
    sh = Image.new('RGB', (2 * 540 + 12, 540), (28, 28, 28))
    for i, im in enumerate(ims):
        sh.paste(im.resize((540, 540)), (i * 552, 0))
    sh.save(os.path.join(HERE, '_sheet_sq.jpg'), quality=90)
