// node render.js <편> <fps>        → /tmp/mg_frames/<편>/*.jpg
// node render.js <편> sheet t1,t2…  → /tmp/mg_sheet_<편>_<i>.jpg (점검용)
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
(async () => {
  const n = process.argv[2], mode = process.argv[3] || '30';
  const TM = JSON.parse(fs.readFileSync('/tmp/mg_timing.json'))[n];
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(__dirname, 'index.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.evaluate(([n, tm]) => initEp(n, tm), [+n, TM]);
  if (mode === 'sheet') { const ts = process.argv[4].split(',').map(Number); for (let i = 0; i < ts.length; i++) { await p.evaluate(t => setT(t), ts[i]); await p.screenshot({ path: `/tmp/mg_sheet_${n}_${i}.jpg`, type: 'jpeg', quality: 80 }); } console.log(n, 'sheet', errs.join(' | ') || 'ok'); await b.close(); return; }
  const fps = +mode, N = Math.ceil(TM.total * fps), dir = `/tmp/mg_frames/${n}`; fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < N; i++) { await p.evaluate(t => setT(t), i / fps); await p.screenshot({ path: `${dir}/${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 88 }); }
  console.log('ep', n, N, 'frames', errs.join(' | ') || 'ok'); await b.close();
})();
