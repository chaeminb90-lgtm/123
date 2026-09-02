#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공정위 가맹정보 오픈API 수집 + 조인 + 창업비 5천만원 이하 필터

사용법:
  1) 아래 URL_CREATION / URL_STORE 두 줄에 '미리보기' 주소창 URL을 그대로 붙여넣는다
     (serviceKey 포함된 전체 URL. pageNo/numOfRows는 스크립트가 알아서 덮어씀)
  2) pip install requests
  3) python3 ftc_5000.py

출력:
  ftc_창업금액_원본.csv
  ftc_가맹점현황_원본.csv
  ftc_5천이하_결과.csv   <- 이걸 보면 됨
"""

import csv
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests

# ============================================================
# 1. 여기 두 줄만 채우세요 (미리보기 창의 주소 전체)
# ============================================================
URL_CREATION = "여기에_창업금액_미리보기_URL_붙여넣기"      # 15110265
URL_STORE    = "여기에_가맹점현황_미리보기_URL_붙여넣기"    # 15110241

YEAR = "2021"          # 통하는 최신 연도로 바꾸세요 (2022~2025 시도)
ROWS_PER_PAGE = 1000   # 너무 크면 거부하는 경우 있음. 실패하면 500 → 100 순으로 낮추기

# ============================================================
# 2. 필터 조건 — 여기만 바꾸면 기준이 달라집니다
# ============================================================
MAX_COST = 50000       # 창업비용 상한 (천원). 50000 = 5,000만원
MIN_STORES = 30        # 최소 가맹점 수. 검증 안 된 신생 브랜드 제외
MAX_CLOSE_RATE = 0.15  # 폐점률 상한 (15%)

# 추정 영업이익 가정 — 화면에 반드시 같이 표기할 것
COST_RATIO = {         # 매출 대비 비용 비율 합계
    "외식":   0.75,    # 원재료38 + 임차10 + 인건20 + 로열티·기타7 → 영업이익률 약 25%
    "도소매": 0.85,
    "서비스": 0.70,
}
DEFAULT_COST_RATIO = 0.78


def fetch_all(base_url: str, label: str):
    """미리보기 URL을 받아 전 페이지를 순회하며 dict 리스트로 반환."""
    if base_url.startswith("여기에"):
        sys.exit(f"[중단] {label} URL을 먼저 채워주세요.")

    parts = urlparse(base_url)
    params = {k: v[0] for k, v in parse_qs(parts.query).items()}
    params["numOfRows"] = str(ROWS_PER_PAGE)
    if "yr" in params:
        params["yr"] = YEAR

    rows, page, total = [], 1, None
    while True:
        params["pageNo"] = str(page)
        url = urlunparse(parts._replace(query=urlencode(params, safe="%")))
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        try:
            root = ET.fromstring(r.text)
        except ET.ParseError:
            sys.exit(f"[중단] {label} 응답이 XML이 아닙니다. 앞부분:\n{r.text[:400]}")

        code = root.findtext(".//resultCode")
        if code not in (None, "00"):
            sys.exit(f"[중단] {label} 에러 {code}: {root.findtext('.//resultMsg')}")

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
    print("[1/3] 수집")
    cost_rows = fetch_all(URL_CREATION, "창업금액")
    store_rows = fetch_all(URL_STORE, "가맹점현황")

    write_csv(cost_rows, "ftc_창업금액_원본.csv")
    write_csv(store_rows, "ftc_가맹점현황_원본.csv")

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
        area_m2 = sales_yr / sales_ar if sales_ar else 0.0

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
            "추정평수": round(area_m2 / 3.3058, 1),
            "추정월영업이익_만원": round(month_profit / 10),
            "회수개월_추정": round(payback, 1),
        })

    print("[3/3] 필터")
    result = [
        m for m in merged
        if 0 < m["창업비용_만원"] * 10 < MAX_COST
        and m["가맹점수"] >= MIN_STORES
        and m["폐점률"] <= MAX_CLOSE_RATE * 100
    ]
    result.sort(key=lambda x: x["창업비용_만원"])

    write_csv(result, "ftc_5천이하_결과.csv")
    print(f"\n조건 통과: {len(result)}개 / 전체 {len(merged)}개")
    print(f"조건: 창업비 {MAX_COST//10}만원 미만 · 가맹점 {MIN_STORES}개 이상 · 폐점률 {MAX_CLOSE_RATE*100:.0f}% 이하\n")

    for m in result[:20]:
        print(f"  {m['창업비용_만원']:>6,}만원 | 점포 {m['가맹점수']:>4} | 폐점 {m['폐점률']:>4.1f}% | "
              f"월매출 {m['월매출_만원']:>6,}만원 | {m['브랜드']}")


if __name__ == "__main__":
    main()
