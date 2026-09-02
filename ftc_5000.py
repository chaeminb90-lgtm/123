#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공정위 가맹정보 오픈API 수집 + 조인 + 창업비 5천만원 이하 필터

사용법:
  1) data.go.kr 인증키를 환경변수로 넣는다 (키는 절대 이 파일에 적지 말 것):
       export FTC_SERVICE_KEY='발급받은키'
     또는 같은 폴더에 .ftc_key 파일을 만들고 키만 한 줄 적어둔다.
     인코딩키(%2F, %3D 포함) / 디코딩키(+, /, =) 둘 다 인식한다.
  2) pip install requests
  3) python3 ftc_5000.py

출력:
  ftc_창업금액_원본_<연도>.csv
  ftc_가맹점현황_원본_<연도>.csv
  ftc_5천이하_결과_<연도>.csv   <- 이걸 보면 됨

연도는 YEAR=""면 2025→2024→... 순으로 자동탐지한다.
"""

import csv
import os
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlencode

import requests

# ============================================================
# 1. 엔드포인트 (공개 정보라 하드코딩. 인증키만 환경변수)
# ============================================================
EP_CREATION = "https://apis.data.go.kr/1130000/FftcBrandFntnStatsService/getBrandFntnStats"          # 브랜드별 창업비용
EP_STORE    = "https://apis.data.go.kr/1130000/FftcBrandFrcsStatsService/getBrandFrcsStats"          # 브랜드별 가맹점현황
EP_INDUTY_FRCS = "https://apis.data.go.kr/1130000/FftcBrandIndutyDropFrcsStatsService/getBrandIndutyFrcsStats"  # 업종별 가맹점수 구간
EP_INDUTY_DROP = "https://apis.data.go.kr/1130000/FftcBrandIndutyDropFrcsStatsService/getBrandIndutyDropStats"  # 업종별 폐점수 구간

YEAR = ""              # "" = 자동탐지(최신연도 우선). "2024"처럼 직접 지정도 가능
YEAR_CANDIDATES = ["2025", "2024", "2023", "2022", "2021"]  # 앞에서부터 시도
ROWS_PER_PAGE = 1000   # 너무 크면 거부하는 경우 있음. 실패하면 500 → 100 순으로 낮추기

# ============================================================
# 2. 필터 조건 — 여기만 바꾸면 기준이 달라집니다
# ============================================================
MAX_COST = 50000       # 창업비용 상한 (천원). 50000 = 5,000만원
MIN_STORES = 30        # 최소 가맹점 수. 검증 안 된 신생 브랜드 제외
MAX_CLOSE_RATE = 0.15  # 폐점률 상한 (15%)
REQUIRE_SALES = True   # 평균매출 미공시(0) 브랜드 제외. False로 두면 회수개월이 0으로 찍혀 오해 유발

# ---- 추천 5개 뽑기 조건 ----
MIN_MONTH_PROFIT = 5000   # 추정 월영업이익 하한 (천원). 5000 = 500만원
#   주의: 외식 비용률 75% 가정이므로 월 500만원 = 월매출 2,000만원(연 2.4억) 이상이라는 뜻
PICK_MLSFC = "한식"       # 업종중분류. "" 로 두면 업종 제한 없음
PICK_TOP_N = 5            # 몇 개 뽑을지
PICK_SORT = "회수개월_추정"  # 정렬 기준. "추정월영업이익_만원"으로 바꾸면 순이익 큰 순

# 추정 영업이익 가정 — 화면에 반드시 같이 표기할 것
COST_RATIO = {         # 매출 대비 비용 비율 합계
    "외식":   0.75,    # 원재료38 + 임차10 + 인건20 + 로열티·기타7 → 영업이익률 약 25%
    "도소매": 0.85,
    "서비스": 0.70,
}
DEFAULT_COST_RATIO = 0.78


def load_key() -> str:
    """환경변수 또는 .ftc_key에서 인증키를 읽어 URL에 넣을 수 있는 형태로 반환."""
    key = os.environ.get("FTC_SERVICE_KEY", "").strip()
    if not key:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ftc_key")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                key = f.read().strip()
    if not key:
        sys.exit(
            "[중단] 인증키가 없습니다.\n"
            "  export FTC_SERVICE_KEY='발급받은키'   또는   .ftc_key 파일에 키 한 줄"
        )
    # '%'가 있으면 이미 인코딩된 키로 보고 그대로, 아니면 인코딩한다.
    return key if "%" in key else quote(key, safe="")


SERVICE_KEY = ""   # main()에서 채움


def build_url(endpoint: str, params: dict) -> str:
    """serviceKey는 이미 인코딩돼 있으므로 재인코딩하지 않고 직접 붙인다."""
    rest = urlencode({k: v for k, v in params.items() if k != "serviceKey"})
    return f"{endpoint}?serviceKey={SERVICE_KEY}&{rest}"


def _request(endpoint: str, params: dict, label: str):
    """1회 호출 후 XML 루트 반환. 에러면 중단."""
    url = build_url(endpoint, params)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        sys.exit(f"[중단] {label} 응답이 XML이 아닙니다. 앞부분:\n{r.text[:400]}")
    code = root.findtext(".//resultCode")
    if code not in (None, "00"):
        sys.exit(f"[중단] {label} 에러 {code}: {root.findtext('.//resultMsg')}")
    return root


def probe_count(endpoint: str, year: str, label: str) -> int:
    """해당 연도의 totalCount만 가볍게 조회. 호출 실패는 0으로 처리."""
    try:
        root = _request(endpoint, {"yr": year, "pageNo": "1", "numOfRows": "1"}, label)
    except (requests.RequestException, SystemExit):
        return 0
    return int(root.findtext(".//totalCount") or 0)


def detect_year(eps_with_labels) -> str:
    """두 데이터셋 모두에 자료가 있는 가장 최신 연도를 찾는다."""
    if YEAR:
        print(f"  연도 고정: {YEAR}")
        return YEAR
    print("  연도 자동탐지 (최신부터)")
    for y in YEAR_CANDIDATES:
        counts = [probe_count(ep, y, lb) for ep, lb in eps_with_labels]
        state = " / ".join(f"{lb} {c:,}건" for (_, lb), c in zip(eps_with_labels, counts))
        print(f"    {y}: {state}")
        if all(c > 0 for c in counts):
            print(f"  -> {y}년 사용")
            return y
    sys.exit(f"[중단] {YEAR_CANDIDATES} 중 두 데이터셋이 모두 있는 연도가 없습니다.")


def fetch_all(endpoint: str, label: str, year: str):
    """전 페이지를 순회하며 dict 리스트로 반환."""
    params = {"yr": year, "numOfRows": str(ROWS_PER_PAGE)}

    rows, page, total = [], 1, None
    while True:
        params["pageNo"] = str(page)
        root = _request(endpoint, params, label)

        if total is None:
            total = int(root.findtext(".//totalCount") or 0)
            print(f"  {label}: 총 {total}건")

        items = root.findall(".//items/item")
        if not items:
            break
        for it in items:
            rows.append({child.tag: (child.text or "").strip() for child in it})

        print(f"  {label}: {len(rows)}/{total}", end="\r")
        if len(rows) >= total:
            break
        page += 1
        time.sleep(0.2)

    print(f"  {label}: {len(rows)}건 수집 완료   ")
    return rows


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def write_csv(rows, path):
    if not rows:
        return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path}")


def main():
    global SERVICE_KEY
    SERVICE_KEY = load_key()

    print("[1/3] 수집")
    year = detect_year([(EP_CREATION, "창업금액"), (EP_STORE, "가맹점현황")])
    cost_rows = fetch_all(EP_CREATION, "창업금액", year)
    store_rows = fetch_all(EP_STORE, "가맹점현황", year)

    # 업종별 집계 2종은 조인에 쓰지 않고 참고용으로 그대로 저장
    for ep, lb, fn in [(EP_INDUTY_FRCS, "업종별가맹점수", "ftc_업종별_가맹점수구간"),
                       (EP_INDUTY_DROP, "업종별폐점수", "ftc_업종별_폐점수구간")]:
        try:
            write_csv(fetch_all(ep, lb, year), f"{fn}_{year}.csv")
        except (requests.RequestException, SystemExit) as e:
            print(f"  [건너뜀] {lb}: {e}")

    write_csv(cost_rows, f"ftc_창업금액_원본_{year}.csv")
    write_csv(store_rows, f"ftc_가맹점현황_원본_{year}.csv")

    print("[2/3] 조인")
    # 브랜드명 + 상호명으로 매칭 (동명 브랜드 충돌 방지)
    store_idx = {}
    for s in store_rows:
        store_idx[(s.get("brandNm", ""), s.get("corpNm", ""))] = s

    merged = []
    for c in cost_rows:
        s = store_idx.get((c.get("brandNm", ""), c.get("corpNm", "")))
        if not s:
            s = {}

        cost = to_int(c.get("smtnAmt"))
        stores = to_int(s.get("frcsCnt"))
        ended = to_int(s.get("ctrtEndCnt")) + to_int(s.get("ctrtCncltnCnt"))
        sales_yr = to_int(s.get("avrgSlsAmt"))
        sales_ar = to_int(s.get("arUnitAvrgSlsAmt"))

        close_rate = ended / (stores + ended) if (stores + ended) else 0.0
        # arUnitAvrgSlsAmt는 '면적(3.3㎡)당' 매출이므로 나눈 값이 곧 평수다.
        # ㎡로 보고 3.3058로 한 번 더 나누면 실제의 1/3.3이 된다.
        pyeong = sales_yr / sales_ar if sales_ar else 0.0

        lclas = c.get("indutyLclasNm", "")
        ratio = COST_RATIO.get(lclas, DEFAULT_COST_RATIO)
        month_sales = sales_yr / 12
        month_profit = month_sales * (1 - ratio)
        payback = (cost / month_profit) if month_profit > 0 else 0.0

        merged.append({
            "브랜드": c.get("brandNm", ""),
            "본사": c.get("corpNm", ""),
            "업종대": lclas,
            "업종중": c.get("indutyMlsfcNm", ""),
            "창업비용_만원": round(cost / 10),
            "  가맹금_만원": round(to_int(c.get("jngBzmnJngAmt")) / 10),
            "  교육비_만원": round(to_int(c.get("jngBzmnEduAmt")) / 10),
            "  보증금_만원": round(to_int(c.get("jngBzmnAssrncAmt")) / 10),
            "  기타_만원": round(to_int(c.get("jngBzmnEtcAmt")) / 10),
            "가맹점수": stores,
            "계약종료해지": ended,
            "폐점률": round(close_rate * 100, 1),
            "연매출_만원": round(sales_yr / 10),
            "월매출_만원": round(month_sales / 10),
            "추정평수": round(pyeong, 1),
            "추정월영업이익_만원": round(month_profit / 10),
            "회수개월_추정": round(payback, 1),
        })

    print("[3/3] 필터")
    result = [
        m for m in merged
        if 0 < m["창업비용_만원"] * 10 < MAX_COST
        and m["가맹점수"] >= MIN_STORES
        and m["폐점률"] <= MAX_CLOSE_RATE * 100
        and (m["연매출_만원"] > 0 if REQUIRE_SALES else True)
    ]
    result.sort(key=lambda x: x["창업비용_만원"])

    write_csv(result, f"ftc_5천이하_결과_{year}.csv")
    print(f"\n조건 통과: {len(result)}개 / 전체 {len(merged)}개")
    cond = f"조건: {year}년 · 창업비 {MAX_COST//10}만원 미만 · 가맹점 {MIN_STORES}개 이상 · 폐점률 {MAX_CLOSE_RATE*100:.0f}% 이하"
    if REQUIRE_SALES:
        cond += " · 평균매출 공시"
    print(cond)
    print("주의: 창업비용은 가맹본부 지급분(가맹금·교육비·보증금·기타) 합계입니다.")
    print("      점포 임차보증금·권리금은 포함되지 않으므로 실제 소요자금은 이보다 큽니다.")
    print("      영업이익·회수개월은 업종별 비용률 가정에 따른 추정치입니다.\n")

    for m in result[:20]:
        print(f"  {m['창업비용_만원']:>6,}만원 | 점포 {m['가맹점수']:>4} | 폐점 {m['폐점률']:>4.1f}% | "
              f"월매출 {m['월매출_만원']:>6,}만원 | {m['브랜드']}")

    # ------------------------------------------------------------
    # 추천 N개: 순이익 하한 + 업종중분류 조건 추가
    # ------------------------------------------------------------
    picks = [
        m for m in result
        if m["추정월영업이익_만원"] * 10 >= MIN_MONTH_PROFIT
        and (m["업종중"] == PICK_MLSFC if PICK_MLSFC else True)
    ]
    # 회수개월은 짧을수록, 그 외 지표는 클수록 좋다
    picks.sort(key=lambda x: x[PICK_SORT], reverse=(PICK_SORT != "회수개월_추정"))
    picks = picks[:PICK_TOP_N]

    label = f"{PICK_MLSFC} " if PICK_MLSFC else ""
    print("\n" + "=" * 62)
    print(f"추천 {label}브랜드 {len(picks)}개"
          f"  (창업비 {MAX_COST//10:,}만원 미만 · 추정 월순익 {MIN_MONTH_PROFIT//10:,}만원 이상)")
    print(f"정렬: {PICK_SORT}")
    print("=" * 62)

    if not picks:
        print("조건을 만족하는 브랜드가 없습니다. MIN_STORES나 MIN_MONTH_PROFIT을 낮춰보세요.")
    for i, m in enumerate(picks, 1):
        print(f"\n[{i}] {m['브랜드']}")
        for k, v in m.items():
            if k == "브랜드":
                continue
            key = k.strip()
            mark = "   └ " if k.startswith("  ") else " "
            print(f"{mark}{key:<14}: {v:,}" if isinstance(v, (int, float)) else f"{mark}{key:<14}: {v}")

    write_csv(picks, f"ftc_추천_{PICK_MLSFC or '전체'}_{year}.csv")

    print("\n" + "-" * 62)
    print("추정월영업이익 = 월매출 x (1 - 업종별 비용률). 공정위 데이터에 영업이익은 없습니다.")
    print(f"적용 비용률: 외식 {COST_RATIO['외식']:.0%} / 도소매 {COST_RATIO['도소매']:.0%} "
          f"/ 서비스 {COST_RATIO['서비스']:.0%} (그 외 {DEFAULT_COST_RATIO:.0%})")
    print("점포별 임차료·인건비 편차가 커서 실제 수익은 브랜드가 아니라 입지가 좌우합니다.")


if __name__ == "__main__":
    main()
