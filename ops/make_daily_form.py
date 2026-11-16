"""하복당 바이저 일일관리 양식 (엑셀). A4 가로 한 장씩 인쇄되는 2개 보고 시트 + 입력/기준 시트.

시트
  일일보고          ① 지점별 매출 추이(자동) · 과일발주 · 특이사항/불만 · 보상/전표차감 · 플랫폼 계정 확인
  입출금            ② 지점별 당일 입금(상품명) · 출금 · 미수 · 로열티(월 단위) 입금여부
  매출입력          날짜·지점·채널별 매출을 매일 한 줄씩 입력 → 일일보고 매출 추이가 자동 계산
  지점목록          지점명 · 점주 · 연락처 · 월 로열티 (8개 지점)
  계정관리(인쇄금지) 배민/쿠팡이츠/네이버 아이디·비밀번호. 일일보고에는 아이디만 표시
  사용법

usage: python3 ops/make_daily_form.py <out.xlsx> [--sample]
"""
import sys, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter as CL

N_BR = 8                      # 지점 수 (지점목록 4~11행)
OR, INK, PALE, AUTO = 'F06A0F', '3A1705', 'FFE7CF', 'F4F1EE'
FN = '맑은 고딕'
thin = Side(style='thin', color='9C8E84')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WON = '#,##0;[Red]-#,##0;"-"'
PCT = '+0.0%;[Red]-0.0%;0.0%'
DATE = 'yyyy-mm-dd'
RED_FILL = PatternFill('solid', fgColor='FAD4D4')
BR_LIST = '=지점목록!$B$4:$B$11'


def put(ws, r, c, span=1, v=None, *, bold=False, size=9, color='000000', fill=None, h='center', fmt=None, wrap=True, border=True):
    if span > 1:
        ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + span - 1)
    for cc in range(c, c + span):
        x = ws.cell(r, cc)
        if border:
            x.border = BOX
        if fill:
            x.fill = PatternFill('solid', fgColor=fill)
    x = ws.cell(r, c)
    x.value = v
    x.font = Font(name=FN, size=size, bold=bold, color=color)
    x.alignment = Alignment(horizontal=h, vertical='center', wrap_text=wrap, shrink_to_fit=not wrap)
    if fmt:
        x.number_format = fmt
    return x


def header(ws, r, c0, cols):
    c = c0
    for name, span in cols:
        put(ws, r, c, span, name, bold=True, color='FFFFFF', fill=OR, size=9, wrap=False)
        c += span


def title(ws, r, c0, span, text):
    put(ws, r, c0, span, text, bold=True, size=10, color=INK, fill=PALE, h='left')


def a4_landscape(ws, last_row, last_col=20):
    ws.print_area = f'A1:{CL(last_col)}{last_row}'
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.page_margins.top = ws.page_margins.bottom = 0.35
    ws.page_margins.header = ws.page_margins.footer = 0.15
    ws.sheet_view.showGridLines = False
    for i in range(1, last_col + 1):
        ws.column_dimensions[CL(i)].width = 7.4


def dv_list(ws, formula, rng, allow_blank=True):
    dv = DataValidation(type='list', formula1=formula, allow_blank=allow_blank, showDropDown=False)
    ws.add_data_validation(dv)
    dv.add(rng)


def report_header(ws, name, sub):
    put(ws, 1, 1, 10, name, bold=True, size=15, color=INK, h='left', border=False)
    put(ws, 1, 11, 2, '보고일', bold=True, fill=PALE)
    put(ws, 1, 13, 3, None, bold=True, size=11, fmt=DATE)
    put(ws, 1, 16, 2, '담당 바이저', bold=True, fill=PALE)
    put(ws, 1, 18, 3, None, bold=True, size=11)
    put(ws, 2, 1, 20, sub, size=8, color='6B5A4E', h='left', border=False)
    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 14


def br(i):
    return f'=IF(지점목록!$B${4 + i}="","",지점목록!$B${4 + i})'


def build(sample=False):
    wb = Workbook()
    rep = wb.active; rep.title = '일일보고'
    cash = wb.create_sheet('입출금')
    sales = wb.create_sheet('매출입력')
    brs = wb.create_sheet('지점목록')
    acc = wb.create_sheet('계정관리(인쇄금지)')
    howto = wb.create_sheet('사용법')
    acc.sheet_properties.tabColor = 'C62828'
    rep.sheet_properties.tabColor = cash.sheet_properties.tabColor = OR

    # ------------------------------------------------------------- 지점목록
    put(brs, 1, 1, 7, '지점목록 — 여기 적은 지점명이 모든 보고서에 자동으로 들어갑니다', bold=True, size=12, color=INK, h='left', border=False)
    put(brs, 2, 1, 7, '월 로열티: 지점별 월 정액(원). 입출금 시트의 로열티 칸에 자동 표시됩니다.', size=9, color='6B5A4E', h='left', border=False)
    for c, (n, w) in enumerate((('번호', 6), ('지점명', 16), ('점주', 12), ('연락처', 16), ('오픈일', 12), ('월 로열티(원)', 14), ('비고', 24)), 1):
        put(brs, 3, c, 1, n, bold=True, color='FFFFFF', fill=OR)
        brs.column_dimensions[CL(c)].width = w
    for i in range(N_BR):
        r = 4 + i
        put(brs, r, 1, 1, i + 1)
        for c in range(2, 8):
            put(brs, r, c, 1, None, fmt=DATE if c == 5 else (WON if c == 6 else None))
    brs.freeze_panes = 'A4'

    # ------------------------------------------------------------- 계정관리(인쇄금지)
    put(acc, 1, 1, 10, '플랫폼 계정관리 — 인쇄·사진·메신저 공유 금지', bold=True, size=12, color='C62828', h='left', border=False)
    put(acc, 2, 1, 10, '일일보고에는 아이디만 표시됩니다. 비밀번호는 이 시트에만 두고, 바꾸면 최종 변경일을 적어주세요.', size=9, color='6B5A4E', h='left', border=False)
    cols = (('번호', 6), ('지점명', 14), ('배민 아이디', 16), ('배민 비밀번호', 16), ('쿠팡이츠 아이디', 16), ('쿠팡이츠 비밀번호', 16),
            ('네이버 아이디', 16), ('네이버 비밀번호', 16), ('최종 변경일', 12), ('비고', 18))
    for c, (n, w) in enumerate(cols, 1):
        put(acc, 3, c, 1, n, bold=True, color='FFFFFF', fill='C62828')
        acc.column_dimensions[CL(c)].width = w
    for i in range(N_BR):
        r = 4 + i
        put(acc, r, 1, 1, i + 1)
        put(acc, r, 2, 1, br(i), fill=AUTO)
        for c in range(3, 11):
            put(acc, r, c, 1, None, fmt=DATE if c == 9 else None)
    acc.print_area = 'A1:B2'

    # ------------------------------------------------------------- 매출입력
    put(sales, 1, 1, 8, '매출입력 — 매일 지점별로 한 줄씩 입력 (일일보고 매출 추이가 자동 계산)', bold=True, size=12, color=INK, h='left', border=False)
    put(sales, 2, 1, 8, '날짜·지점 필수. 채널 금액은 원 단위, 비어 있으면 0으로 봅니다. 합계는 자동.', size=9, color='6B5A4E', h='left', border=False)
    for c, (n, w) in enumerate((('날짜', 12), ('지점', 14), ('배민', 13), ('쿠팡이츠', 13), ('네이버·포장', 13), ('홀·기타', 13), ('합계(자동)', 14), ('메모', 24)), 1):
        put(sales, 3, c, 1, n, bold=True, color='FFFFFF', fill=OR)
        sales.column_dimensions[CL(c)].width = w
    N_ROWS = 1500
    for r in range(4, 4 + N_ROWS):
        sales.cell(r, 1).number_format = DATE
        for c in range(3, 7):
            sales.cell(r, c).number_format = WON
        g = sales.cell(r, 7, f'=IF(COUNT(C{r}:F{r})=0,"",SUM(C{r}:F{r}))')
        g.number_format = WON
        g.fill = PatternFill('solid', fgColor=AUTO)
    dv_list(sales, BR_LIST, f'B4:B{3 + N_ROWS}')
    dvd = DataValidation(type='date', operator='greaterThan', formula1='DATE(2020,1,1)', allow_blank=True)
    sales.add_data_validation(dvd); dvd.add(f'A4:A{3 + N_ROWS}')
    sales.freeze_panes = 'A4'

    # ------------------------------------------------------------- ① 일일보고
    ws = rep
    a4_landscape(ws, 36)
    report_header(ws, '하복당 지점관리 일일보고', '회색 칸은 자동 계산(입력 금지) · 흰 칸에 입력 · 매출은 「매출입력」 시트에 넣으면 아래 표가 자동으로 채워집니다')
    D = '$M$1'
    S = '매출입력!'
    r = 3
    title(ws, r, 1, 20, '① 지점별 매출 추이  (단위: 원 · 전일/전주 같은 요일 대비 · 월 누적)')
    r += 1
    header(ws, r, 1, [('지점', 2), ('배민', 2), ('쿠팡이츠', 2), ('네이버·포장', 2), ('홀·기타', 2), ('당일 합계', 2),
                      ('전일', 2), ('전일비', 1), ('전주 같은요일', 2), ('전주비', 1), ('월 누적', 2)])
    first = r + 1
    for i in range(N_BR):
        r += 1
        A = f'$A{r}'
        put(ws, r, 1, 2, br(i), bold=True, fill=AUTO)
        for c, col in ((3, 'C'), (5, 'D'), (7, 'E'), (9, 'F')):
            put(ws, r, c, 2, f'=IF({A}="","",SUMIFS({S}${col}:${col},{S}$A:$A,{D},{S}$B:$B,{A}))', fill=AUTO, fmt=WON, h='right')
        put(ws, r, 11, 2, f'=IF({A}="","",SUM(C{r},E{r},G{r},I{r}))', bold=True, fill=AUTO, fmt=WON, h='right')
        put(ws, r, 13, 2, f'=IF({A}="","",SUMIFS({S}$G:$G,{S}$A:$A,{D}-1,{S}$B:$B,{A}))', fill=AUTO, fmt=WON, h='right')
        put(ws, r, 15, 1, f'=IF(OR({A}="",N(M{r})=0),"",K{r}/M{r}-1)', fill=AUTO, fmt=PCT, h='right')
        put(ws, r, 16, 2, f'=IF({A}="","",SUMIFS({S}$G:$G,{S}$A:$A,{D}-7,{S}$B:$B,{A}))', fill=AUTO, fmt=WON, h='right')
        put(ws, r, 18, 1, f'=IF(OR({A}="",N(P{r})=0),"",K{r}/P{r}-1)', fill=AUTO, fmt=PCT, h='right')
        put(ws, r, 19, 2, f'=IF({A}="","",SUMIFS({S}$G:$G,{S}$B:$B,{A},{S}$A:$A,">="&DATE(YEAR({D}),MONTH({D}),1),{S}$A:$A,"<="&{D}))',
            fill=AUTO, fmt=WON, h='right')
    last = r
    r += 1
    put(ws, r, 1, 2, '합계', bold=True, fill=PALE)
    for c, col in ((3, 'C'), (5, 'E'), (7, 'G'), (9, 'I'), (11, 'K'), (13, 'M'), (16, 'P'), (19, 'S')):
        put(ws, r, c, 2, f'=SUM({col}{first}:{col}{last})', bold=True, fill=PALE, fmt=WON, h='right')
    put(ws, r, 15, 1, f'=IF(N(M{r})=0,"",K{r}/M{r}-1)', bold=True, fill=PALE, fmt=PCT, h='right')
    put(ws, r, 18, 1, f'=IF(N(P{r})=0,"",K{r}/P{r}-1)', bold=True, fill=PALE, fmt=PCT, h='right')
    for col in ('O', 'R'):
        ws.conditional_formatting.add(f'{col}{first}:{col}{r}', CellIsRule(operator='lessThan', formula=['-0.1'], fill=RED_FILL))

    # ② 과일발주 (좌) + ③ 특이사항·불만 (우)
    r += 1
    title(ws, r, 1, 11, '② 지점별 과일 발주량  (단위: 박스)')
    title(ws, r, 12, 9, '③ 지점별 특이사항 · 불만사항')
    r += 1
    header(ws, r, 1, [('지점', 2), ('딸기', 1), ('망고', 1), ('샤인', 1), ('멜론', 1), ('키위', 1), ('귤·오렌지', 1), ('기타', 1), ('발주금액(원)', 2)])
    header(ws, r, 12, [('지점', 2), ('구분', 1), ('내용', 4), ('조치 · 결과', 2)])
    f0 = r + 1
    for i in range(N_BR):
        r += 1
        put(ws, r, 1, 2, br(i), bold=True, fill=AUTO)
        for c in range(3, 10):
            put(ws, r, c, 1, None, fmt='#,##0.#;-#,##0.#;""')
        put(ws, r, 10, 2, None, fmt=WON, h='right')
        put(ws, r, 12, 2, None)
        put(ws, r, 14, 1, None)
        put(ws, r, 15, 4, None, h='left', size=8)
        put(ws, r, 19, 2, None, h='left', size=8)
    dv_list(ws, BR_LIST, f'L{f0}:L{r}')
    dv_list(ws, '"불만,특이,위생,시설,인력,기타"', f'N{f0}:N{r}')

    # ④ 보상·전표차감 (좌) + ⑤ 플랫폼 계정·전표 확인 (우)
    r += 1
    title(ws, r, 1, 11, '④ 보상 · 전표 차감 내역  (단위: 원)')
    title(ws, r, 12, 9, '⑤ 플랫폼 계정 · 전표 확인  (비밀번호는 「계정관리」 시트에만)')
    r += 1
    header(ws, r, 1, [('지점', 2), ('플랫폼', 1), ('주문번호', 2), ('사유', 2), ('보상액', 2), ('전표 차감액', 2)])
    header(ws, r, 12, [('지점', 2), ('배민 아이디', 2), ('쿠팡이츠 아이디', 2), ('네이버 아이디', 2), ('전표확인', 1)])
    c0 = r + 1
    AC = "'계정관리(인쇄금지)'!"
    for i in range(N_BR):
        r += 1
        L = f'$L{r}'
        put(ws, r, 12, 2, br(i), bold=True, fill=AUTO)
        for c, col in ((14, 'C'), (16, 'E'), (18, 'G')):
            put(ws, r, c, 2, f'=IF({L}="","",IFERROR(INDEX({AC}${col}$4:${col}$11,MATCH({L},{AC}$B$4:$B$11,0))&"",""))', fill=AUTO, size=8)
        put(ws, r, 20, 1, None)
        if i < N_BR - 1:
            put(ws, r, 1, 2, None)
            put(ws, r, 3, 1, None)
            put(ws, r, 4, 2, None, size=8)
            put(ws, r, 6, 2, None, h='left', size=8)
            put(ws, r, 8, 2, None, fmt=WON, h='right')
            put(ws, r, 10, 2, None, fmt=WON, h='right')
        else:
            put(ws, r, 1, 7, '합계', bold=True, fill=PALE)
            put(ws, r, 8, 2, f'=SUM(H{c0}:H{r - 1})', bold=True, fill=PALE, fmt=WON, h='right')
            put(ws, r, 10, 2, f'=SUM(J{c0}:J{r - 1})', bold=True, fill=PALE, fmt=WON, h='right')
    dv_list(ws, BR_LIST, f'A{c0}:A{r - 1}')
    dv_list(ws, '"배민,쿠팡이츠,네이버,기타"', f'C{c0}:C{r - 1}')
    dv_list(ws, '"O,X"', f'T{c0}:T{r}')
    ws.conditional_formatting.add(f'T{c0}:T{r}', CellIsRule(operator='equal', formula=['"X"'], fill=RED_FILL))

    r += 1
    put(ws, r, 1, 20, '다음 방문·점검 예정 지점:', h='left', size=9, bold=True)
    r += 1
    put(ws, r, 1, 4, '바이저 확인', bold=True, fill=PALE)
    put(ws, r, 5, 6, None)
    put(ws, r, 11, 4, '대표 확인', bold=True, fill=PALE)
    put(ws, r, 15, 6, None)
    ws.print_area = f'A1:T{r}'
    for rr in range(3, r + 1):
        ws.row_dimensions[rr].height = 17
    ws.row_dimensions[r].height = 24

    # ------------------------------------------------------------- ② 입출금
    ws = cash
    a4_landscape(ws, 40)
    report_header(ws, '하복당 지점 입출금 일일보고', '입금확인·로열티 입금여부는 O / X 로 표시 · X·미납은 빨간색 · 로열티는 월 단위(대상월 기준)')
    ws['M1'] = '=IF(일일보고!$M$1="","",일일보고!$M$1)'
    ws['R1'] = '=IF(일일보고!$R$1="","",일일보고!$R$1)'
    D = '$M$1'
    r = 3
    title(ws, r, 1, 10, '⑥ 지점별 당일 입금내역')
    title(ws, r, 11, 10, '⑦ 지점별 당일 출금내역')
    r += 1
    header(ws, r, 1, [('지점', 2), ('상품명 · 내용', 3), ('수량', 1), ('금액(원)', 2), ('입금확인', 1), ('비고', 1)])
    header(ws, r, 11, [('지점', 2), ('출금 내역', 3), ('거래처', 2), ('금액(원)', 2), ('비고', 1)])
    i0 = r + 1
    N_IO = 12
    for i in range(N_IO):
        r += 1
        put(ws, r, 1, 2, None); put(ws, r, 3, 3, None, h='left', size=8); put(ws, r, 6, 1, None, fmt='#,##0;-#,##0;""')
        put(ws, r, 7, 2, None, fmt=WON, h='right'); put(ws, r, 9, 1, None); put(ws, r, 10, 1, None, size=8)
        put(ws, r, 11, 2, None); put(ws, r, 13, 3, None, h='left', size=8); put(ws, r, 16, 2, None, size=8)
        put(ws, r, 18, 2, None, fmt=WON, h='right'); put(ws, r, 20, 1, None, size=8)
    i1 = r
    r += 1
    put(ws, r, 1, 6, '입금 합계', bold=True, fill=PALE)
    put(ws, r, 7, 2, f'=SUM(G{i0}:G{i1})', bold=True, fill=PALE, fmt=WON, h='right')
    put(ws, r, 9, 2, None, fill=PALE)
    put(ws, r, 11, 7, '출금 합계', bold=True, fill=PALE)
    put(ws, r, 18, 2, f'=SUM(R{i0}:R{i1})', bold=True, fill=PALE, fmt=WON, h='right')
    put(ws, r, 20, 1, None, fill=PALE)
    in_tot, out_tot = f'G{r}', f'R{r}'
    dv_list(ws, BR_LIST, f'A{i0}:A{i1}')
    dv_list(ws, BR_LIST, f'K{i0}:K{i1}')
    dv_list(ws, '"O,X"', f'I{i0}:I{i1}')
    ws.conditional_formatting.add(f'I{i0}:I{i1}', CellIsRule(operator='equal', formula=['"X"'], fill=RED_FILL))

    r += 1
    title(ws, r, 1, 10, '⑧ 미수내역  (경과일 자동)')
    title(ws, r, 11, 10, '⑨ 로열티 — 월 단위  (대상월을 적으면 미납액 자동 계산)')
    r += 1
    header(ws, r, 1, [('지점', 2), ('상품명 · 내용', 3), ('금액(원)', 2), ('발생일', 1), ('입금예정일', 1), ('경과일', 1)])
    header(ws, r, 11, [('지점', 2), ('대상월', 1), ('로열티(원)', 2), ('입금여부', 1), ('입금일', 1), ('미납액', 2), ('비고', 1)])
    m0 = r + 1
    for i in range(N_BR):
        r += 1
        put(ws, r, 1, 2, None); put(ws, r, 3, 3, None, h='left', size=8)
        put(ws, r, 6, 2, None, fmt=WON, h='right'); put(ws, r, 8, 1, None, fmt='mm-dd', size=8); put(ws, r, 9, 1, None, fmt='mm-dd', size=8)
        put(ws, r, 10, 1, f'=IF(OR(H{r}="",{D}=""),"",{D}-H{r})', fill=AUTO, fmt='0"일";-0"일";"당일"', size=8)
        put(ws, r, 11, 2, br(i), bold=True, fill=AUTO)
        put(ws, r, 13, 1, None, fmt='yy"년" m"월"', size=8)
        put(ws, r, 14, 2, f'=IF(K{r}="","",IFERROR(INDEX(지점목록!$F$4:$F$11,MATCH(K{r},지점목록!$B$4:$B$11,0)),""))', fill=AUTO, fmt=WON, h='right')
        put(ws, r, 16, 1, None)
        put(ws, r, 17, 1, None, fmt='mm-dd', size=8)
        put(ws, r, 18, 2, f'=IF(OR(N(N{r})=0,M{r}=""),"",IF(P{r}="O",0,N{r}))', fill=AUTO, fmt=WON, h='right')
        put(ws, r, 20, 1, None, size=8)
    m1 = r
    r += 1
    put(ws, r, 1, 5, '미수 합계', bold=True, fill=PALE)
    put(ws, r, 6, 2, f'=SUM(F{m0}:F{m1})', bold=True, fill=PALE, fmt=WON, h='right')
    put(ws, r, 8, 3, None, fill=PALE)
    put(ws, r, 11, 7, '로열티 미납 합계', bold=True, fill=PALE)
    put(ws, r, 18, 2, f'=SUM(R{m0}:R{m1})', bold=True, fill=PALE, fmt=WON, h='right')
    put(ws, r, 20, 1, None, fill=PALE)
    mi_tot, roy_tot = f'F{r}', f'R{r}'
    dv_list(ws, BR_LIST, f'A{m0}:A{m1}')
    dv_list(ws, '"O,X"', f'P{m0}:P{m1}')
    ws.conditional_formatting.add(f'P{m0}:P{m1}', CellIsRule(operator='equal', formula=['"X"'], fill=RED_FILL))
    ws.conditional_formatting.add(f'R{m0}:R{m1}', CellIsRule(operator='greaterThan', formula=['0'], fill=RED_FILL))
    ws.conditional_formatting.add(f'J{m0}:J{m1}', FormulaRule(formula=[f'AND(ISNUMBER(J{m0}),J{m0}>=7)'], fill=RED_FILL))

    r += 1
    title(ws, r, 1, 20, '⑩ 오늘 요약')
    r += 1
    for k, (lab, f) in enumerate((('당일 입금', f'={in_tot}'), ('당일 출금', f'={out_tot}'), ('입금 - 출금', f'={in_tot}-{out_tot}'),
                                  ('미수 잔액', f'={mi_tot}'), ('로열티 미납', f'={roy_tot}'))):
        put(ws, r, 1 + k * 4, 2, lab, bold=True, fill=PALE)
        put(ws, r, 3 + k * 4, 2, f, bold=True, fmt=WON, h='right', fill=AUTO)
    r += 1
    put(ws, r, 1, 20, '※ 로열티: 매월 대상월을 적고 입금 확인 시 O. 미납(X)은 다음 달까지 매일 보고서에 남겨 관리합니다.  ※ 미수 7일 이상 경과 시 빨간색.',
        size=8, color='6B5A4E', h='left', border=False)
    r += 1
    put(ws, r, 1, 4, '바이저 확인', bold=True, fill=PALE)
    put(ws, r, 5, 6, None)
    put(ws, r, 11, 4, '대표 확인', bold=True, fill=PALE)
    put(ws, r, 15, 6, None)
    ws.print_area = f'A1:T{r}'
    for rr in range(3, r + 1):
        ws.row_dimensions[rr].height = 17
    ws.row_dimensions[r].height = 24

    # ------------------------------------------------------------- 사용법
    howto.column_dimensions['A'].width = 110
    lines = [
        ('하복당 바이저 일일관리 양식 — 사용법', True),
        ('', False),
        ('처음 한 번', True),
        ('1. 「지점목록」에 담당 지점명·점주·연락처·월 로열티를 적습니다. (최대 8개 지점)', False),
        ('2. 「계정관리(인쇄금지)」에 배민·쿠팡이츠·네이버 아이디와 비밀번호를 적습니다. 일일보고에는 아이디만 나옵니다.', False),
        ('', False),
        ('매일', True),
        ('1. 「매출입력」에 날짜·지점·채널별 매출을 지점마다 한 줄씩 입력합니다.', False),
        ('2. 「일일보고」 맨 위 보고일과 담당 바이저를 적습니다. → ① 매출 추이(전일·전주 같은 요일·월 누적)가 자동으로 채워집니다.', False),
        ('3. ② 과일 발주량, ③ 특이사항·불만, ④ 보상·전표 차감, ⑤ 전표확인(O/X)을 입력합니다.', False),
        ('4. 「입출금」에 ⑥ 입금(상품명), ⑦ 출금, ⑧ 미수, ⑨ 로열티 입금여부를 입력합니다. 보고일은 일일보고에서 자동으로 따라옵니다.', False),
        ('5. 「일일보고」와 「입출금」을 각각 A4 가로 1장으로 인쇄합니다. (인쇄 설정이 한 페이지에 맞춰져 있음)', False),
        ('6. 매일 파일을 「하복당_일일보고_YYYY-MM-DD.xlsx」로 따로 저장하면 지난 기록이 남습니다. 매출입력 시트는 계속 이어서 씁니다.', False),
        ('', False),
        ('표시 규칙', True),
        ('· 회색 칸: 자동 계산(입력하지 마세요)   · 흰 칸: 입력   · 빨간 칸: 전일·전주 대비 -10% 이하, 입금 X, 로열티 미납, 미수 7일 이상', False),
        ('· 로열티는 월 단위입니다. 대상월을 적고 입금되면 O, 안 되면 X. 미납액은 자동 계산됩니다.', False),
        ('', False),
        ('보안', True),
        ('· 「계정관리(인쇄금지)」 시트는 인쇄·사진·메신저로 보내지 마세요. 파일에 암호를 걸어 두는 것을 권장합니다 (파일 → 정보 → 통합 문서 보호 → 암호 설정).', False),
    ]
    for i, (t, b) in enumerate(lines, 1):
        c = howto.cell(i, 1, t)
        c.font = Font(name=FN, size=13 if i == 1 else 10, bold=b, color=INK if b else '000000')
        c.alignment = Alignment(wrap_text=True, vertical='center')

    if sample:
        names = ['서현점', '구의점', '안양점', '송파문정점', '경기광주점', '분당정자점', '', '']
        for i, n in enumerate(names):
            brs.cell(4 + i, 2, n or None)
            if n:
                brs.cell(4 + i, 6, 500000)
                acc.cell(4 + i, 3, f'bm_{i}')
                acc.cell(4 + i, 5, f'cp_{i}')
                acc.cell(4 + i, 7, f'nv_{i}')
        d0 = dt.date(2026, 11, 16)
        rr = 4
        for back in range(0, 17):
            d = d0 - dt.timedelta(days=back)
            for i, n in enumerate(names):
                if not n:
                    continue
                sales.cell(rr, 1, d); sales.cell(rr, 2, n)
                base = 600000 + i * 80000 + back * 3000
                sales.cell(rr, 3, base); sales.cell(rr, 4, base // 2); sales.cell(rr, 5, 120000); sales.cell(rr, 6, 50000)
                rr += 1
        rep['M1'] = d0
        rep['R1'] = '홍길동'
        cash['M20'] = dt.date(2026, 11, 1); cash['P20'] = 'O'; cash['Q20'] = dt.date(2026, 11, 10); cash['M21'] = dt.date(2026, 11, 1); cash['P21'] = 'X'
        cash['A5'] = '서현점'; cash['C5'] = '딸기 요거트모찌 단체주문'; cash['F5'] = 30; cash['G5'] = 135000; cash['I5'] = 'O'
        cash['K5'] = '구의점'; cash['M5'] = '과일 추가발주'; cash['P5'] = '명가'; cash['R5'] = 220000
        cash['A20'] = '안양점'; cash['C20'] = '케이터링 잔금'; cash['F20'] = 80000; cash['H20'] = dt.date(2026, 11, 5)
    wb.active = 0
    return wb


if __name__ == '__main__':
    out = sys.argv[1]
    build(sample='--sample' in sys.argv).save(out)
    print('saved', out)
