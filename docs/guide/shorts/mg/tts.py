# 나레이션 TTS(단어 타이밍 포함) → 편별 timing.json + WAV
import asyncio, json, os, subprocess
import edge_tts
VOICE, RATE = 'ko-KR-SunHiNeural', '+6%'
OUT = '/tmp/mg_audio'; os.makedirs(OUT, exist_ok=True)
PX = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
SUB = [('DESIGN.md', '디자인 엠디'), ('DESIGN', '디자인'), ('gitignore', '깃 이그노어'), ('F12', '에프 십이'), ('KPI', '케이피아이'), ('AI', '에이아이'), ('1~2', '한두')]
def spoken(text):
    out, mp, i = [], [], 0
    while i < len(text):
        for a, b in SUB:
            if text.startswith(a, i):
                pos = len(''.join(out)); mp += [pos] * len(a); out.append(b); i += len(a); break
        else:
            c = text[i]; pos = len(''.join(out)); mp.append(pos)
            if c not in '“”"\'': out.append(c)
            i += 1
    s = ''.join(out); mp.append(len(s)); return s, mp
eps = json.load(open('/tmp/mg_eps.json'))
async def synth(key, i, text):
    sp, mp = spoken(text); f = f'{OUT}/{key}_{i}.mp3'; marks = []
    for attempt in range(4):
        try:
            marks = []; audio = bytearray()
            async for ch in edge_tts.Communicate(sp, VOICE, rate=RATE, proxy=PX, boundary='WordBoundary').stream():
                if ch['type'] == 'audio': audio += ch['data']
                elif ch['type'] == 'WordBoundary': marks.append((ch['text'], ch['offset'] / 1e7))
            open(f, 'wb').write(audio); break
        except Exception as e:
            if attempt == 3: raise
            await asyncio.sleep(2)
    cur = 0; mk = []
    for w, t in marks:
        j = sp.find(w, cur)
        if j < 0: continue
        mk.append([j, t]); cur = j + len(w)
    return key, i, {'text': text, 'spoken': sp, 'map': mp, 'marks': mk, 'file': f}
async def main():
    sem = asyncio.Semaphore(4)
    async def run(k, i, t):
        async with sem: return await synth(k, i, t)
    return await asyncio.gather(*[run(k, i, t) for k, v in eps.items() for i, t in enumerate(v['segs'])])
res = asyncio.run(main())
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode())
by = {}
for k, i, d in res: by.setdefault(k, {})[i] = d
timing = {}
for k, v in eps.items():
    open_ = 0.25 if v['intro'] else 1.5
    first_of_group = {g[0] for g in v['groups']}
    t = open_; segs = []
    for i in range(len(v['segs'])):
        d = by[k][i]; L = dur(d['file'])
        if i in first_of_group and i > 0: t += 0.35
        start = t; tail_marks = [[m[0], start + m[1]] for m in d['marks']]
        segs.append({'text': d['text'], 'map': d['map'], 'marks': tail_marks, 'start': start, 'end': start + L, 'file': d['file']})
        t = start + L + 0.22
    total = segs[-1]['end'] + (1.0 if v['intro'] else 1.6)
    timing[k] = {'open': 0 if v['intro'] else 1.5, 'total': total, 'segs': [{x: s[x] for x in ('text', 'map', 'marks', 'start', 'end')} for s in segs]}
    ins, flt, mix = [], [], []
    for j, s in enumerate(segs):
        ms = int(s['start'] * 1000); ins += ['-i', s['file']]
        flt.append(f'[{j}:a]aresample=44100,aformat=channel_layouts=mono,adelay={ms}|{ms}[a{j}]'); mix.append(f'[a{j}]')
    fc = ';'.join(flt) + ';' + ''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:dropout_transition=0,apad,atrim=0:{total:.3f}[o]'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', fc, '-map', '[o]', '-ac', '2', '-ar', '44100', f'{OUT}/ep{k}.wav'])
    print(k, f'{total:.1f}s', len(segs), 'segs')
json.dump(timing, open('/tmp/mg_timing.json', 'w'), ensure_ascii=False)
