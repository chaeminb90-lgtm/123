"""하복당 카페 업종변경 전단 — 글자를 직접 고칠 수 있는 PowerPoint 버전 (A4 세로 2장).
모든 글자는 텍스트 상자, 카드·버튼은 도형, 사진은 '그림 바꾸기'로 교체 가능한 그림입니다.
좌표는 인쇄용 HTML(make_flyer.py)과 같은 1240x1754 기준(px)으로 적고 mm로 환산합니다.
usage: python3 ops/flyer/make_pptx.py <out.pptx>
"""
import os, sys, copy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from lxml import etree

H = os.path.dirname(os.path.abspath(__file__))
K = 7560000 / 1240            # EMU per design px (A4 width 210mm = 1240px)
E = lambda v: Emu(int(round(v * K)))
FPT = lambda px: Pt(round(px * 0.48, 1))  # design px -> pt
HEAD, BODY, BODY_SB, BODY_XB, PEN = 'Black Han Sans', 'Pretendard', 'Pretendard SemiBold', 'Pretendard ExtraBold', 'Nanum Pen Script'
C = lambda h: RGBColor.from_string(h)
INK, DEEP, YEL, CREAM, SHADOW = '3A1705', 'B8430A', 'FFD24A', 'FFF4E6', '8A2F04'
PHONE = '010.7683.1577'


def set_font(run, name, size_px, color, bold=False, shadow=None, highlight=None):
    f = run.font
    f.name = name; f.size = FPT(size_px); f.bold = bold; f.color.rgb = C(color)
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', name)
    if shadow:   # hard drop shadow straight down, like the print version
        eff = etree.SubElement(rPr, qn('a:effectLst'))
        sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad='0', dist=str(int(shadow[1] * K)), dir='5400000', algn='t', rotWithShape='0')
        clr = etree.SubElement(sh, qn('a:srgbClr'), val=shadow[0])
        # effectLst must come before latin/ea/cs in rPr
        rPr.remove(eff); rPr.insert(0 if rPr.find(qn('a:solidFill')) is None else 1, eff)
    if highlight:
        hl = etree.SubElement(rPr, qn('a:highlight'))
        etree.SubElement(hl, qn('a:srgbClr'), val=highlight)
        rPr.remove(hl); rPr.append(hl)


def tbox(sl, x, y, w, h, paras, *, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, wrap=True, line=None, after=0, rot=0, name=None):
    """paras: list of paragraphs; each paragraph is a list of runs (text, font, size_px, color, opts dict)."""
    tb = sl.shapes.add_textbox(E(x), E(y), E(w), E(h))
    if name: tb.name = name
    tb.rotation = rot
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line: p.line_spacing = line
        if after: p.space_after = FPT(after)
        for text, font, size, color, opt in runs:
            for k, piece in enumerate(text.split('\n')):
                if k:
                    p.add_line_break()
                if piece:
                    r = p.add_run(); r.text = piece
                    set_font(r, font, size, color, **(opt or {}))
    return tb


def shape(sl, kind, x, y, w, h, fill, *, radius=None, line=None, line_w=0, rot=0, shadow=None, name=None, text=None):
    s = sl.shapes.add_shape(kind, E(x), E(y), E(w), E(h))
    if name: s.name = name
    s.rotation = rot
    s.fill.solid(); s.fill.fore_color.rgb = C(fill)
    if line:
        s.line.color.rgb = C(line); s.line.width = E(line_w)
    else:
        s.line.fill.background()
    if radius is not None and len(s.adjustments):
        s.adjustments[0] = min(0.5, radius / min(w, h))
    if shadow:
        spPr = s._element.spPr
        eff = etree.SubElement(spPr, qn('a:effectLst'))
        sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad='0', dist=str(int(shadow[1] * K)), dir=str(shadow[2]), algn='t', rotWithShape='0')
        etree.SubElement(sh, qn('a:srgbClr'), val=shadow[0])
    else:   # theme shapes carry a default style shadow in some viewers; switch it off
        etree.SubElement(s._element.spPr, qn('a:effectLst'))
    if text:
        tf = s.text_frame
        tf.word_wrap = True; tf.auto_size = None
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for i, runs in enumerate(text):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            for t, font, size, color, opt in runs:
                r = p.add_run(); r.text = t
                set_font(r, font, size, color, **(opt or {}))
    return s


def picture(sl, path, x, y, w, h, *, kind=None, line=None, line_w=0, name=None):
    pic = sl.shapes.add_picture(path, E(x), E(y), E(w), E(h))
    if name: pic.name = name
    if kind is not None:
        pic.auto_shape_type = kind
    if line:
        pic.line.color.rgb = C(line); pic.line.width = E(line_w)
    return pic


def background(sl):
    fill = sl.background.fill
    fill.gradient(); fill.gradient_angle = 90
    st = fill.gradient_stops
    st[0].color.rgb = C('F47A22'); st[0].position = 0
    st[1].color.rgb = C('E05A0C'); st[1].position = 1.0


def front(sl):
    background(sl)
    picture(sl, os.path.join(H, 'logo_w_4x.png'), 84, 64, 300, 233, name='로고')
    picture(sl, os.path.join(H, 'fruit_boxes_sq.jpg'), 690, 50, 500, 500, kind=MSO_SHAPE.OVAL, line=CREAM, line_w=14, name='사진(원) — 우클릭 > 그림 바꾸기')
    shape(sl, MSO_SHAPE.STAR_12_POINT, 930, 400, 250, 250, YEL, rot=-12, name='배지')
    tbox(sl, 940, 466, 230, 120, [[('교육 3일,', HEAD, 42, INK, None)], [('바로 오픈!', HEAD, 42, INK, None)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False, rot=-12, name='배지 문구')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 80, 330, 450, 80, CREAM, radius=40, name='상단 말풍선',
          text=[[('카페 운영 중인 사장님!', BODY_XB, 40, INK, None)]])
    tbox(sl, 78, 584, 1100, 120, [[('지금 그 카페 자리에서,', HEAD, 96, CREAM, {'shadow': (SHADOW, 6)})]], wrap=False, name='헤드라인 1')
    shape(sl, MSO_SHAPE.RECTANGLE, 70, 715, 980, 150, YEL, rot=-1.6, shadow=(SHADOW, 16, 3240000), name='헤드라인 2 박스',
          text=[[('하복당으로 다시 시작!', HEAD, 108, INK, None)]])
    for i in range(2):
        shape(sl, MSO_SHAPE.ISOSCELES_TRIANGLE, 76 + i * 38, 925, 48, 34, YEL, rot=90, name='화살표')
    tbox(sl, 172, 916, 1000, 70, [[('카페 업종변경 · 숍인숍 가맹점 모집', HEAD, 52, CREAM, None)]], wrap=False, name='모집 문구')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 70, 996, 1100, 600, CREAM, radius=40, name='카드')
    rows = [('불·기름\n없는 주방', [('과일을 ', INK), ('담기만 하면 끝!', 'E0490A')], '교육 3일이면 나도 과일 마스터!'),
            ('검증된\n배달 매출', [('구월점 배달 매출 ', INK), ('8,200만원', 'E0490A')], '인계점 6월 7,200만원 · 7월 전 지점 평균 5,000만원 달성'),
            ('투명한\n과일 공급', [('가락시장 경매가로 ', INK), ('매장 앞까지', 'E0490A')], '저녁에 발주하면 가락시장 과일 도매회사가 매장 앞까지 바로 배달'),
            ('로스율\n0%', [('썩은 과일은 ', INK), ('100% 환불', 'E0490A')], '과일 단 하나라도 상한 채 배송되면 전액 환불해 드립니다'),
            ('간판만 바꾸면\n바로 시작', [('도마와 칼', 'E0490A'), ('만 있으면 OK', INK)], '인테리어 공사 없이 간판만 달면 바로 시작')]
    for i, (badge, title, sub) in enumerate(rows):
        y0 = 1016 + i * 112
        shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 110, y0 + 11, 200, 90, DEEP, radius=20, name=f'배지 {i + 1}',
              text=[[(t, HEAD, 29, CREAM, None)] for t in badge.split('\n')])
        tbox(sl, 344, y0 + 14, 800, 56, [[(t, HEAD, 44, c, None) for t, c in title]], wrap=False, name=f'항목 {i + 1} 제목')
        tbox(sl, 344, y0 + 70, 800, 34, [[(sub, BODY_SB, 25, '5A3A26', None)]], wrap=False, name=f'항목 {i + 1} 설명')
        if i < 4:
            ln = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(110), E(y0 + 112), E(1130), E(y0 + 112))
            ln.line.color.rgb = C('E8C9AC'); ln.line.width = E(3); ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 70, 1636, 270, 84, YEL, radius=18, name='미팅 버튼',
          text=[[('1:1 미팅 예약', HEAD, 40, INK, None)]])
    tbox(sl, 360, 1614, 810, 130, [[(PHONE, HEAD, 104, CREAM, {'shadow': (SHADOW, 7)})]], align=PP_ALIGN.RIGHT, wrap=False, name='전화번호')


def back(sl):
    background(sl)
    picture(sl, os.path.join(H, 'logo_w_4x.png'), 535, 36, 170, 132, name='로고')
    tbox(sl, 0, 182, 1240, 120, [[('카페 사장님께', HEAD, 94, YEL, {'shadow': (SHADOW, 6)}), (' 드리는 편지', HEAD, 94, CREAM, {'shadow': (SHADOW, 6)})]],
         align=PP_ALIGN.CENTER, wrap=False, name='제목')
    picture(sl, os.path.join(H, 'storefront_wide.jpg'), 60, 306, 1120, 196, kind=MSO_SHAPE.ROUNDED_RECTANGLE, line=YEL, line_w=10,
            name='매장 사진 — 우클릭 > 그림 바꾸기')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 60, 520, 1120, 1030, CREAM, radius=44, name='편지 카드')
    tbox(sl, 130, 556, 980, 84, [[('사장님, 요즘 많이 힘드시죠?', HEAD, 64, DEEP, None)]], wrap=False, name='편지 제목')
    t = lambda x, o=None: (x, BODY, 31, '2B140A', o or {'bold': False})
    tbox(sl, 130, 652, 980, 360, [
        [t('카페 하나 지키는 게 얼마나 버거운지 잘 압니다.\n문 닫는 가게 소식이 남 얘기 같지 않으실 겁니다.')],
        [t('‘배달은 남는 게 없다’고 생각하시죠? 맞습니다.\n가격이 정해진 치킨·피자라면요.')],
        [t('그런데 파인애플 250g 원가, 알고 계신가요?\n같은 사과도 한 개에 1천 원부터 1만 원까지,\n과일은 상품성에 따라 값이 크게 다릅니다.')],
    ], line=1.22, after=18, name='편지 본문 1')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 130, 1022, 980, 122, 'FFE7A6', radius=18, name='강조 박스')
    shape(sl, MSO_SHAPE.RECTANGLE, 130, 1022, 12, 122, 'F06A0F', name='강조 선')
    tbox(sl, 168, 1036, 920, 96, [[('그래서 하복당은\n가락시장 도매회사와 직접 손을 잡았습니다.', BODY, 34, 'B8430A', {'bold': True})]],
         line=1.15, anchor=MSO_ANCHOR.MIDDLE, name='강조 문장')
    tbox(sl, 130, 1172, 980, 290, [
        [t('말로만 소자본이 아니라,\n돈이 없어도 의지와 열정만 있으면\n시작할 수 있는 브랜드를 만들고 싶었습니다.')],
        [t('본사만 배부른 브랜드가 아니라,\n'), t('함께 돈 버는 브랜드', {'bold': True}), t('를 만들겠습니다.\n지금의 적자. 저희와 함께라면 분명 이겨낼 수 있습니다.')],
    ], line=1.22, after=18, name='편지 본문 2')
    tbox(sl, 640, 1466, 470, 70, [[('하복당 가맹본부 드림', PEN, 64, 'C2410A', None)]], align=PP_ALIGN.RIGHT, wrap=False, name='서명')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 60, 1564, 190, 180, CREAM, radius=28, name='로고 박스')
    picture(sl, os.path.join(H, 'logo_o_4x.png'), 80, 1596, 150, 117, name='로고(주황)')
    tbox(sl, 300, 1570, 900, 60, [[('궁금하신 점은 1:1 미팅에서 숫자로 보여드립니다.', HEAD, 42, CREAM, None)]], wrap=False, name='안내 문구')
    tbox(sl, 296, 1630, 900, 120, [[(PHONE, HEAD, 104, YEL, {'shadow': (SHADOW, 7)})]], wrap=False, name='전화번호')


if __name__ == '__main__':
    from PIL import Image
    im = Image.open(os.path.join(H, 'storefront.jpg')).convert('RGB')      # whole storefront, cropped only to the 1120:420 frame
    th = round(im.width * 196 / 1120)
    t0 = max(0, round((im.height - th) * 0.20))
    im.crop((0, t0, im.width, t0 + min(th, im.height))).save(os.path.join(H, 'storefront_wide.jpg'), quality=95)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(7560000), Emu(10692000)     # A4 portrait
    blank = prs.slide_layouts[6]
    front(prs.slides.add_slide(blank))
    back(prs.slides.add_slide(blank))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, 'flyer.pptx')
    prs.save(out)
    print('saved', out)
