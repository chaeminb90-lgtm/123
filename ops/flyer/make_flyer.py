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
  background:url('{u("fruit_boxes.jpg")}') 50% 50%/auto 520px no-repeat;box-shadow:0 18px 40px rgba(90,30,0,.35)}}
.star{{left:930px;top:400px;width:250px;height:250px;background:var(--yel);transform:rotate(-12deg);
  clip-path:polygon(50% 0,61% 18%,79% 7%,80% 28%,100% 30%,88% 47%,100% 64%,80% 68%,82% 90%,62% 81%,50% 100%,38% 81%,18% 90%,20% 68%,0 64%,12% 47%,0 30%,20% 28%,21% 7%,39% 18%);
  display:flex;align-items:center;justify-content:center;text-align:center;color:var(--ink);font-family:'Black Han Sans';font-size:42px;line-height:1.12}}
.pill{{left:80px;top:330px;padding:16px 40px;border-radius:60px;background:var(--cream);color:var(--ink);font-size:40px;font-weight:800;letter-spacing:-.04em}}
.l1{{left:78px;top:590px;font-size:96px}}
.box{{left:70px;top:715px;padding:18px 40px 26px;background:var(--yel);color:var(--ink);font-size:112px;transform:rotate(-1.6deg);
  box-shadow:10px 12px 0 #8A2F04}}
.sub{{left:80px;top:920px;font-size:52px;display:flex;align-items:center;gap:22px}}
.sub i{{display:inline-block;width:0;height:0;border-top:24px solid transparent;border-bottom:24px solid transparent;border-left:34px solid var(--yel)}}
.card{{left:70px;top:996px;width:1100px;height:600px;border-radius:40px;background:var(--cream);color:var(--ink);padding:20px 40px}}
.row{{display:flex;align-items:center;gap:34px;height:112px;border-bottom:3px dashed #E8C9AC}}
.row:last-child{{border-bottom:none}}
.badge{{flex:none;width:200px;height:90px;border-radius:20px;background:var(--deep);color:var(--cream);font-family:'Black Han Sans';font-size:29px;line-height:1.12;
  display:flex;align-items:center;justify-content:center;text-align:center}}
.rt{{font-family:'Black Han Sans';font-size:44px;line-height:1.1;letter-spacing:-.01em}}
.rt b{{font-weight:400;color:#E0490A}}
.rs{{margin-top:6px;font-size:25px;font-weight:600;letter-spacing:-.03em;color:#5A3A26}}
.cta{{left:70px;top:1622px;right:70px;display:flex;align-items:center;justify-content:space-between;gap:24px}}
.cta .p{{flex:none;white-space:nowrap;padding:16px 26px;border-radius:18px;background:var(--yel);color:var(--ink);font-family:'Black Han Sans';font-size:40px}}
.cta .n{{white-space:nowrap;font-family:'Black Han Sans';font-size:104px;line-height:1;text-shadow:0 7px 0 #8A2F04}}
.note{{left:80px;top:1688px;font-size:17px;line-height:1.45;font-weight:600;color:rgba(255,244,230,.92);letter-spacing:-.02em}}
.check{{height:0}}
</style>
<img class="a" src="{u('logo_w_4x.png')}" style="left:84px;top:64px;width:300px">
<div class="a photo"></div>
<div class="a star">교육 3일,<br>바로 오픈!</div>
<div class="a pill">카페 운영 중인 사장님!</div>
<div class="a l1 bh sh">지금 그 카페 자리에서,</div>
<div class="a box bh">하복당으로 다시 시작!</div>
<div class="a sub bh"><span><i></i><i></i></span>카페 업종변경 · 숍인숍 가맹점 모집</div>
<div class="a card">
 <div class="row"><div class="badge">불·기름<br>없는 주방</div><div><div class="rt">과일을 <b>담기만 하면 끝!</b></div>
   <div class="rs">교육 3일이면 나도 과일 마스터!</div></div></div>
 <div class="row"><div class="badge">검증된<br>배달 매출</div><div><div class="rt">구월점 배달 매출 <b>8,200만원</b></div>
   <div class="rs">인계점 6월 7,200만원 · 7월 전 지점 평균 5,000만원 달성</div></div></div>
 <div class="row"><div class="badge">투명한<br>과일 공급</div><div><div class="rt">가락시장 경매가로 <b>매장 앞까지</b></div>
   <div class="rs">저녁에 발주하면 가락시장 과일 도매회사가 매장 앞까지 바로 배달</div></div></div>
 <div class="row"><div class="badge">로스율<br>0%</div><div><div class="rt">썩은 과일은 <b>100% 환불</b></div>
   <div class="rs">과일 단 하나라도 상한 채 배송되면 전액 환불해 드립니다</div></div></div>
 <div class="row"><div class="badge">간판만 바꾸면<br>바로 시작</div><div><div class="rt"><b>도마와 칼</b>만 있으면 OK</div>
   <div class="rs">인테리어 공사 없이 간판만 달면 바로 시작</div></div></div>
</div>
<div class="a cta"><span class="p">1:1 미팅 예약</span><span class="n">{PHONE}</span></div>
'''

BACK = HEAD + f'''<style>
.t{{left:0;right:0;top:186px;text-align:center;font-size:94px}}
.t .y{{color:var(--yel)}}
.store{{left:60px;top:306px;width:1120px;height:196px;border-radius:36px;border:10px solid var(--yel);
  background:#fff url('{u("storefront.jpg")}') 50% 20%/1100px auto no-repeat;box-shadow:0 14px 30px rgba(90,30,0,.3)}}
.card{{left:60px;top:520px;width:1120px;height:1030px;border-radius:44px;background:var(--cream);color:var(--ink)}}
.ph{{left:70px;top:56px;width:300px;height:300px;border-radius:50%;border:12px solid var(--deep);box-shadow:0 0 0 10px var(--yel);
  background:url('{u("storefront.jpg")}') 22% 50%/auto 300px no-repeat}}
.hl{{left:0;right:0;text-align:center;top:40px;font-size:64px;color:var(--deep);line-height:1.1}}
.by{{right:70px;top:54px;font-size:0px;font-weight:700;color:#7A5A44}}
.body{{left:70px;right:70px;text-align:center;top:132px;font-size:31px;line-height:1.46;letter-spacing:-.03em;font-weight:500;color:#2B140A}}
.body p{{margin-bottom:18px}}
.call{{margin:2px 0 20px;padding:14px 26px 16px;border-radius:18px;background:#FFE7A6;border:3px solid #F6A54A;
  color:#B8430A;font-weight:800;font-size:34px;line-height:1.36;letter-spacing:-.035em}}
.body b{{font-weight:800}}
.body m{{font-weight:800;color:#C2410A;background:linear-gradient(transparent 58%,#FFE08A 58%)}}
.sign{{left:0;right:0;text-align:center;bottom:18px;font-family:'Nanum Pen Script';font-size:64px;color:#C2410A}}
.qrbox{{left:60px;top:1564px;width:190px;height:180px;border-radius:28px;background:var(--cream);display:flex;align-items:center;justify-content:center}}
.ask{{left:300px;top:1570px;font-size:42px}}
.tel{{left:296px;top:1630px;font-size:96px;white-space:nowrap;color:var(--yel);text-shadow:0 7px 0 #8A2F04;display:flex;align-items:center;gap:22px}}
.small{{left:312px;top:1692px;font-size:20px;font-weight:600;color:rgba(255,244,230,.92)}}
</style>
<img class="a" src="{u('logo_w_4x.png')}" style="left:535px;top:36px;width:170px">
<div class="a t bh sh"><span class="y">카페 사장님께</span> 드리는 편지</div>
<div class="a store"></div>
<div class="a card">
 <div class="a hl bh">사장님, 요즘 많이 힘드시죠?</div>
 <div class="a by">하복당 가맹본부</div>
 <div class="a body">
  <p>카페 하나 지키는 게 얼마나 버거운지 잘 압니다.<br>문 닫는 가게 소식이 남 얘기 같지 않으실 겁니다.</p>
  <p>‘배달은 남는 게 없다’고 생각하시죠? 맞습니다.<br>가격이 정해진 치킨·피자라면요.</p>
  <p>그런데 파인애플 250g 원가, 알고 계신가요?<br>같은 사과도 한 개에 1천 원부터 1만 원까지,<br>과일은 상품성에 따라 값이 크게 다릅니다.</p>
  <div class="call">그래서 하복당은<br>가락시장 도매회사와 직접 손을 잡았습니다.</div>
  <p>말로만 소자본이 아니라,<br>돈이 없어도 의지와 열정만 있으면<br>시작할 수 있는 브랜드를 만들고 싶었습니다.</p>
  <p>본사만 배부른 브랜드가 아니라,<br><b>함께 돈 버는 브랜드</b>를 만들겠습니다.<br>지금의 적자. 저희와 함께라면 분명 이겨낼 수 있습니다.</p>
 </div>
 <div class="a sign">하복당 가맹본부 드림</div>
</div>
<div class="a qrbox"><img src="{u('logo_o_4x.png')}" style="width:150px"></div>
<div class="a ask bh">궁금하신 점은 1:1 미팅에서 숫자로 보여드립니다.</div>
<div class="a tel bh"><span style="font-size:84px">☎</span>{PHONE}</div>
'''

for name, html in (('front', FRONT), ('back', BACK)):
    open(os.path.join(H, f'{name}.html'), 'w').write(html)
print('ok')
