#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정보공개서 '본문'에서 로열티(계속가맹금)를 뽑는다.

apis.data.go.kr(집계 통계)이 아니라 franchise.ftc.go.kr 자체 API를 쓴다.
3단계로 동작한다.

  1) type=list      연도별 정보공개서 목록 -> 문서 일련번호(jngIfrmpSn)
  2) type=title     그 문서의 목차
  3) type=content   그 문서의 본문  <- 로열티는 여기

주의: 파라미터 이름이 servicekey (소문자 k)다. apis.data.go.kr의 serviceKey와 다르다.

  export FTC_SERVICE_KEY='발급키'
  python3 ftc_royalty.py --probe               # 접속·키 확인만
  python3 ftc_royalty.py --brand 달떡볶이       # 특정 브랜드 본문에서 로열티 검색
"""

import argparse
import json
import os
import re
import sys

import requests

BASE = "https://franchise.ftc.go.kr/api/search.do"
VIEWER = "https://franchise.ftc.go.kr/api/viewer.do"

# 본문에서 이 단어들 주변을 로열티 후보로 본다
ROYALTY_WORDS = ["계속가맹금", "로열티", "로얄티", "royalty", "정기납입",
                 "가맹금(계속", "월회비", "광고비", "판촉비", "물품대금"]


def load_key() -> str:
    key = os.environ.get("FTC_SERVICE_KEY", "").strip()
    if not key:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ftc_key")
        if os.path.exists(p):
            key = open(p, encoding="utf-8").read().strip()
    if not key:
        sys.exit("[중단] FTC_SERVICE_KEY를 설정하세요.")
    from urllib.parse import unquote
    # 이 API는 인코딩되지 않은 원본 키를 쓰는 것으로 보인다. %가 있으면 되돌린다.
    return unquote(key) if "%" in key else key


def call(key, **params):
    params["servicekey"] = key          # 소문자 k — 명세서 기준
    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    return r


def show_raw(r, limit=1200):
    t = r.text.strip()
    print(f"  HTTP {r.status_code} · {r.headers.get('Content-Type','?')} · {len(t):,}자")
    print("  --- 응답 앞부분 ---")
    print("  " + t[:limit].replace("\n", "\n  "))
    if len(t) > limit:
        print(f"  ... (이하 {len(t)-limit:,}자 생략)")


def cmd_probe(key, year):
    print(f"[1] 목록 조회 — type=list&yr={year}\n")
    try:
        r = call(key, type="list", yr=year, pageNo="1", numOfRows="5", viewType="xml")
    except requests.RequestException as e:
        sys.exit(f"[중단] 호출 실패: {type(e).__name__}\n  {str(e)[:200]}")
    show_raw(r)
    sns = re.findall(r"<jngIfrmpSn>(\d+)</jngIfrmpSn>", r.text) or re.findall(r'"jngIfrmpSn"\s*:\s*"?(\d+)', r.text)
    print(f"\n  찾은 문서 일련번호: {sns[:5] if sns else '없음'}")
    if not sns:
        print("  ※ 일련번호 태그명이 다를 수 있습니다. 위 응답을 그대로 붙여주세요.")
        return
    sn = sns[0]
    print(f"\n[2] 본문 조회 — type=content&jngIfrmpSn={sn}\n")
    r2 = call(key, type="content", jngIfrmpSn=sn)
    show_raw(r2, 1500)
    hits = [w for w in ROYALTY_WORDS if w in r2.text]
    print(f"\n  로열티 관련 단어 발견: {hits if hits else '없음'}")


def cmd_brand(key, year, brand):
    print(f"'{brand}' 문서 찾는 중 (yr={year}) ...")
    page, found = 1, None
    while page <= 40 and not found:
        r = call(key, type="list", yr=year, pageNo=str(page), numOfRows="500", viewType="xml")
        if brand in r.text:
            # 브랜드명이 든 항목 블록에서 일련번호를 뽑는다
            for blk in re.findall(r"<item>.*?</item>", r.text, re.S):
                if brand in blk:
                    m = re.search(r"<jngIfrmpSn>(\d+)</jngIfrmpSn>", blk)
                    if m:
                        found = m.group(1)
                        print("  매칭 블록:", re.sub(r"\s+", " ", blk)[:300])
                        break
        if not re.search(r"<item>", r.text):
            break
        page += 1
    if not found:
        sys.exit(f"[중단] '{brand}'를 목록에서 못 찾았습니다. 상호명으로도 시도해 보세요.")

    print(f"\n일련번호 {found} · 본문 조회\n")
    r = call(key, type="content", jngIfrmpSn=found)
    text = re.sub(r"<[^>]+>", " ", r.text)
    text = re.sub(r"\s+", " ", text)
    print(f"본문 길이 {len(text):,}자\n")
    for w in ROYALTY_WORDS:
        for m in re.finditer(re.escape(w), text):
            s, e = max(0, m.start()-120), min(len(text), m.end()+220)
            print(f"[{w}] ...{text[s:e]}...\n")
    print(f"뷰어로 직접 보기: {VIEWER}?jngIfrmpSn={found}&servicekey=<키>")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--probe", action="store_true", help="접속·키·응답형식 확인")
    p.add_argument("--brand", help="이 브랜드의 본문에서 로열티 검색")
    p.add_argument("--year", default="2025")
    a = p.parse_args()
    key = load_key()
    if a.brand:
        cmd_brand(key, a.year, a.brand)
    else:
        cmd_probe(key, a.year)


if __name__ == "__main__":
    main()
