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
            r = p.add_run(); r.text = text
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
    tbox(sl, 940, 466, 230, 120, [[('교육 이틀,', HEAD, 42, INK, None)], [('바로 오픈!', HEAD, 42, INK, None)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False, rot=-12, name='배지 문구')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 80, 330, 450, 80, CREAM, radius=40, name='상단 말풍선',
          text=[[('카페 운영 중인 사장님!', BODY_XB, 40, INK, None)]])
    tbox(sl, 78, 584, 1100, 120, [[('지금 그 카페 자리에서,', HEAD, 96, CREAM, {'shadow': (SHADOW, 6)})]], wrap=False, name='헤드라인 1')
    shape(sl, MSO_SHAPE.RECTANGLE, 70, 715, 980, 150, YEL, rot=-1.6, shadow=(SHADOW, 16, 3240000), name='헤드라인 2 박스',
          text=[[('하복당으로 다시 시작!', HEAD, 108, INK, None)]])
    for i in range(2):
        shape(sl, MSO_SHAPE.ISOSCELES_TRIANGLE, 76 + i * 38, 925, 48, 34, YEL, rot=90, name='화살표')
    tbox(sl, 172, 916, 1000, 70, [[('카페 업종변경 · 숍인숍 가맹점 모집', HEAD, 52, CREAM, None)]], wrap=False, name='모집 문구')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 70, 1010, 1100, 530, CREAM, radius=40, name='카드')
    rows = [('불·기름\n없는 주방', [('조리가 아니라 ', INK), ('조합', 'E0490A')], '정해진 레시피대로 과일·시럽·토핑을 담아요 · 기본 교육 이틀'),
            ('검증된\n배달 매출', [('안양점 6월 배달 매출 ', INK), ('5,073만원', 'E0490A')], '배민 약 2,577만원 + 쿠팡이츠 약 2,497만원 · 영업잔여금 21.3%'),
            ('투명한\n과일 공급', [('가락시장 경매가 + ', INK), ('원가 전표', 'E0490A')], '박스당 1,000원만 붙여 본점과 같은 단가로 공급'),
            ('카페 그대로\n숍인숍', [('운영 중인 카페에 ', INK), ('하복당 더하기', 'E0490A')], '간판·내부 주황색 페인트는 필수 · 10평 내외, 배달·포장 중심')]
    for i, (badge, title, sub) in enumerate(rows):
        y0 = 1036 + i * 119
        shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 110, y0 + 11, 200, 96, DEEP, radius=20, name=f'배지 {i + 1}',
              text=[[(t, HEAD, 32, CREAM, None)] for t in badge.split('\n')])
        tbox(sl, 344, y0 + 14, 800, 58, [[(t, HEAD, 46, c, None) for t, c in title]], wrap=False, name=f'항목 {i + 1} 제목')
        tbox(sl, 344, y0 + 72, 800, 36, [[(sub, BODY_SB, 26, '5A3A26', None)]], wrap=False, name=f'항목 {i + 1} 설명')
        if i < 3:
            ln = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(110), E(y0 + 119), E(1130), E(y0 + 119))
            ln.line.color.rgb = C('E8C9AC'); ln.line.width = E(3); ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 70, 1614, 270, 84, YEL, radius=18, name='미팅 버튼',
          text=[[('1:1 미팅 예약', HEAD, 40, INK, None)]])
    tbox(sl, 360, 1592, 810, 130, [[(PHONE, HEAD, 104, CREAM, {'shadow': (SHADOW, 7)})]], align=PP_ALIGN.RIGHT, wrap=False, name='전화번호')


def back(sl):
    background(sl)
    picture(sl, os.path.join(H, 'logo_w_4x.png'), 510, 50, 220, 171, name='로고')
    tbox(sl, 0, 246, 1240, 130, [[('카페 사장님께', HEAD, 104, YEL, {'shadow': (SHADOW, 6)}), (' 드리는 편지', HEAD, 104, CREAM, {'shadow': (SHADOW, 6)})]],
         align=PP_ALIGN.CENTER, wrap=False, name='제목')
    picture(sl, os.path.join(H, 'storefront_wide.jpg'), 60, 380, 1120, 420, kind=MSO_SHAPE.ROUNDED_RECTANGLE, line=YEL, line_w=10,
            name='매장 사진 — 우클릭 > 그림 바꾸기')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 60, 830, 1120, 700, CREAM, radius=44, name='편지 카드')
    tbox(sl, 130, 872, 760, 70, [[('카페 자리에서 다시 시작하는 방법', HEAD, 54, DEEP, None)]], wrap=False, name='편지 제목')
    tbox(sl, 860, 892, 250, 40, [[('하복당 가맹본부', BODY, 26, '7A5A44', {'bold': True})]], align=PP_ALIGN.RIGHT, wrap=False, name='보내는 사람')
    O, Bd = {'bold': False}, {'bold': True}
    HL = {'bold': True, 'highlight': 'FFE08A'}
    paras = [
        [('하복당은 생과일을 손질해 컵과 그릇에 담아 파는 과일디저트 브랜드입니다. ', BODY, 25, '2B140A', O), ('10평 내외 매장에서 배달과 포장 중심', BODY, 25, '2B140A', Bd), ('으로 운영합니다.', BODY, 25, '2B140A', O)],
        [('메뉴는 조리가 아니라 조합입니다. ', BODY, 25, '2B140A', O), ('불도 기름도 쓰지 않고', BODY, 25, 'C2410A', HL), (' 정해진 레시피대로 만들어 ', BODY, 25, '2B140A', O),
         ('기본 교육은 이틀', BODY, 25, 'C2410A', HL), ('이면 됩니다. 오픈 전 상권 분석과 배달앱 세팅, 초기 바이럴은 본사가 함께 준비합니다.', BODY, 25, '2B140A', O)],
        [('과일은 ‘명가’가 가락시장 중앙청과 경매에서 매입해 보내 드립니다. ', BODY, 25, '2B140A', O), ('원가 전표', BODY, 25, 'C2410A', HL), ('를 함께 드리고, ', BODY, 25, '2B140A', O),
         ('박스당 1,000원', BODY, 25, 'C2410A', HL), ('만 붙여 본점과 같은 단가로 공급합니다.', BODY, 25, '2B140A', O)],
        [('운영 중인 카페에 하복당을 더하는 ', BODY, 25, '2B140A', O), ('숍인숍', BODY, 25, 'C2410A', HL), ('도 가능합니다. 간판과 내부 주황색 페인트는 꼭 갖추셔야 합니다.', BODY, 25, '2B140A', O)],
        [('매출과 비용은 1:1 미팅에서 손익계산서와 원가 전표로 보여 드리고, 수익 자료는 서면으로 드립니다. 정보공개서와 계약서(안)를 받으신 뒤 ', BODY, 25, '2B140A', O),
         ('14일이 지나야 계약', BODY, 25, '2B140A', Bd), ('합니다. ', BODY, 25, '2B140A', O), ('충분히 따져 보고 결정하세요.', BODY, 25, '2B140A', Bd)],
    ]
    tbox(sl, 130, 954, 980, 470, paras, line=1.38, after=12, name='편지 본문')
    tbox(sl, 640, 1456, 470, 64, [[('하복당 가맹본부 드림', PEN, 54, 'C2410A', None)]], align=PP_ALIGN.RIGHT, wrap=False, name='서명')
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, 60, 1556, 190, 180, CREAM, radius=28, name='로고 박스')
    picture(sl, os.path.join(H, 'logo_o_4x.png'), 80, 1588, 150, 117, name='로고(주황)')
    tbox(sl, 300, 1562, 900, 60, [[('궁금하신 점은 1:1 미팅에서 숫자로 보여드립니다.', HEAD, 42, CREAM, None)]], wrap=False, name='안내 문구')
    tbox(sl, 296, 1622, 900, 120, [[(PHONE, HEAD, 104, YEL, {'shadow': (SHADOW, 7)})]], wrap=False, name='전화번호')


if __name__ == '__main__':
    from PIL import Image
    im = Image.open(os.path.join(H, 'storefront.jpg')).convert('RGB')      # whole storefront, cropped only to the 1120:420 frame
    tw = round(im.height * 1120 / 420)
    l = max(0, (im.width - tw) // 2)
    im.crop((l, 0, l + min(tw, im.width), im.height)).save(os.path.join(H, 'storefront_wide.jpg'), quality=95)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(7560000), Emu(10692000)     # A4 portrait
    blank = prs.slide_layouts[6]
    front(prs.slides.add_slide(blank))
    back(prs.slides.add_slide(blank))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, 'flyer.pptx')
    prs.save(out)
    print('saved', out)
