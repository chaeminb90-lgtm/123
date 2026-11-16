"""하복당 카페 업종변경 전단 2장 (A4 세로). 앞면: 업종변경·숍인숍 가맹점 모집 / 뒷면: 카페 사장님께 드리는 편지.
문구와 숫자는 하복당 사이트(site/src/sections)에 공개된 사실만 사용합니다.
usage: python3 ops/flyer/make_flyer.py && node ops/flyer/render.js
"""
import os
H = os.path.dirname(os.path.abspath(__file__))
F = 'file:///home/user/123/ads_meta/fonts'
u = lambda p: 'file://' + os.path.join(H, p)
PHONE = '010.7683.1577'

HEAD = f'''<!doctype html><meta charset=utf-8><link rel=stylesheet href="{F}/pen/400.css"><link rel=stylesheet href="{F}/bhs/400.css"><style>
@font-face{{font-family:PT;src:url('{F}/PretendardVariable.ttf');font-weight:100 950}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1240px;height:1754px;overflow:hidden}}
body{{position:relative;font-family:PT,sans-serif;word-break:keep-all;color:#FFF4E6;
  background:radial-gradient(ellipse 90% 60% at 70% 20%,#F47A22 0%,#EE6A16 55%,#E05A0C 100%)}}
.a{{position:absolute}}
.bh{{font-family:'Black Han Sans';letter-spacing:-.01em;line-height:1.05}}
.sh{{text-shadow:0 6px 0 #8A2F04}}
.check{{left:0;right:0;bottom:0;height:56px;background:
  repeating-conic-gradient(#FFF4E6 0 25%,transparent 0 50%) 0 0/56px 56px}}
:root{{--ink:#3A1705;--deep:#B8430A;--yel:#FFD24A;--cream:#FFF4E6}}
</style>'''

FRONT = HEAD + f'''<style>
.photo{{left:690px;top:50px;width:500px;height:500px;border-radius:50%;border:14px solid var(--cream);
  background:url('{u("hero_lineup.jpg")}') 34% 60%/auto 760px no-repeat;box-shadow:0 18px 40px rgba(90,30,0,.35)}}
.star{{left:930px;top:400px;width:250px;height:250px;background:var(--yel);transform:rotate(-12deg);
  clip-path:polygon(50% 0,61% 18%,79% 7%,80% 28%,100% 30%,88% 47%,100% 64%,80% 68%,82% 90%,62% 81%,50% 100%,38% 81%,18% 90%,20% 68%,0 64%,12% 47%,0 30%,20% 28%,21% 7%,39% 18%);
  display:flex;align-items:center;justify-content:center;text-align:center;color:var(--ink);font-family:'Black Han Sans';font-size:42px;line-height:1.12}}
.pill{{left:80px;top:330px;padding:16px 40px;border-radius:60px;background:var(--cream);color:var(--ink);font-size:40px;font-weight:800;letter-spacing:-.04em}}
.l1{{left:78px;top:590px;font-size:96px}}
.box{{left:70px;top:715px;padding:18px 40px 26px;background:var(--yel);color:var(--ink);font-size:112px;transform:rotate(-1.6deg);
  box-shadow:10px 12px 0 #8A2F04}}
.sub{{left:80px;top:920px;font-size:52px;display:flex;align-items:center;gap:22px}}
.sub i{{display:inline-block;width:0;height:0;border-top:24px solid transparent;border-bottom:24px solid transparent;border-left:34px solid var(--yel)}}
.card{{left:70px;top:1010px;width:1100px;height:530px;border-radius:40px;background:var(--cream);color:var(--ink);padding:26px 40px}}
.row{{display:flex;align-items:center;gap:34px;height:119px;border-bottom:3px dashed #E8C9AC}}
.row:last-child{{border-bottom:none}}
.badge{{flex:none;width:200px;height:96px;border-radius:20px;background:var(--deep);color:var(--cream);font-family:'Black Han Sans';font-size:32px;line-height:1.12;
  display:flex;align-items:center;justify-content:center;text-align:center}}
.rt{{font-family:'Black Han Sans';font-size:46px;line-height:1.1;letter-spacing:-.01em}}
.rt b{{font-weight:400;color:#E0490A}}
.rs{{margin-top:8px;font-size:26px;font-weight:600;letter-spacing:-.03em;color:#5A3A26}}
.cta{{left:70px;top:1566px;right:70px;display:flex;align-items:center;justify-content:space-between;gap:24px}}
.cta .p{{flex:none;white-space:nowrap;padding:16px 26px;border-radius:18px;background:var(--yel);color:var(--ink);font-family:'Black Han Sans';font-size:40px}}
.cta .n{{white-space:nowrap;font-family:'Black Han Sans';font-size:104px;line-height:1;text-shadow:0 7px 0 #8A2F04}}
.note{{left:80px;top:1688px;font-size:17px;line-height:1.45;font-weight:600;color:rgba(255,244,230,.92);letter-spacing:-.02em}}
.check{{height:0}}
</style>
<img class="a" src="{u('logo_w_4x.png')}" style="left:84px;top:64px;width:300px">
<div class="a photo"></div>
<div class="a star">교육 이틀,<br>바로 오픈!</div>
<div class="a pill">카페 운영 중인 사장님!</div>
<div class="a l1 bh sh">지금 그 카페 자리에서,</div>
<div class="a box bh">하복당으로 다시 시작!</div>
<div class="a sub bh"><span><i></i><i></i></span>카페 업종변경 · 숍인숍 가맹점 모집</div>
<div class="a card">
 <div class="row"><div class="badge">불·기름<br>없는 주방</div><div><div class="rt">조리가 아니라 <b>조합</b></div>
   <div class="rs">정해진 레시피대로 과일·시럽·토핑을 담아요 · 기본 교육 이틀</div></div></div>
 <div class="row"><div class="badge">검증된<br>배달 매출</div><div><div class="rt">안양점 6월 배달 매출 <b>5,073만원</b></div>
   <div class="rs">배민 약 2,577만원 + 쿠팡이츠 약 2,497만원 · 영업잔여금 21.3%</div></div></div>
 <div class="row"><div class="badge">투명한<br>과일 공급</div><div><div class="rt">가락시장 경매가 + <b>원가 전표</b></div>
   <div class="rs">박스당 1,000원만 붙여 본점과 같은 단가로 공급</div></div></div>
 <div class="row"><div class="badge">카페 그대로<br>숍인숍</div><div><div class="rt">운영 중인 카페에 <b>하복당 더하기</b></div>
   <div class="rs">간판·내부 주황색 페인트는 필수 · 10평 내외, 배달·포장 중심</div></div></div>
</div>
<div class="a cta"><span class="p">1:1 미팅 예약</span><span class="n">{PHONE}</span></div>
<div class="a note">서울·경기·인천 50호점까지만 모집 · 가맹 상담은 본사 1:1 미팅으로 진행합니다<br>
※ 안양점 수치: 하복당 공식 블로그 ‘안양점 6월 손익계산서’(2026.7.13)의 배달앱 매출 기준. 특정 매장의 과거 실적이며 다른 매장의 수익을 보장하지 않습니다.</div>'''

BACK = HEAD + f'''<style>
.t{{left:0;right:0;top:250px;text-align:center;font-size:104px}}
.t .y{{color:var(--yel)}}
.card{{left:60px;top:400px;width:1120px;height:1060px;border-radius:44px;background:var(--cream);color:var(--ink)}}
.ph{{left:70px;top:56px;width:300px;height:300px;border-radius:50%;border:12px solid var(--deep);box-shadow:0 0 0 10px var(--yel);
  background:url('{u("storefront.jpg")}') 22% 50%/auto 300px no-repeat}}
.hl{{left:420px;top:92px;font-size:66px;color:var(--deep);line-height:1.18}}
.by{{left:424px;top:268px;font-size:28px;font-weight:700;color:#7A5A44}}
.body{{left:70px;right:70px;top:392px;font-size:27px;line-height:1.7;letter-spacing:-.03em;font-weight:500;color:#2B140A}}
.body p{{margin-bottom:20px}}
.body b{{font-weight:800}}
.body m{{font-weight:800;color:#C2410A;background:linear-gradient(transparent 58%,#FFE08A 58%)}}
.sign{{right:76px;bottom:22px;font-family:'Nanum Pen Script';font-size:60px;color:#C2410A}}
.qrbox{{left:60px;top:1488px;width:210px;height:210px;border-radius:28px;background:var(--cream);display:flex;align-items:center;justify-content:center}}
.ask{{left:310px;top:1494px;font-size:42px}}
.tel{{left:306px;top:1562px;font-size:96px;white-space:nowrap;color:var(--yel);text-shadow:0 7px 0 #8A2F04;display:flex;align-items:center;gap:22px}}
.small{{left:312px;top:1692px;font-size:20px;font-weight:600;color:rgba(255,244,230,.92)}}
</style>
<img class="a" src="{u('logo_w_4x.png')}" style="left:510px;top:50px;width:220px">
<div class="a t bh sh"><span class="y">카페 사장님께</span> 드리는 편지</div>
<div class="a card">
 <div class="a ph"></div>
 <div class="a hl bh">카페 자리에서<br>다시 시작하는 방법</div>
 <div class="a by">하복당 가맹본부</div>
 <div class="a body">
  <p>하복당은 생과일을 손질해 컵과 그릇에 담아 파는 과일디저트 브랜드입니다. <b>10평 내외 매장에서 배달과 포장 중심</b>으로 운영합니다.</p>
  <p>메뉴는 조리가 아니라 조합입니다. <m>불도 기름도 쓰지 않고</m> 정해진 레시피대로 만들어 <m>기본 교육은 이틀</m>이면 됩니다. 오픈 전 상권 분석과 배달앱 세팅, 초기 바이럴은 본사가 함께 준비합니다.</p>
  <p>과일은 ‘명가’가 가락시장 중앙청과 경매에서 매입해 보내 드립니다. <m>원가 전표</m>를 함께 드리고, <m>박스당 1,000원</m>만 붙여 본점과 같은 단가로 공급합니다.</p>
  <p>운영 중인 카페에 하복당을 더하는 <m>숍인숍</m>도 가능합니다. 간판과 내부 주황색 페인트는 꼭 갖추셔야 합니다.</p>
  <p>매출과 비용은 1:1 미팅에서 손익계산서와 원가 전표로 보여 드리고, 수익 자료는 서면으로 드립니다. 정보공개서와 계약서(안)를 받으신 뒤 <b>14일이 지나야 계약</b>합니다. <b>충분히 따져 보고 결정하세요.</b></p>
 </div>
 <div class="a sign">하복당 가맹본부 드림</div>
</div>
<div class="a qrbox"><img src="{u('logo_o_4x.png')}" style="width:170px"></div>
<div class="a ask bh">궁금하신 점은 1:1 미팅에서 숫자로 보여드립니다.</div>
<div class="a tel bh"><span style="font-size:84px">☎</span>{PHONE}</div>
<div class="a small">서울·경기·인천 50호점까지만 모집 · 2026년 10월 기준 32팀 미팅 대기</div>'''

for name, html in (('front', FRONT), ('back', BACK)):
    open(os.path.join(H, f'{name}.html'), 'w').write(html)
print('ok')
