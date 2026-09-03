#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공정거래위원회(기관코드 1130000) 오픈API 엔드포인트 탐색기.

이미 발급받은 인증키로 후보 엔드포인트를 하나씩 찔러보고,
살아있는 것과 없는 것을 구분해 출력한다. 로열티·광고판촉비 같은
추가 항목을 주는 서비스가 있는지 찾는 용도.

  export FTC_SERVICE_KEY='발급키'
  python3 ftc_probe.py

주의: 활용신청을 하지 않은 서비스는 키가 있어도 거부된다(SERVICE_ACCESS_DENIED).
      그 경우 data.go.kr에서 해당 서비스에 활용신청을 먼저 해야 한다.
"""

import os
import sys
import xml.etree.ElementTree as ET

import requests

BASE = "https://apis.data.go.kr/1130000"

# (서비스명, 오퍼레이션명) — 앞 3개는 이미 확인된 것, 나머지는 후보
CANDIDATES = [
    # --- 확인된 것 (대조군) ---
    ("FftcBrandFntnStatsService",          "getBrandFntnStats"),
    ("FftcBrandFrcsStatsService",          "getBrandFrcsStats"),
    ("FftcBrandIndutyDropFrcsStatsService", "getBrandIndutyFrcsStats"),
    ("FftcBrandIndutyDropFrcsStatsService", "getBrandIndutyDropStats"),
    # --- 후보: 같은 서비스의 다른 오퍼레이션 ---
    ("FftcBrandFntnStatsService",          "getBrandFntnDetailStats"),
    ("FftcBrandFrcsStatsService",          "getBrandFrcsDetailStats"),
    # --- 후보: 형제 서비스 ---
    ("FftcBrandRoyltStatsService",         "getBrandRoyltStats"),
    ("FftcBrandAdvrtStatsService",         "getBrandAdvrtStats"),
    ("FftcBrandCntrctStatsService",        "getBrandCntrctStats"),
    ("FftcJnghdqrtrsStatsService",         "getJnghdqrtrsStats"),
    ("FftcBrandInfoService",               "getBrandInfo"),
    ("FftcFranchiseInfoService",           "getFranchiseInfo"),
]


def load_key() -> str:
    key = os.environ.get("FTC_SERVICE_KEY", "").strip()
    if not key:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ftc_key")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                key = f.read().strip()
    if not key:
        sys.exit("[중단] export FTC_SERVICE_KEY='발급키' 를 먼저 하세요.")
    from urllib.parse import quote
    return key if "%" in key else quote(key, safe="")


def probe(key, svc, op):
    url = f"{BASE}/{svc}/{op}?serviceKey={key}&pageNo=1&numOfRows=1&yr=2025"
    try:
        r = requests.get(url, timeout=30)
    except requests.RequestException as e:
        return "네트워크실패", type(e).__name__
    if r.status_code != 200:
        return "HTTP오류", f"status {r.status_code}"
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        return "비XML응답", r.text[:80].replace("\n", " ")
    code = root.findtext(".//resultCode") or root.findtext(".//returnReasonCode") or "?"
    msg = (root.findtext(".//resultMsg") or root.findtext(".//returnAuthMsg") or "").strip()
    total = root.findtext(".//totalCount")
    if code in ("00", "0"):
        fields = sorted({ch.tag for it in root.findall(".//items/item") for ch in it})
        return "사용가능", f"{total or 0}건 · 필드: {', '.join(fields) if fields else '없음'}"
    return "거부/없음", f"code={code} {msg}"


def main():
    key = load_key()
    print(f"공정거래위원회(1130000) 엔드포인트 {len(CANDIDATES)}개 탐색\n")
    ok = []
    for svc, op in CANDIDATES:
        status, detail = probe(key, svc, op)
        mark = "O" if status == "사용가능" else "X"
        print(f"[{mark}] {svc}/{op}")
        print(f"     {status} — {detail}\n")
        if status == "사용가능":
            ok.append((svc, op, detail))
    print("=" * 60)
    print(f"사용 가능: {len(ok)}개")
    for svc, op, d in ok:
        print(f"   {svc}/{op}")
    print("""
[해석]
  '사용가능' = 이 엔드포인트가 실제로 존재하고 키로 접근된다.
  '거부/없음' = 엔드포인트가 없거나, 있어도 활용신청을 안 한 상태다.
                code=30 계열이면 키/신청 문제, 그 외는 대체로 미존재.

  이 결과를 그대로 복사해서 알려주면, 새 필드가 있는지 판단해 붙이겠습니다.""")


if __name__ == "__main__":
    main()
