// node ops/flyer/render.js -> front.png, back.png (2480x3508) and 하복당_카페업종변경_전단_A4.pdf
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const H = __dirname; const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const pdfs = [];
  for (const n of ['front', 'back']) {
    const p = await b.newPage({ viewport: { width: 1240, height: 1754 }, deviceScaleFactor: 2 });
    await p.goto('file://' + path.join(H, n + '.html'), { waitUntil: 'load' });
    await p.evaluate(async () => { for (const f of ['40px "Black Han Sans"', '700 40px PT', '400 40px "Nanum Pen Script"']) { try { await document.fonts.load(f, '하복당 가나다 0123'); } catch (e) {} } await document.fonts.ready; }); await p.waitForTimeout(600);
    await p.screenshot({ path: path.join(H, n + '.png') });
    await p.pdf({ path: path.join(H, n + '.pdf'), width: '210mm', height: '297mm', printBackground: true, scale: 210 / (1240 * 25.4 / 96), margin: { top: 0, right: 0, bottom: 0, left: 0 }, pageRanges: '1' });
    await p.close();
  }
  await b.close();
})();
