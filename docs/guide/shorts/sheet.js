// 점검용: 편마다 장면 중간 시점 프레임을 한 장에 모아 저장 (node sheet.js <편>)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const n = +process.argv[2]; const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })).newPage();
  await p.goto('file://' + path.resolve(__dirname, 'shorts.html')); await p.waitForTimeout(300); await p.evaluate(n => initEp(n), n);
  const times = await p.evaluate(() => scenes.map(s => [s.s + (s.e - s.s) * 0.75, s.s + 0.5]).flat().map(x => x + 1.0));
  const out = []; for (let i = 0; i < times.length; i++) { await p.evaluate(t => setT(t), times[i]); const f = `/tmp/sh_${n}_${i}.jpg`; await p.screenshot({ path: f, type: 'jpeg', quality: 80 }); out.push(f); }
  console.log(JSON.stringify(out)); await b.close();
})();
