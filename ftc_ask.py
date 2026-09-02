#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
저장된 공정위 원본 CSV에 조건을 걸어 브랜드를 뽑는 도구. (네트워크 불필요)

전제: ftc_5000.py를 한 번 돌려서 아래 두 파일이 있어야 한다.
  ftc_창업금액_원본_<연도>.csv
  ftc_가맹점현황_원본_<연도>.csv

예시:
  python3 ftc_ask.py                                   # 5천 미만 · 순익 500 이상 · 한식 5개
  python3 ftc_ask.py --mlsfc 치킨 --top 10             # 치킨 10개
  python3 ftc_ask.py --max-cost 3000 --min-profit 300  # 3천 미만 · 순익 300 이상
  python3 ftc_ask.py --lclas 서비스 --mlsfc ""          # 서비스업 전체
  python3 ftc_ask.py --list-mlsfc                      # 업종중분류 목록 보기
  python3 ftc_ask.py --sort 추정월영업이익_만원          # 순익 큰 순
"""

import argparse
import csv
import signal
import glob
import os
import re
import sys

from ftc_5000 import merge, write_csv, COST_RATIO, DEFAULT_COST_RATIO

HERE = os.path.dirname(os.path.abspath(__file__))


def load_year(year=None):
    """저장된 원본 CSV 쌍 중 지정연도(없으면 최신)를 읽어 반환."""
    pat = os.path.join(HERE, "ftc_창업금액_원본_*.csv")
    years = sorted(re.search(r"_(\d{4})\.csv$", p).group(1)
                   for p in glob.glob(pat) if re.search(r"_(\d{4})\.csv$", p))
    if not years:
        sys.exit("[중단] ftc_창업금액_원본_<연도>.csv 가 없습니다.\n"
                 "  먼저 인터넷 되는 PC에서 python3 ftc_5000.py 를 한 번 실행하세요.")
    year = year or years[-1]
    if year not in years:
        sys.exit(f"[중단] {year}년 파일이 없습니다. 있는 연도: {', '.join(years)}")

    def read(path):
        if not os.path.exists(path):
            sys.exit(f"[중단] {os.path.basename(path)} 가 없습니다.")
        with open(path, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    cost = read(os.path.join(HERE, f"ftc_창업금액_원본_{year}.csv"))
    store = read(os.path.join(HERE, f"ftc_가맹점현황_원본_{year}.csv"))
    return year, cost, store


def main():
    p = argparse.ArgumentParser(description="공정위 가맹정보 조건 검색")
    p.add_argument("--year")
    p.add_argument("--max-cost", type=int, default=5000, help="창업비 상한(만원). 기본 5000")
    p.add_argument("--min-profit", type=int, default=500, help="추정 월순익 하한(만원). 기본 500")
    p.add_argument("--min-stores", type=int, default=30, help="최소 가맹점수. 기본 30")
    p.add_argument("--max-close", type=float, default=15.0, help="폐점률 상한(%%). 기본 15")
    p.add_argument("--lclas", default="", help="업종대분류 (외식/도소매/서비스)")
    p.add_argument("--mlsfc", default="한식", help='업종중분류. ""면 전체')
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--sort", default="회수개월_추정")
    p.add_argument("--min-etc", type=int, default=1000,
                   help="기타(인테리어·설비) 최소액(만원). 기본 1000. "
                        "이하는 창업비 공시가 불완전해 회수개월이 왜곡됨. 0이면 필터 해제")
    p.add_argument("--list-mlsfc", action="store_true", help="업종중분류 목록만 출력")
    p.add_argument("--stats", action="store_true",
                   help="기타(인테리어·설비) 공시 분포만 출력. 임계값 정하는 근거로 사용")
    a = p.parse_args()

    year, cost_rows, store_rows = load_year(a.year)
    rows = merge(cost_rows, store_rows)
    print(f"{year}년 · 원본 {len(rows):,}건 로드")

    if a.list_mlsfc:
        seen = {}
        for r in rows:
            seen.setdefault((r["업종대"], r["업종중"]), 0)
            seen[(r["업종대"], r["업종중"])] += 1
        for (lc, mc), n in sorted(seen.items(), key=lambda x: -x[1]):
            print(f"  {lc:<6} {mc:<14} {n:>5,}건")
        return

    dropped = [r for r in rows
               if 0 < r["창업비용_만원"] <= a.max_cost
               and r["추정월영업이익_만원"] >= a.min_profit
               and r["가맹점수"] >= a.min_stores
               and r["폐점률"] <= a.max_close
               and r["연매출_만원"] > 0
               and r["  기타_만원"] < a.min_etc
               and (r["업종대"] == a.lclas if a.lclas else True)
               and (r["업종중"] == a.mlsfc if a.mlsfc else True)]

    if a.stats:
        base = [r for r in rows
                if 0 < r["창업비용_만원"] <= a.max_cost
                and r["가맹점수"] >= a.min_stores
                and r["폐점률"] <= a.max_close
                and r["연매출_만원"] > 0
                and (r["업종대"] == a.lclas if a.lclas else True)
                and (r["업종중"] == a.mlsfc if a.mlsfc else True)]
        print(f"창업비 {a.max_cost:,}만원 이하 기본조건 통과 {len(base):,}건의 "
              f"'기타(인테리어·설비)' 분포")
        buckets = [(0, 0, "0원 — 인테리어 미공시"), (1, 999, "1~999만원 — 사실상 미공시"),
                   (1000, 1999, "1,000~1,999만원"), (2000, 2999, "2,000~2,999만원"),
                   (3000, 10**9, "3,000만원 이상 — 정상 공시")]
        for lo, hi, name in buckets:
            grp = [r for r in base if lo <= r["  기타_만원"] <= hi]
            pct = len(grp) / len(base) * 100 if base else 0
            bar = "#" * int(pct / 2)
            print(f"  {name:<26} {len(grp):>4}건 ({pct:>5.1f}%) {bar}")
        share = [r["  기타_만원"] / r["창업비용_만원"] for r in base if r["창업비용_만원"]]
        if share:
            share.sort()
            mid = share[len(share) // 2]
            print(f"\n  창업비 중 기타 비중 중앙값: {mid:.0%}")
            print("  정상 공시 브랜드는 보통 50~75%가 인테리어·설비입니다.")
        return

    picks = [
        r for r in rows
        if 0 < r["창업비용_만원"] <= a.max_cost
        and r["  기타_만원"] >= a.min_etc
        and r["추정월영업이익_만원"] >= a.min_profit
        and r["가맹점수"] >= a.min_stores
        and r["폐점률"] <= a.max_close
        and r["연매출_만원"] > 0
        and (r["업종대"] == a.lclas if a.lclas else True)
        and (r["업종중"] == a.mlsfc if a.mlsfc else True)
    ]
    picks.sort(key=lambda x: x[a.sort], reverse=(a.sort != "회수개월_추정"))
    total = len(picks)
    picks = picks[:a.top]

    scope = " ".join(x for x in [a.lclas, a.mlsfc] if x) or "전체 업종"
    print("=" * 62)
    print(f"{scope} · 창업비 {a.max_cost:,}만원 이하 · 추정 월순익 {a.min_profit:,}만원 이상")
    print(f"가맹점 {a.min_stores}개 이상 · 폐점률 {a.max_close:g}% 이하 · 정렬 {a.sort}")
    print(f"조건 통과 {total:,}건 중 상위 {len(picks)}건")
    if dropped:
        print(f"※ 창업비 공시 불완전(기타 {a.min_etc:,}만원 미만) {len(dropped)}건 제외: "
              + ", ".join(d["브랜드"] for d in dropped[:5])
              + (" 외" if len(dropped) > 5 else ""))
    print("=" * 62)

    if not total:
        print("조건을 만족하는 브랜드가 없습니다. --min-profit 이나 --min-stores 를 낮춰보세요.")
        return

    for i, m in enumerate(picks, 1):
        print(f"\n[{i}] {m['브랜드']}")
        for k, v in m.items():
            if k == "브랜드":
                continue
            mark = "   └ " if k.startswith("  ") else " "
            val = f"{v:,}" if isinstance(v, (int, float)) else v
            print(f"{mark}{k.strip():<14}: {val}")

    write_csv(picks, os.path.join(HERE, f"ftc_추천_{a.mlsfc or a.lclas or '전체'}_{year}.csv"))

    print("\n" + "-" * 62)
    print("추정월영업이익 = 월매출 x (1 - 업종별 비용률). 공정위 데이터에 영업이익은 없습니다.")
    print(f"적용 비용률: 외식 {COST_RATIO['외식']:.0%} / 도소매 {COST_RATIO['도소매']:.0%} "
          f"/ 서비스 {COST_RATIO['서비스']:.0%} (그 외 {DEFAULT_COST_RATIO:.0%})")
    print("창업비용에 점포 임차보증금·권리금은 포함되지 않습니다.")


if __name__ == "__main__":
    # head 등으로 파이프할 때 역추적 대신 조용히 종료
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    main()
