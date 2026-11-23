# 나레이션 음성 생성: 장면 자막(caps)을 문장 단위로 TTS → 시간표에 맞춰 편별 WAV 합성
import asyncio, json, os, re, subprocess, sys
import edge_tts
VOICE = 'ko-KR-SunHiNeural'
OUT = '/tmp/audio'; os.makedirs(OUT, exist_ok=True)
PX = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
SUB = [('DESIGN.md', '디자인 엠디'), ('F12', '에프 십이'), ('gitignore', '깃 이그노어'), ('Console', '콘솔'), ('AI', '에이아이'), ('KPI', '케이피아이'), ('310', '삼백십')]
def speak(t):
    for a, b in SUB: t = t.replace(a, b)
    return re.sub(r"[\'\"]", '', t)
eps = json.load(open('/tmp/eps.json'))
async def one(sem, key, i, text):
    f = f'{OUT}/{key}_{i}.mp3'
    async with sem:
        for _ in range(3):
            try:
                await edge_tts.Communicate(speak(text), VOICE, proxy=PX, rate='+0%').save(f); return f
            except Exception as e: err = e; await asyncio.sleep(1.5)
        raise err
async def main():
    sem = asyncio.Semaphore(4); jobs = []
    for k, v in eps.items():
        segs = v['voice'] or v['caps']; v['segs'] = segs
        for i, s in enumerate(segs): jobs.append(one(sem, k, i, s[2]))
    await asyncio.gather(*jobs)
asyncio.run(main())
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
report = []
for k, v in eps.items():
    off = 0.0 if v['intro'] else 1.0; ins = []; flt = []; mix = []
    for i, (s, e, t) in enumerate(v['segs']):
        f = f'{OUT}/{k}_{i}.mp3'; d = dur(f); slot = e - s - 0.12
        tempo = max(1.0, d / slot); tempo = min(tempo, 1.4)
        report.append((k, i, round(d, 2), round(slot, 2), round(tempo, 2), 'OVER' if d / tempo > slot + 0.05 else ''))
        ins += ['-i', f]; ms = int((s + off) * 1000)
        flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono,atempo={tempo:.3f},adelay={ms}|{ms}[a{i}]'); mix.append(f'[a{i}]')
    fc = ';'.join(flt) + ';' + ''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:dropout_transition=0,apad=pad_dur=1[o]'
    subprocess.check_call(['ffmpeg','-y','-loglevel','error'] + ins + ['-filter_complex', fc, '-map', '[o]', '-ac', '2', '-ar', '44100', f'{OUT}/ep{k}.wav'])
for r in report:
    if r[5] or r[4] > 1.2: print('주의', r)
print('audio ok', len(report), 'segments')
