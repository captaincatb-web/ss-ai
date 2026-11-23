# 장면마다 '첫 대사 끝 무렵'과 '마지막 대사 끝 무렵' 시점을 뽑아 한 장으로
import json, subprocess, sys
from PIL import Image
T = json.load(open('/tmp/mg_timing.json')); E = json.load(open('/tmp/mg_eps.json'))
for n in sys.argv[1:]:
    segs = T[n]['segs']; ts = [0.7] if T[n]['open'] else []
    for g in E[n]['groups']: ts += [segs[g[0]]['end'] - .1, (segs[g[-1]]['start']+segs[g[-1]]['end'])/2]
    subprocess.run(['node', 'render.js', n, 'sheet', ','.join(f'{t:.2f}' for t in ts)], check=True)
    ims = [Image.open(f'/tmp/mg_sheet_{n}_{i}.jpg').resize((270, 480)) for i in range(len(ts))]
    s = Image.new('RGB', (276 * len(ims) + 6, 492), (60, 60, 70)); x = 6
    for im in ims: s.paste(im, (x, 6)); x += 276
    s.save(f'/tmp/mg_sheet_{n}.png')
