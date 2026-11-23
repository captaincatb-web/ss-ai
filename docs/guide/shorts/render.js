// 사용: node render.js <편번호 0~6> <fps>  → frames/<n>/ 에 JPG 저장
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const n = +process.argv[2], fps = +(process.argv[3] || 20), only = process.argv[4] ? +process.argv[4] : null;
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(__dirname, 'shorts.html')); await p.waitForTimeout(300);
  const TM = JSON.parse(fs.readFileSync('/tmp/timemap.json'))[n]; await p.evaluate(([n, tm]) => initEp(n, tm), [n, TM]);
  const total = await p.evaluate(() => TOTAL);
  const dir = path.resolve(process.env.FRAMES || '/tmp/frames', String(n)); fs.mkdirSync(dir, { recursive: true });
  const N = Math.ceil(total * fps);
  if (only !== null) { await p.evaluate(t => setT(t), only); await p.screenshot({ path: dir + '/t.jpg', type: 'jpeg', quality: 90 }); console.log('single', only, errs.join('|')); await b.close(); return; }
  for (let i = 0; i < N; i++) { await p.evaluate(t => setT(t), i / fps); await p.screenshot({ path: path.join(dir, String(i).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 88 }); }
  console.log('ep', n, 'frames', N, errs.length ? 'ERR ' + errs.join('|') : 'ok'); await b.close();
})();
