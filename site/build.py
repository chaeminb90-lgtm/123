#!/usr/bin/env python3
"""하복당 가맹 사이트 빌드.

src/ 를 읽어 두 가지를 만든다.
  dist/          아임웹에 붙여 넣을 파일 (공통 코드 + 섹션별 코드 위젯 HTML)
  preview 페이지  전체 화면 미리보기 (로컬 점검용, 아티팩트용, CDN 점검용)

사용 예
  python3 site/build.py dist --sha <커밋 SHA>
  python3 site/build.py preview --mode artifact --out /path/page.html
"""
import argparse
import base64
import glob
import html
import io
import mimetypes
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
IMG = os.path.join(ROOT, 'img')
DIST = os.path.join(ROOT, 'dist')
REPO = 'chaeminb90-lgtm/123'
WIDGET_LIMIT = 1000000  # 아임웹 코드 위젯 최대 글자 수 (아임웹 도움말: 최대 100만 자)

PRETENDARD_CSS = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css'
JUA_CSS = 'https://fonts.googleapis.com/css2?family=Jua&display=swap'


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def sections():
    return [(os.path.basename(p), read(p)) for p in sorted(glob.glob(os.path.join(SRC, 'sections', '*.html')))]


def min_html(s):
    s = re.sub(r'<!--(?!\[).*?-->', '', s, flags=re.S)
    s = re.sub(r'>\s+<', '><', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def min_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([{};])\s*', r'\1', s)
    s = s.replace(';}', '}')
    return s.strip()


def cdn(sha, path):
    return f'https://cdn.jsdelivr.net/gh/{REPO}@{sha}/site/{path}'


def apply_phone(text, phone):
    if not phone:
        return text
    digits = re.sub(r'[^0-9+]', '', phone)
    text = text.replace('data-tel=""', f'data-tel="{html.escape(phone)}"')
    call = (f'<div class="hbd-call" data-reveal><a class="hbd-btn hbd-btn--light" href="tel:{digits}">'
            f'가맹 상담 {html.escape(phone)}</a></div>')
    return text.replace('<ul class="hbd-limit"', call + '\n    <ul class="hbd-limit"', 1)


# ---------------------------------------------------------------- dist
def build_dist(sha, phone, inline_css):
    os.makedirs(os.path.join(DIST, 'imweb'), exist_ok=True)
    css = min_css(read(os.path.join(SRC, 'hbd.css')))
    js = read(os.path.join(SRC, 'hbd.js'))
    write(os.path.join(DIST, 'hbd.css'), css + '\n')
    write(os.path.join(DIST, 'hbd.js'), js)

    head = ['<!-- 하복당 가맹 사이트: 공통 코드 (헤더) -->',
            f'<link rel="stylesheet" href="{PRETENDARD_CSS}">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            f'<link rel="stylesheet" href="{JUA_CSS}">']
    if inline_css:
        head.append('<style>' + css + '</style>')
    else:
        head.append(f'<link rel="stylesheet" href="{cdn(sha, "dist/hbd.css")}">')
    write(os.path.join(DIST, 'imweb', '00-common-head.html'), '\n'.join(head) + '\n')
    write(os.path.join(DIST, 'imweb', '00-common-body.html'),
          '<!-- 하복당 가맹 사이트: 공통 코드 (바디 끝) -->\n'
          f'<script src="{cdn(sha, "dist/hbd.js")}" defer></script>\n')

    report = []
    parts = []
    for name, text in sections():
        text = apply_phone(text, phone).replace('{{IMG}}', cdn(sha, 'img'))
        out = min_html(text)
        parts.append(out)
        report.append((name, len(out)))
    allin = '<!-- 하복당 가맹 페이지 본문 (코드 위젯 1개에 그대로 붙여 넣기) -->\n' + '\n'.join(parts) + '\n'
    write(os.path.join(DIST, 'imweb', '01-main-widget.html'), allin)
    report.append(('01-main-widget.html', len(allin)))
    for name, n in report:
        flag = 'OK ' if n <= WIDGET_LIMIT else 'OVER'
        print(f'{flag} {name:22s} {n:6d} chars')
    over = [n for n in report if n[1] > WIDGET_LIMIT]
    if over:
        sys.exit('섹션 글자 수가 상한을 넘었습니다.')


# ---------------------------------------------------------------- preview
PREVIEW_CSS = r'''
html{background:#FFF8F0}
body{margin:0;background:#FFF8F0;color:#3A1705;font-family:"Pretendard Variable","Pretendard",-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
.pv-note{margin:0;padding:10px max(16px,env(safe-area-inset-left,0px));background:#3A1705;color:#FFE7D3;font-size:13px;line-height:1.5;text-align:center;letter-spacing:-.01em}
.pv-head{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:#fff;border-bottom:1px solid #F2DCC9}
.pv-head__in{display:flex;align-items:center;gap:24px;max-width:1120px;margin:0 auto;min-height:68px;padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px))}
.pv-logo{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:12px;background:#F26A10}
.pv-logo img{width:34px;height:auto;display:block}
.pv-brand{font-size:20px;font-weight:900;letter-spacing:-.04em;color:#3A1705;text-decoration:none}
.pv-nav{display:flex;gap:22px;margin-left:auto;font-size:15px;font-weight:700}
.pv-nav a{color:#3A1705;text-decoration:none}
.pv-nav a.cta{color:#fff;background:#F26A10;padding:9px 16px;border-radius:999px}
.pv-form{background:#FFF8F0;padding:0 max(20px,env(safe-area-inset-right,0px)) 96px max(20px,env(safe-area-inset-left,0px))}
.pv-form form{max-width:720px;margin:-48px auto 0;position:relative;display:grid;gap:16px;padding:36px clamp(20px,4vw,44px);border-radius:24px;background:#fff;box-shadow:0 18px 40px rgba(122,52,0,.12)}
.pv-form .tag{justify-self:start;font-size:12px;font-weight:700;color:#7A5642;border:1px dashed #D9B79C;border-radius:8px;padding:4px 8px}
.pv-form label{display:grid;gap:6px;font-size:15px;font-weight:700}
.pv-form input,.pv-form select,.pv-form textarea{font:inherit;font-weight:500;padding:13px 14px;border:1.5px solid #F2DCC9;border-radius:12px;background:#FFFCF8;color:#3A1705}
.pv-form textarea{min-height:110px;resize:vertical}
.pv-form .agree{display:flex;align-items:center;gap:8px;font-weight:600}
.pv-form button{min-height:56px;border:0;border-radius:999px;background:#F26A10;color:#fff;font:inherit;font-size:17px;font-weight:800;cursor:pointer}
.pv-form .msg{margin:0;font-size:14px;color:#D4520A;font-weight:700}
.pv-foot{background:#3A1705;color:#E9D3C2;font-size:13px;line-height:1.7;padding:40px max(20px,env(safe-area-inset-left,0px)) 120px}
.pv-foot div{max-width:1120px;margin:0 auto}
@media (max-width:760px){.pv-nav a:not(.cta){display:none}}
'''


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def font_face_subset(text, font_path):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    chars = set(text) | set(map(chr, range(32, 127))) | set('·…‘’“”–—★')
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['*']
    opts.notdef_outline = True
    font = TTFont(font_path)
    sub = subset.Subsetter(options=opts)
    sub.populate(text=''.join(sorted(chars)))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = 'woff2'
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f'font subset: {len(chars)} glyph chars, {len(buf.getvalue())//1024} KB')
    return ('@font-face{font-family:"Pretendard Variable";font-weight:45 920;font-style:normal;font-display:swap;'
            f'src:url(data:font/woff2;base64,{b64}) format("woff2-variations"),url(data:font/woff2;base64,{b64}) format("woff2")}}')


def build_preview(mode, out, sha, phone, font_path):
    body_sections = [apply_phone(t, phone) for _, t in sections()]
    body = '\n'.join(body_sections)

    def img_src(m):
        name = m.group(1)
        if mode == 'artifact':
            return data_uri(os.path.join(IMG, name))
        if mode == 'cdn':
            return cdn(sha, 'img/' + name)
        return 'file://' + os.path.join(IMG, name)

    head_html = f'''<header class="pv-head"><div class="pv-head__in">
<a class="pv-brand" href="#hbd-top"><span class="pv-logo"><img src="{{{{IMG}}}}/logo_white.png" alt=""></span></a>
<a class="pv-brand" href="#hbd-top">하복당</a>
<nav class="pv-nav" aria-label="미리보기 메뉴"><a href="#hbd-menu">메뉴</a><a href="#hbd-stores">오픈매장</a><a href="#hbd-process">창업 절차</a><a href="#hbd-faq">FAQ</a><a class="cta" href="#hbd-contact">가맹 문의</a></nav>
</div></header>'''
    form_html = '''<div class="pv-form"><form id="pv-form" novalidate>
<span class="tag">이 칸은 아임웹 입력폼 위젯 자리입니다 (미리보기)</span>
<label for="pv-name">이름<input id="pv-name" name="name" autocomplete="name" placeholder="홍길동"></label>
<label for="pv-tel">연락처<input id="pv-tel" name="tel" inputmode="tel" autocomplete="tel" placeholder="010-0000-0000"></label>
<label for="pv-area">희망 지역<select id="pv-area" name="area"><option>서울</option><option>경기</option><option>인천</option></select></label>
<label for="pv-msg">문의 내용<textarea id="pv-msg" name="msg" placeholder="희망 상권, 오픈 희망 시기 등을 적어 주세요."></textarea></label>
<label class="agree" for="pv-agree"><input type="checkbox" id="pv-agree"> 개인정보 수집·이용에 동의합니다</label>
<button type="submit">상담 신청하기</button>
<p class="msg" id="pv-msg-out" hidden>미리보기 화면이라 실제로 접수되지 않아요. 실제 사이트에서는 아임웹 입력폼으로 접수됩니다.</p>
</form></div>'''
    foot_html = '''<footer class="pv-foot"><div><b>하복당</b><br>바닥글(상호, 대표자, 사업자등록번호, 주소, 연락처)은 지금 아임웹 사이트의 바닥글을 그대로 씁니다.</div></footer>'''
    form_js = '''<script>document.getElementById('pv-form').addEventListener('submit',function(e){e.preventDefault();document.getElementById('pv-msg-out').hidden=false;});</script>'''

    page_body = (f'<p class="pv-note">미리보기 화면입니다. 맨 위 머리말, 문의 입력폼, 맨 아래 바닥글은 아임웹 기본 기능을 그대로 쓰고, 그 사이 섹션들을 코드 위젯으로 넣습니다.</p>\n'
                 f'{head_html}\n<main>\n{body}\n{form_html}\n</main>\n{foot_html}')
    page_body = re.sub(r'\{\{IMG\}\}/([A-Za-z0-9_.-]+)', img_src, page_body)

    css = read(os.path.join(SRC, 'hbd.css'))
    js = read(os.path.join(SRC, 'hbd.js'))
    fonts = ''
    links = ''
    if mode == 'artifact':
        text = re.sub(r'<[^>]+>', ' ', page_body)
        fonts = '<style>' + font_face_subset(text + css, font_path) + '</style>'
        links = f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="{JUA_CSS}">'
    elif mode == 'cdn':
        links = f'<link rel="stylesheet" href="{PRETENDARD_CSS}"><link rel="stylesheet" href="{JUA_CSS}">'
    else:
        fonts = ('<style>@font-face{font-family:"Pretendard Variable";font-weight:45 920;'
                 f'src:url("file://{font_path}") format("truetype")}}</style>')

    doc_head = ('<title>하복당 가맹 사이트</title>\n'
                '<meta name="claude:viewport-fit-sides" content="cover">\n'
                f'{links}\n{fonts}\n<style>{PREVIEW_CSS}\n{css}</style>\n')
    if mode != 'artifact':
        doc_head = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + doc_head + '</head><body>\n'
        tail = f'<script>{js}</script>\n{form_js}\n</body></html>\n'
    else:
        tail = f'<script>{js}</script>\n{form_js}\n'
    write(out, doc_head + page_body + '\n' + tail)
    print(f'preview ({mode}) -> {out} ({os.path.getsize(out)//1024} KB)')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('dist')
    d.add_argument('--sha', required=True)
    d.add_argument('--phone', default='')
    d.add_argument('--inline-css', action='store_true')
    p = sub.add_parser('preview')
    p.add_argument('--mode', choices=['local', 'artifact', 'cdn'], default='local')
    p.add_argument('--out', required=True)
    p.add_argument('--sha', default='')
    p.add_argument('--phone', default='')
    p.add_argument('--font', default='')
    a = ap.parse_args()
    if a.cmd == 'dist':
        build_dist(a.sha, a.phone, a.inline_css)
    else:
        build_preview(a.mode, a.out, a.sha, a.phone, a.font)


if __name__ == '__main__':
    main()
