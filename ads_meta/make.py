"""하복당 가맹모집 메타광고 시안 15종 (주제 5 x 3, 1080x1350).

Style follows the brand reference posts: orange or cream studio backdrop, product photo, logo top-left,
bold two-line Korean headline, white pills, wavy round sticker, small footnote for every number.
Copy follows the 기획안 (Claude Docs): no "차액가맹금 0원", no "본사가 남기는 게 없음", no "업계 유일",
sources and disclaimers on the same screen as the numbers, no second-person assumptions.

usage: python3 make.py [ids...]   -> out/<id>.png + out/<id>.jpg, _boxes.json, _sheet.jpg
"""
import json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
def u(p): return 'file://' + os.path.join(HERE, p)

PLATE = lambda n: u(f'plates/{n}.png')
CUP3D = u('assets/cup3d.png')
LOGO_W = u('assets/logo_w.png'); LOGO_O = u('assets/logo_o.png')

HEAD = f'''<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:PT;src:url('{u("fonts/PretendardVariable.ttf")}');font-weight:100 950}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{font-family:PT,sans-serif;position:relative;word-break:keep-all;color:#fff;-webkit-font-smoothing:antialiased}}
.a{{position:absolute}}
:root{{--or:#F06A0F;--deep:#C9500A;--ink:#3A1705;--cream:#FFF6EC;--pale:#FFE7CF}}
.plate{{left:0;top:0;width:1080px;height:1350px}}
.logo{{left:64px;top:56px;width:112px}}
.logo img{{width:100%;display:block}}
.toppill{{left:200px;top:80px;padding:10px 24px;border-radius:40px;background:#fff;color:var(--or);font-size:27px;font-weight:800;letter-spacing:-.02em;line-height:1.2}}
.toppill.o{{background:var(--or);color:#fff}}
.kicker{{left:64px;font-size:29px;font-weight:700;letter-spacing:.12em;line-height:1}}
.small{{left:64px;font-size:42px;font-weight:800;letter-spacing:-.03em;line-height:1.2}}
.hl{{left:60px;font-weight:900;letter-spacing:-.045em;line-height:1.1}}
.hl em{{font-style:normal;color:#fff;background:linear-gradient(transparent 74%,rgba(255,226,196,.42) 74%)}}
.ink{{color:var(--ink)}} .orc{{color:var(--or)}}
.divider{{left:64px;display:flex;align-items:center;gap:14px}}
.divider i{{display:block;width:110px;height:8px;border-radius:8px;background:currentColor}}
.divider b{{display:block;width:12px;height:12px;border-radius:50%;background:currentColor}}
.bar{{left:64px;width:96px;height:10px;border-radius:10px;background:var(--or)}}
.pill{{padding:12px 28px;border-radius:44px;background:#fff;color:var(--ink);font-size:30px;font-weight:800;letter-spacing:-.03em;line-height:1.2;white-space:nowrap;
  box-shadow:0 6px 16px rgba(90,30,0,.18)}}
.pill b{{color:var(--or);font-weight:900}}
.pill.o{{background:var(--or);color:#fff;box-shadow:0 6px 16px rgba(90,30,0,.22)}}
.fn{{font-size:21px;font-weight:600;letter-spacing:-.02em;line-height:1.45}}
.fnbox{{padding:10px 20px;border-radius:14px;background:#B4480A;color:#fff}}
.card{{background:#fff;border-radius:30px;box-shadow:0 14px 36px rgba(90,30,0,.16);color:var(--ink)}}
.st{{display:flex;align-items:center;justify-content:center;text-align:center}}
.st svg{{position:absolute;inset:0;filter:drop-shadow(0 8px 12px rgba(90,30,0,.25))}}
.st span{{position:relative;font-weight:900;color:var(--or);letter-spacing:-.04em;line-height:1.12}}
</style>'''


def sticker(x, y, size, text, fs=None, rot=-8, fill='#fff', color=None):
    """wavy round sticker (scalloped circle) like the reference posts"""
    n, pts = 14, []
    for i in range(361):
        t = math.radians(i)
        r = 46 + 3.2 * math.cos(n * t)
        pts.append(f'{50 + r * math.cos(t):.2f},{50 + r * math.sin(t):.2f}')
    fs = fs or int(size * 0.2)
    col = f'color:{color};' if color else ''
    return (f'<div class="a st k" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;transform:rotate({rot}deg)">'
            f'<svg viewBox="0 0 100 100" width="{size}" height="{size}"><polygon points="{" ".join(pts)}" fill="{fill}"/></svg>'
            f'<span style="font-size:{fs}px;{col}">{text}</span></div>')


def sparkle(x, y, s=34, c='#FFE7CF'):
    return (f'<svg class="a" style="left:{x}px;top:{y}px" width="{s}" height="{s}" viewBox="0 0 40 40">'
            f'<path d="M20 0 C21.5 13 27 18.5 40 20 C27 21.5 21.5 27 20 40 C18.5 27 13 21.5 0 20 C13 18.5 18.5 13 20 0Z" fill="{c}"/></svg>')


def divider(y, color='#fff'):
    return f'<div class="a divider" style="top:{y}px;color:{color}"><i></i><b></b><b></b><b></b></div>'


def logo(white=True, pill=None, pill_o=False):
    s = f'<div class="a logo"><img src="{LOGO_W if white else LOGO_O}"></div>'
    if pill:
        s += f'<div class="a toppill k{" o" if pill_o else ""}">{pill}</div>'
    return s


def pill(x, y, html, cls='', fs=None, right=False):
    pos = f'right:{1080 - x}px' if right else f'left:{x}px'
    f = f'font-size:{fs}px;' if fs else ''
    return f'<div class="a pill k {cls}" style="{pos};top:{y}px;{f}">{html}</div>'


def stage(cx, top, cup_w=420, ped_w=400, floor='checker', floor_y=1080, bg=None):
    """cup3d on an orange pedestal, with a checker (or plain orange) floor"""
    ped_h, ell = 150, 74
    px = cx - ped_w // 2
    if floor == 'checker':
        fl = (f'<div class="a" style="left:0;top:{floor_y}px;width:1080px;height:{1350 - floor_y}px;overflow:hidden">'
              f'<div style="position:absolute;left:-760px;top:0;width:2600px;height:1100px;transform-origin:50% 0;'
              f'transform:perspective(520px) rotateX(64deg);background:conic-gradient(#F58B42 25%,#FFF0E2 0 50%,#F58B42 0 75%,#FFF0E2 0) 0 0/110px 110px"></div>'
              f'<div style="position:absolute;inset:0;background:linear-gradient(rgba(240,106,15,.35),rgba(240,106,15,0) 40%)"></div></div>')
    else:
        fl = (f'<div class="a" style="left:0;top:{floor_y}px;width:1080px;height:{1350 - floor_y}px;'
              f'background:linear-gradient(#F37320,#E8630F)"></div>')
    shadow = (f'<div class="a" style="left:{px - 40}px;top:{top + ped_h + ell // 2 - 30}px;width:{ped_w + 80}px;height:70px;border-radius:50%;'
              f'background:radial-gradient(ellipse,rgba(110,40,0,.38),rgba(110,40,0,0) 70%)"></div>')
    body = (f'<div class="a" style="left:{px}px;top:{top + ell // 2}px;width:{ped_w}px;height:{ped_h}px;border-radius:0 0 {ped_w // 2}px {ped_w // 2}px / 0 0 {ell // 2}px {ell // 2}px;'
            f'background:linear-gradient(90deg,#C94A05,#EE6E1C 22%,#FF8C42 48%,#F57422 70%,#C24604)"></div>')
    topc = (f'<div class="a" style="left:{px}px;top:{top}px;width:{ped_w}px;height:{ell}px;border-radius:50%;'
            f'background:radial-gradient(ellipse at 45% 40%,#FFA466,#F7802F 70%,#EC6E1E)"></div>')
    cup_h = int(cup_w * 913 / 869)
    cup = (f'<img class="a" src="{CUP3D}" style="left:{cx - cup_w // 2}px;top:{top + ell // 2 - cup_h + 22}px;width:{cup_w}px;'
           f'filter:drop-shadow(0 24px 22px rgba(90,30,0,.32))">')
    return fl + shadow + body + topc + cup


def page(body, bg='#F06A0F', plate=None):
    pl = f'<img class="a plate" src="{PLATE(plate)}">' if plate else ''
    return HEAD + f'<style>body{{background:{bg}}}</style>' + pl + body


FN500 = '창업비 500만원 = 가맹비 300만원 + 교육비 200만원 기준 · 임대료·보증금·인테리어·장비 비용 별도'
SRC_FTC = '출처: 공정거래위원회 2025년도 가맹사업 현황(2026.4 발표, 2024년 말 정보공개서 기준)'
BOX = '박스당 1,000원은 과일 공급 기준'
NOGUAR = '매장·상권별로 차이가 있으며 수익을 보장하지 않습니다'

ADS = {}
FN500_2 = '창업비 500만원 = 가맹비 300만원 + 교육비 200만원 기준<br>임대료·보증금·인테리어·장비 비용 별도'
BOXFIX = '박스당 1,000원은 하복당 과일 공급 기준 본사 몫(고정 금액)'


def fnbox(html, top, left=40, right=40, extra=''):
    return f'<div class="a fn fnbox k" style="left:{left}px;right:{right}px;top:{top}px;text-align:center;{extra}">{html}</div>'


def checklist(items, top, width, qfs=32, afs=27, gap=22):
    rows = ''.join(f'''<div style="display:flex;gap:18px;align-items:flex-start">
        <div style="flex:none;width:52px;height:52px;border-radius:50%;background:var(--or);color:#fff;font-size:28px;font-weight:900;display:flex;align-items:center;justify-content:center">{i}</div>
        <div><div style="font-size:{qfs}px;font-weight:800;letter-spacing:-.035em;line-height:1.25">{q}</div>
        <div style="margin-top:6px;font-size:{afs}px;font-weight:800;letter-spacing:-.03em;color:#C9500A">→ {a}</div></div></div>'''
                   for i, (q, a) in enumerate(items, 1))
    return (f'<div class="a k" style="left:64px;top:{top}px;width:{width}px;color:var(--ink);'
            f'display:flex;flex-direction:column;gap:{gap}px">{rows}</div>')


def circle(inner, cx=534, cy=922, r=150):
    return (f'<div class="a k st" style="left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:#FFF4E6;box-shadow:0 10px 30px rgba(90,30,0,.25);flex-direction:column;color:var(--ink)">'
            f'<img src="{LOGO_O}" style="width:56px;margin-bottom:10px">{inner}</div>')


CREAM = 'linear-gradient(#FFF8F0,#FBEBDD 80%)'

# ============================================================== 1. 신규창업
ADS['1-1'] = ('신규창업', '계약 전에 이것부터 물어보세요', page(
    logo(False)
    + '<div class="a small k ink" style="top:214px">첫 창업, 계약 전에</div>'
    + '<div class="a hl k orc" style="top:270px;font-size:116px">이것부터<br>물어보세요</div>'
    + '<div class="a bar" style="top:552px"></div>'
    + checklist([('창업비에 뭐가 포함되나요?', '가맹비 300 + 교육비 200만원'),
                 ('인테리어 업체를 정해 주나요?', '지정업체 없이 점주 자율공사'),
                 ('과일 공급가는 어떻게 정하나요?', '경매 원가 전표 + 본사 몫 공개')], 592, 660)
    + sticker(822, 214, 190, '첫 창업<br>체크리스트', fs=34, rot=8)
    + '<div class="a fn k ink" style="left:64px;top:900px;width:520px;font-size:21px;font-weight:700;opacity:.82">'
      '창업비 500만원 = 가맹비 300만원 + 교육비 200만원 기준<br>임대료·보증금·인테리어·장비 비용 별도</div>',
    bg=CREAM, plate='pavlova_b'))

ADS['1-2'] = ('신규창업', '창업비 500만원, 내역부터', page(
    logo(True, '가맹점 모집')
    + '<div class="a kicker k" style="top:190px">HABOKDANG FRANCHISE</div>'
    + '<div class="a hl k" style="top:236px;font-size:104px">창업비 500만원,<br><em>내역부터</em> 보여드려요</div>'
    + divider(486)
    + pill(64, 530, '인테리어·장비 <b>별도 · 자율공사</b>', fs=28)
    + pill(64, 596, '가맹비 <b>300만원</b>', fs=28)
    + pill(64, 662, '교육비 <b>200만원</b>', fs=28)
    + sticker(852, 556, 186, '첫 창업<br>비용 공개', fs=34, rot=10)
    + fnbox(FN500_2, 1236),
    plate='hero_a'))

ADS['1-3'] = ('신규창업', '처음 하는 창업, 비용부터 투명하게', page(
    logo(True)
    + '<div class="a kicker k" style="top:196px">HABOKDANG FRANCHISE</div>'
    + '<div class="a hl k" style="top:240px;font-size:100px">처음 하는 창업,<br><em>비용부터</em> 투명하게</div>'
    + pill(64, 476, '서울·경기 가맹점 <b>20곳</b> 계약·오픈*', fs=26)
    + circle('<div style="font-size:37px;font-weight:900;letter-spacing:-.04em;line-height:1.2">가맹비 300만원<br>'
             '<span style="color:var(--or)">교육비 200만원</span></div>'
             '<div style="margin-top:10px;font-size:19px;font-weight:800;color:#8a5a3a">임대·인테리어·장비 별도</div>')
    + fnbox('*2026년 6월 본사 발표, 이넷뉴스 보도 기준 · 임대료·보증금·인테리어·장비 비용 별도', 1242,
            extra='height:66px;display:flex;align-items:center;justify-content:center'),
    plate='ring_a'))

# ============================================================== 2. 업종변경
ADS['2-1'] = ('업종변경', '간판보다 메뉴부터', page(
    logo(False, '가맹점 모집', pill_o=True)
    + '<div class="a small k ink" style="top:214px">업종 전환, 브랜드 고를 때</div>'
    + '<div class="a hl k orc" style="top:268px;font-size:140px;line-height:1.06">간판보다<br>메뉴부터</div>'
    + sparkle(626, 296, 42, '#F06A0F')
    + '<div class="a bar" style="top:600px"></div>'
    + '<div class="a k ink" style="left:64px;top:640px;font-size:33px;font-weight:700;letter-spacing:-.03em;line-height:1.45">인테리어·집기는 지정업체 없이<br>점주가 업체를 직접 고릅니다</div>'
    + pill(64, 774, '컷팅과일·과일디저트 배달 전문', 'o', fs=27)
    + pill(64, 846, '가맹비 300 + 교육비 200만원', 'o', fs=27)
    + fnbox(FN500_2, 1236),
    bg='#FFF8EE', plate='cutfruit_a'))

ADS['2-2'] = ('업종변경', '인테리어·집기 지정업체 없음', page(
    logo(True, '가맹점 모집')
    + '<div class="a small k" style="top:194px;font-size:38px">업종 전환할 때 따져볼 것</div>'
    + '<div class="a hl k" style="top:246px;font-size:110px">인테리어·집기<br><em>지정업체 없음</em></div>'
    + '<div class="a k" style="left:64px;top:500px;font-size:32px;font-weight:800;letter-spacing:-.035em">시공업체와 집기 구매처를 점주가 정합니다</div>'
    + pill(64, 590, '가맹비 <b>300만원</b>', fs=28)
    + pill(64, 656, '교육비 <b>200만원</b>', fs=28)
    + sticker(22, 966, 238, '점주<br>자율공사', fs=42, rot=-8)
    + fnbox('가맹비·교육비 외 임대료·보증금·인테리어·장비 비용 별도 · 세부 조건은 가맹계약서 기준', 1248,
            extra='height:62px;display:flex;align-items:center;justify-content:center'),
    plate='bingsu_a'))

ADS['2-3'] = ('업종변경', '업종 전환 전에 묻는 3가지', page(
    logo(True, '가맹점 모집')
    + '<div class="a hl k" style="top:196px;font-size:110px">업종 전환 전에<br><em>묻는 3가지</em></div>'
    + '<div class="a k" style="left:64px;top:470px;width:466px;display:flex;flex-direction:column;gap:16px">'
    + ''.join(f'''<div class="card" style="padding:16px 22px;border-radius:24px">
        <div style="font-size:26px;font-weight:800;color:#C9500A;letter-spacing:-.03em">Q. {q}</div>
        <div style="margin-top:4px;font-size:31px;font-weight:900;letter-spacing:-.04em">{a}</div></div>'''
              for q, a in [('인테리어 업체가 정해져 있나요?', '지정업체 없이 점주 자율공사'),
                           ('어떤 메뉴로 운영하나요?', '컷팅과일·빙수·화채 배달'),
                           ('과일은 어떻게 들여오나요?', '가락시장 경매 매입·전표 공개')])
    + '</div>'
    + '<div class="a fn k ink" style="right:44px;top:1222px;width:300px;text-align:right;font-weight:700;opacity:.8">인테리어·집기 업체 선정 등<br>세부 조건은 가맹계약서 기준</div>',
    plate='delivery_a'))

# ============================================================== 3. 프랜차이즈 문제해결
ADS['3-1'] = ('문제해결', '가맹점 1곳이 낸 평균 차액가맹금', page(
    logo(True)
    + '<div class="a kicker k" style="top:192px;letter-spacing:.02em;font-size:28px">공정위 2025년도 가맹사업 현황 · 외식업</div>'
    + '<div class="a k" style="left:64px;top:236px;font-size:50px;font-weight:900;letter-spacing:-.04em">가맹점 1곳이 낸 평균 차액가맹금</div>'
    + '<div class="a hl k" style="top:300px;font-size:128px">연 2,600만원</div>'
    + '<div class="a k" style="left:64px;top:452px;font-size:36px;font-weight:800;letter-spacing:-.035em;color:#FFF1E2">계약 전, 공급 마진부터 확인하세요</div>'
    + pill(64, 532, '과일 <b>경매 원가 전표</b> 공개', fs=27)
    + pill(64, 598, '과일 본사 몫 <b>박스당 정액</b>', fs=27)
    + fnbox('출처: 공정거래위원회 2025년도 가맹사업 현황(2026.4 발표, 2024년 말 정보공개서 기준)<br>외식 가맹점 1곳당 연평균 · 매출 대비 4.4% · 하복당 수익과 무관한 업계 평균', 1236),
    plate='hero_a'))

ADS['3-2'] = ('문제해결', "'차액가맹금' 들어보셨나요", page(
    logo(False)
    + '<div class="a small k ink" style="top:214px;font-size:38px">프랜차이즈 계약 전에 알아둘 단어</div>'
    + '<div class="a hl k orc" style="top:268px;font-size:110px">‘차액가맹금’<br>들어보셨나요?</div>'
    + sticker(860, 184, 172, '전표<br>공개', fs=40, rot=8)
    + '''<div class="a card k" style="left:64px;top:548px;width:460px;padding:24px 28px">
      <div style="font-size:25px;font-weight:800;color:#C9500A">차액가맹금이란?</div>
      <div style="margin-top:8px;font-size:28px;font-weight:800;letter-spacing:-.04em;line-height:1.4">본사가 물품을 공급하며<br>적정 도매가격을 넘겨 받는 대가,<br>즉 유통마진</div>
      <div style="margin-top:10px;font-size:19px;font-weight:700;color:#8a5a3a">공정거래위원회 정의 (뉴시스 2026.4.11 보도)</div></div>'''
    + pill(64, 822, '하복당은 과일 <span style="color:#FFE7CF">원가 전표</span> 공개', 'o', fs=27)
    + pill(64, 890, '과일 본사 몫 <b>박스당 1,000원</b>', fs=27)
    + fnbox(BOXFIX + '<br>원가 전표는 과일 공급분 기준, 세부 항목은 상담 시 안내', 1236),
    bg='#FFF8EE', plate='cutfruit_a'))

ADS['3-3'] = ('문제해결', '과일 원가, 전표로 공개', page(
    logo(False)
    + '<div class="a small k ink" style="top:214px;font-size:38px">과일 공급가, 이렇게 정합니다</div>'
    + '<div class="a hl k orc" style="top:268px;font-size:122px">과일 원가,<br>전표로 공개</div>'
    + '<div class="a k ink" style="left:64px;top:552px;font-size:32px;font-weight:800;letter-spacing:-.035em">과일 공급의 본사 몫은 <span style="color:var(--or)">박스당 1,000원</span>으로 정해 둡니다</div>'
    + pill(64, 630, '과일 <b>경매 원가 전표</b>', fs=28)
    + pill(64, 698, '본사 몫 <b>박스당 1,000원</b>', fs=28)
    + sticker(836, 600, 176, '전표<br>공개', fs=40, rot=8)
    + fnbox(BOXFIX + ' · 원가 전표는 과일 공급분 기준', 1252,
            extra='height:58px;display:flex;align-items:center;justify-content:center'),
    bg=CREAM, plate='pavlova_a'))

# ============================================================== 4. 소자본 창업 및 1인 운영
ADS['4-1'] = ('소자본·1인', '창업비 500만원', page(
    logo(True, '가맹점 모집')
    + '<div class="a kicker k" style="top:190px">HABOKDANG FRANCHISE</div>'
    + '<div class="a hl k" style="top:230px;font-size:110px;line-height:1">창업비<span style="font-size:42px;letter-spacing:-.03em"> (가맹비+교육비)</span></div>'
    + '<div class="a hl k" style="top:336px;font-size:196px;line-height:1">500<span style="font-size:130px">만원</span></div>'
    + '<div class="a k" style="left:64px;top:552px;font-size:30px;font-weight:800;letter-spacing:-.035em">임대료·보증금·인테리어·장비 비용 별도</div>'
    + pill(64, 612, '가맹비 <b>300만원</b>', fs=28)
    + pill(64, 678, '교육비 <b>200만원</b>', fs=28)
    + '<div class="a k" style="left:64px;top:756px;font-size:33px;font-weight:800;letter-spacing:-.035em;line-height:1.38">인테리어·집기는<br>점주 자율공사</div>'
    + sticker(22, 966, 238, '소자본<br>창업', fs=46, rot=-8),
    plate='bingsu_a'))

ADS['4-2'] = ('소자본·1인', '작게 시작하는 과일 배달 창업', page(
    logo(True, '배달의민족 · 쿠팡이츠')
    + '<div class="a small k" style="top:206px;font-size:40px">배달 전문 매장으로</div>'
    + '<div class="a hl k" style="top:264px;font-size:110px">작게 시작하는<br><em>과일 배달 창업</em></div>'
    + sparkle(880, 292, 40)
    + pill(64, 562, '창업비 <b>500만원</b>', fs=30)
    + pill(64, 646, '인테리어·집기 <b>자율공사</b>', fs=28)
    + fnbox('가맹비 300만원 + 교육비 200만원 기준<br>임대료·보증금·인테리어·장비 비용 별도', 740, left=64, right=580,
            extra='text-align:left'),
    plate='delivery_a'))

ADS['4-3'] = ('소자본·1인', '500만원에서 시작하는 구조', page(
    logo(False)
    + '<div class="a small k ink" style="top:214px">과일 배달 창업, 구조 한눈에</div>'
    + '<div class="a hl k" style="top:268px;font-size:118px;line-height:1.08"><span style="color:var(--or)">500만원에서</span><br><span style="color:var(--ink)">시작하는 구조</span></div>'
    + '<div class="a bar" style="top:552px"></div>'
    + '<div class="a k ink" style="left:64px;top:592px;width:350px;display:flex;flex-direction:column;gap:20px">'
    + ''.join(f'''<div style="display:flex;gap:16px;align-items:flex-start">
        <div style="flex:none;width:46px;height:46px;border-radius:50%;background:var(--or);color:#fff;font-size:25px;font-weight:900;display:flex;align-items:center;justify-content:center">{i}</div>
        <div><div style="font-size:23px;font-weight:800;color:#C9500A;letter-spacing:-.02em">{t}</div>
        <div style="margin-top:2px;font-size:27px;font-weight:900;letter-spacing:-.04em;line-height:1.25">{d}</div>{x}</div></div>'''
              for i, (t, d, x) in enumerate([
                  ('창업비', '가맹비 300만원<br>+ 교육비 200만원', '<div style="margin-top:4px;font-size:20px;font-weight:700;opacity:.8">임대료·보증금·인테리어·장비 별도</div>'),
                  ('매장', '인테리어·집기<br>자율공사', ''), ('과일', '본사 공급,<br>원가 전표 공개', ''),
                  ('판매', '배민·쿠팡이츠<br>배달', '')], 1))
    + '</div>'
    + pill(700, 1140, '하복당 <b>과일박스</b>', fs=27),
    bg='#F6EFE8', plate='fruitbox_b'))

# ============================================================== 5. 매출 및 수익성
ADS['5-1'] = ('매출·수익성', '원가가 보이면 마진이 보입니다', page(
    logo(False)
    + '<div class="a small k ink" style="top:214px">수익 계산, 이렇게 합니다</div>'
    + '<div class="a hl k orc" style="top:268px;font-size:112px">원가가 보이면<br>마진이 보입니다</div>'
    + '''<div class="a card k" style="left:64px;top:548px;width:430px;padding:20px 26px;letter-spacing:-.035em">'''
    + ''.join(f'<div style="padding:7px 0;{st}"><div style="font-size:29px;font-weight:800;line-height:1.25">{a}</div>{b}</div>'
              for a, b, st in [
                  ('판매가', '', ''),
                  ('− 과일 원가', '<div style="font-size:22px;font-weight:800;color:#C9500A">경매 원가 전표 공개</div>', ''),
                  ('− 본사 몫(과일)', '<span style="display:inline-block;margin-top:2px;padding:2px 12px;border-radius:20px;background:var(--or);color:#fff;font-size:22px;font-weight:900">박스당 1,000원</span>', ''),
                  ('− 배달앱 수수료·포장비', '<div style="font-size:22px;font-weight:800;color:#C9500A">매장별 상이</div>', ''),
                  ('− 임대료·인건비 등', '<div style="font-size:22px;font-weight:800;color:#C9500A">매장별 상이</div>', 'border-bottom:3px solid #3A1705;padding-bottom:12px'),
                  ('<span style="color:var(--or);font-size:34px;font-weight:900">= 내 마진</span>', '', 'padding-top:10px')])
    + '</div>'
    + fnbox(NOGUAR + '<br>' + BOXFIX, 1236),
    bg='#FFF8EE', plate='cutfruit_a'))

ADS['5-2'] = ('매출·수익성', '매출보다 빨리 오른 숫자', page(
    logo(True)
    + pill(1016, 64, '외식 가맹점 평균 매출 <b>+6.1%</b>', fs=24, right=True)
    + pill(1016, 132, '평균 차액가맹금 <b style="font-size:34px">+13.0%</b>', fs=27, right=True)
    + '<div class="a kicker k" style="top:216px;letter-spacing:.02em;font-size:28px">공정위 2025년도 가맹사업 현황 · 전년 대비</div>'
    + '<div class="a hl k" style="top:258px;font-size:112px">매출보다<br><em>빨리 오른 숫자</em></div>'
    + circle('<div style="font-size:35px;font-weight:900;letter-spacing:-.04em;line-height:1.2">본사가<br>'
             '<span style="color:var(--or)">공급에서 받는 돈</span></div>'
             '<div style="margin-top:10px;font-size:19px;font-weight:800;color:#8a5a3a;line-height:1.3">하복당 본사 몫<br>과일 박스당 1,000원 고정</div>')
    + fnbox('차액가맹금: 본사가 필수품목을 공급하며 적정 도매가격을 넘겨 받는 대가(공정위 정의, 뉴시스 2026.4.11)<br>'
            '출처: 공정거래위원회 2025년도 가맹사업 현황(2026.4 발표, 2024년 말 정보공개서 기준)<br>'
            '박스당 1,000원은 과일 공급 기준 · ' + NOGUAR, 1200, extra='font-size:20px'),
    plate='ring_a'))

ADS['5-3'] = ('매출·수익성', '수익, 숫자 보고 직접 계산', page(
    logo(True, '가맹 상담')
    + '<div class="a hl k" style="top:184px;font-size:96px">수익, 숫자 보고<br><em>직접 계산하세요</em></div>'
    + pill(64, 428, '과일 <b>경매 원가 전표</b>', fs=28)
    + pill(64, 498, '본사 몫 <b>박스당 1,000원</b>', fs=28)
    + pill(64, 568, '창업 <b>비용 내역</b>', fs=28)
    + sticker(852, 430, 186, '상담에서<br>직접 확인', fs=33, rot=10)
    + fnbox(NOGUAR + '<br>' + '박스당 1,000원은 과일 공급 기준', 1240, left=560, extra='text-align:right'),
    plate='hero_c'))


def render(ids):
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for k in ids:
        hp = os.path.join(OUT, f'{k}.html')
        open(hp, 'w').write(ADS[k][2])
        jobs.append({'html': hp, 'out': os.path.join(OUT, f'{k}.png'), 'width': 1080, 'height': 1350})
    jp = os.path.join(HERE, '_jobs.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), jp], check=True)
    from PIL import Image
    import numpy as np
    meta = json.loads(subprocess.run(['node', os.path.join(HERE, 'measure.js'), jp, os.path.join(HERE, '_m')],
                                     check=True, capture_output=True, text=True).stdout)
    boxes = {}
    for name, items in meta.items():
        boxes[name] = []
        for it in items:
            a = np.asarray(Image.open(it.pop('png')))[..., 3]
            ys, xs = np.nonzero(a >= 110)
            if len(xs):
                boxes[name].append({**it, 'x0': int(xs.min()), 'y0': int(ys.min()), 'x1': int(xs.max()) + 1, 'y1': int(ys.max()) + 1})
    old = {}
    bp = os.path.join(HERE, '_boxes.json')
    if os.path.exists(bp):
        old = json.load(open(bp))
    old.update(boxes)
    json.dump(old, open(bp, 'w'), ensure_ascii=False, indent=1)
    for k in ids:
        Image.open(os.path.join(OUT, f'{k}.png')).convert('RGB').save(os.path.join(OUT, f'{k}.jpg'), quality=93)
    probs = []
    for name, items in boxes.items():
        for it in items:
            if it['y0'] < 24 or it['y1'] > 1350 - 20 or it['x0'] < 20 or it['x1'] > 1080 - 20:
                probs.append(f"{name}: '{it['text']}' too close to edge ({it['x0']},{it['y0']})-({it['x1']},{it['y1']})")
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                ox = min(a['x1'], b['x1']) - max(a['x0'], b['x0']); oy = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
                if ox > 4 and oy > 4:
                    probs.append(f"{name}: overlap '{a['text'][:18]}' x '{b['text'][:18]}' ({ox}x{oy}px)")
    print('\n'.join(probs) if probs else 'layout check: no problems')


def sheet():
    from PIL import Image, ImageDraw, ImageFont
    ids = list(ADS)
    w, h = 324, 405
    sh = Image.new('RGB', (5 * (w + 12) + 12, 3 * (h + 12) + 12), (28, 28, 28))
    order = [[k for k in ids if k.startswith(f'{t}-')] for t in '12345']
    for c, col in enumerate(order):
        for r, k in enumerate(col):
            p = os.path.join(OUT, f'{k}.jpg')
            if os.path.exists(p):
                sh.paste(Image.open(p).resize((w, h)), (12 + c * (w + 12), 12 + r * (h + 12)))
    sh.save(os.path.join(HERE, '_sheet.jpg'), quality=88)


if __name__ == '__main__':
    ids = sys.argv[1:] or list(ADS)
    render(ids)
    sheet()
