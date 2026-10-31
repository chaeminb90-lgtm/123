// node render.js jobs.json
// job: {svg:"abs path", out:"abs png", width:px}  -> transparent PNG of the SVG at that width
//   or {html:"abs path", out:"abs png", width, height}  -> page screenshot
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  for (const j of jobs) {
    if (j.svg) {
      const p = await b.newPage({ viewport: { width: j.width + 20, height: 400 } });
      const tmp = j.out + '.html';
      fs.writeFileSync(tmp, `<html><body style="margin:0;background:transparent"><img id="i" src="file://${j.svg}" style="display:block;width:${j.width}px;height:auto"></body></html>`);
      await p.goto('file://' + tmp, { waitUntil: 'load' });
      fs.unlinkSync(tmp);
      await p.locator('#i').screenshot({ path: j.out, omitBackground: true });
      await p.close();
    } else {
      const p = await b.newPage({ viewport: { width: j.width, height: j.height } });
      await p.goto('file://' + j.html, { waitUntil: 'load' });
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
      await p.screenshot({ path: j.out, omitBackground: !!j.transparent, fullPage: !!j.full });
      await p.close();
    }
  }
  await b.close();
})();
