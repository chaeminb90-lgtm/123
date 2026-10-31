// usage: node measure.js jobs.json outdir
// For every element with class "k", renders the page with only that element visible on a
// transparent background and saves <outdir>/<page>__<i>.png; the caller computes the ink box.
// Prints JSON {page: [{i, cls, text, png}]}.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const od = process.argv[3];
  fs.mkdirSync(od, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const res = {};
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.width, height: j.height } });
    await p.goto('file://' + j.html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    const meta = await p.evaluate(() => [...document.querySelectorAll('.k')].map((e, i) => ({ i, cls: e.className, text: e.innerText.replace(/\s+/g, ' ').slice(0, 40) })));
    const name = path.basename(j.out, '.png'); res[name] = [];
    for (const m of meta) {
      await p.evaluate((i) => {
        document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
        document.body.style.visibility = 'hidden';
        document.querySelectorAll('.k').forEach((e, n) => { e.style.visibility = n === i ? 'visible' : 'hidden'; });
      }, m.i);
      const png = path.join(od, `${name}__${m.i}.png`);
      await p.screenshot({ path: png, omitBackground: true });
      res[name].push({ ...m, png });
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(res));
})();
