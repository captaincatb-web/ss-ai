# 자막 파일(SRT) 생성: 새 시간표(timemap) 기준
import json
eps = json.load(open('/tmp/eps.json')); tm = json.load(open('/tmp/timemap.json'))
def f(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def new(k, old):
    kn = tm[k]['knots']
    for i in range(1, len(kn)):
        if old <= kn[i][0] + 1e-9:
            o0, n0, o1, n1 = *kn[i-1], *kn[i]
            return n1 if o1 == o0 else n0 + (n1 - n0) * (old - o0) / (o1 - o0)
    return kn[-1][1]
import os; os.makedirs('out', exist_ok=True)
for k, v in eps.items():
    if v['intro']: continue
    off = tm[k]['off']; lines = []
    for i, (s, e, t) in enumerate(v['caps'], 1): lines.append(f'{i}\n{f(new(k, s) + off)} --> {f(new(k, e) + off)}\n{t}\n')
    open(f'out/ep{k}.srt', 'w', encoding='utf-8').write('\n'.join(lines))
print('srt ok')
