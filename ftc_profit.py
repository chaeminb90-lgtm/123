#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브랜드별 월 손익을 항목별로 쪼개서 보여준다.

공정위 정보공개서에는 비용 항목이 없다. 있는 것은 매출과 창업비뿐이라
비용은 가정할 수밖에 없다. 다만 뭉뚱그린 '비용률 75%' 대신 항목을 나눠
어디서 얼마가 빠지는지 드러내고, 각 항목을 옵션으로 조정할 수 있게 한다.

감가상각만은 가정이 아니다. 공시된 인테리어(기타) 금액을 상각월수로 나눈다.
임차료도 매출 대비 %가 아니라 공시 매출에서 역산한 평수 x 평당임차료로 잡는다.
임차료는 매출이 아니라 면적에 비례하기 때문이다.

  python3 ftc_profit.py --brand 두찜
  python3 ftc_profit.py --mlsfc 한식 --top 5
  python3 ftc_profit.py --top 5 --delivery-share 60 --rent-per-pyeong 30
"""

import argparse
import csv
import os
import signal
import sys

from ftc_5000 import merge

HERE = os.path.dirname(os.path.abspath(__file__))

# 업종중분류별 평당 월매출 중앙값. 같은 업종 안에서의 상대 위치를 보기 위한 기준값.
_MEDIAN_CACHE = {}


def category_medians(rows):
    """업종중분류별 평당 월매출 중앙값을 계산해 캐시."""
    if _MEDIAN_CACHE:
        return _MEDIAN_CACHE
    buckets = {}
    for r in rows:
        if r["추정평수"] > 0 and r["월매출_만원"] > 0:
            buckets.setdefault(r["업종중"], []).append(r["월매출_만원"] / r["추정평수"])
    for k, v in buckets.items():
        v.sort()
        _MEDIAN_CACHE[k] = v[len(v) // 2]
    return _MEDIAN_CACHE


def estimate_delivery_share(r, medians):
    """배달 매출 비중을 추정해 (비중%, 근거) 반환.

    공정위 공시에 배달/홀 구분 필드는 없다. 두 가지 간접 신호만 쓴다.
      - 10평 미만: 홀 영업이 물리적으로 불가능하므로 배달·포장 전문
      - 같은 업종 중앙값 대비 평당매출 배수: 홀 좌석만으로 설명되지 않는 초과분

    업종 '간' 비교로는 쓸 수 없다. 치킨(89만/평)이 일식(131만/평)보다 낮게 나오므로
    평당매출의 절대 수준은 배달 비중을 뜻하지 않는다. 어디까지나 추정이다.
    """
    if r["추정평수"] <= 0 or r["월매출_만원"] <= 0:
        return 30.0, "평수 미상 — 기본값"
    if r["추정평수"] < 10:
        return 90.0, f"{r['추정평수']:g}평 — 홀 영업 불가"
    med = medians.get(r["업종중"], 0)
    if not med:
        return 30.0, "업종 기준값 없음 — 기본값"
    x = (r["월매출_만원"] / r["추정평수"]) / med
    if x >= 3:
        return 70.0, f"{r['업종중']} 중앙값의 {x:.1f}배 — 홀만으로 설명 안 됨"
    if x >= 2:
        return 50.0, f"{r['업종중']} 중앙값의 {x:.1f}배 — 다소 높음"
    return 30.0, f"{r['업종중']} 중앙값의 {x:.1f}배 — 평범"


def load(year):
    def read(name):
        path = os.path.join(HERE, f"{name}_{year}.csv")
        if not os.path.exists(path):
            sys.exit(f"[중단] {os.path.basename(path)} 가 없습니다. 먼저 ftc_5000.py를 실행하세요.")
        with open(path, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    return merge(read("ftc_창업금액_원본"), read("ftc_가맹점현황_원본"))


def pnl(r, a):
    """월 손익을 항목별로 계산해 (항목리스트, 순이익) 반환. 단위 만원.

    평당매출 미공시로 평수를 못 구하면 임차료가 0이 되어 순이익이 부풀려진다.
    그런 브랜드는 임차료를 매출 대비 비율로 대체한다.
    """
    sales = r["월매출_만원"]
    if r["추정평수"] > 0:
        rent = r["추정평수"] * a.rent_per_pyeong
        rent_note = f"{r['추정평수']:g}평 x {a.rent_per_pyeong:g}만원"
    else:
        rent = sales * a.rent_fallback / 100
        rent_note = f"평수 미상 -> 매출 {a.rent_fallback:g}% 대체"
    depr = r["  기타_만원"] / a.depreciation_months
    if a.delivery_share == "auto":
        dshare, dnote = estimate_delivery_share(r, a._medians)
    else:
        dshare, dnote = float(a.delivery_share), "직접 지정"

    items = [
        ("월매출 (공시)",        sales,                                        "공정위 공시"),
        ("식자재비",             -sales * a.food_cost / 100,                   f"매출 {a.food_cost:g}%"),
        ("인건비",               -sales * a.labor / 100,                       f"매출 {a.labor:g}%"),
        ("임차료",               -rent,                                        rent_note),
        ("배달 수수료",          -sales * dshare / 100 * a.delivery_fee / 100,
                                 f"배달비중 {dshare:g}% ({dnote}) x 수수료 {a.delivery_fee:g}%"),
        ("카드 수수료",          -sales * a.card_fee / 100,                    f"매출 {a.card_fee:g}%"),
        ("로열티·광고분담금",    -sales * a.royalty / 100,                     f"매출 {a.royalty:g}%"),
        ("공과금·소모품",        -sales * a.utility / 100,                     f"매출 {a.utility:g}%"),
        ("인테리어 감가상각",    -depr,                                        f"공시 {r['  기타_만원']:,}만원 ÷ {a.depreciation_months}개월"),
    ]
    return items, sum(v for _, v, _ in items)


def show(r, a):
    items, profit = pnl(r, a)
    sales = r["월매출_만원"]
    print(f"\n{'='*64}")
    print(f"{r['브랜드']}  ({r['본사']} · {r['업종중']})")
    print(f"창업비 {r['창업비용_만원']:,}만원 (인테리어 {r['  기타_만원']:,}만원) · "
          f"가맹점 {r['가맹점수']:,}개 · 폐점률 {r['폐점률']}% · 추정 {r['추정평수']:g}평")
    print(f"{'='*64}")
    for name, val, note in items:
        pct = f"{abs(val)/sales*100:>5.1f}%" if sales else "    -"
        print(f"  {name:<18}{val:>12,.0f}만  {pct}   {note}")
    print(f"  {'-'*60}")
    margin = profit / sales * 100 if sales else 0
    print(f"  {'월 순이익':<18}{profit:>12,.0f}만  {margin:>5.1f}%")
    if profit > 0:
        print(f"  {'투자 회수':<18}{r['창업비용_만원']/profit:>12,.1f}개월"
              f"   (점포 임차보증금·권리금 제외)")
    else:
        print(f"  {'투자 회수':<18}{'회수 불가':>12}")


def main():
    p = argparse.ArgumentParser(description="브랜드별 월 손익 항목별 분해")
    p.add_argument("--year", default="2025")
    p.add_argument("--brand", help="특정 브랜드 하나만")
    p.add_argument("--mlsfc", default="", help="업종중분류 필터")
    p.add_argument("--max-cost", type=int, default=5000)
    p.add_argument("--min-stores", type=int, default=30)
    p.add_argument("--min-etc", type=int, default=2000)
    p.add_argument("--max-new-ratio", type=float, default=80.0)
    p.add_argument("--top", type=int, default=5)
    # ---- 비용 가정 (전부 조정 가능) ----
    p.add_argument("--food-cost", type=float, default=38, help="식자재비 %% (기본 38)")
    p.add_argument("--labor", type=float, default=20, help="인건비 %% (기본 20)")
    p.add_argument("--rent-per-pyeong", type=float, default=20, help="평당 월임차료 만원 (기본 20)")
    p.add_argument("--rent-fallback", type=float, default=10,
                   help="평수를 못 구할 때 임차료를 매출의 몇 %%로 볼지 (기본 10)")
    p.add_argument("--delivery-share", default="auto",
                   help="배달 매출 비중 %%. 기본 auto = 평수와 업종 내 평당매출로 추정. "
                        "숫자를 주면 전 브랜드에 그 값을 적용")
    p.add_argument("--delivery-fee", type=float, default=13, help="배달 수수료율 %% (기본 13)")
    p.add_argument("--card-fee", type=float, default=2, help="카드 수수료 %% (기본 2)")
    p.add_argument("--royalty", type=float, default=3, help="로열티·광고 %% (기본 3)")
    p.add_argument("--utility", type=float, default=4, help="공과금·소모품 %% (기본 4)")
    p.add_argument("--depreciation-months", type=int, default=60, help="인테리어 상각월수 (기본 60)")
    a = p.parse_args()

    rows = load(a.year)
    a._medians = category_medians(rows)
    if a.brand:
        hit = [r for r in rows if a.brand in r["브랜드"]]
        if not hit:
            sys.exit(f"[중단] '{a.brand}' 브랜드를 찾지 못했습니다.")
        for r in hit[:5]:
            show(r, a)
    else:
        cand = [r for r in rows
                if 0 < r["창업비용_만원"] <= a.max_cost
                and r["가맹점수"] >= a.min_stores
                and r["  기타_만원"] >= a.min_etc
                and r["신규비율"] <= a.max_new_ratio
                and r["연매출_만원"] > 0
                and (r["업종중"] == a.mlsfc if a.mlsfc else True)]
        cand.sort(key=lambda r: -pnl(r, a)[1])
        for r in cand[:a.top]:
            show(r, a)
        print(f"\n(조건 통과 {len(cand)}건 중 순이익 상위 {min(a.top, len(cand))}건)")

    print("\n" + "-" * 64)
    print("매출과 인테리어 금액만 공정위 공시값입니다.")
    print("나머지 비용 항목은 모두 가정치이며, 옵션으로 조정할 수 있습니다 (--help).")
    print("점주 본인 인건비, 점포 임차보증금·권리금, 세금은 포함돼 있지 않습니다.")


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    main()
