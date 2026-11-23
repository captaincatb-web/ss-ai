# 나레이션 길이에 맞춰 장면 시간표를 늘리는 시간 변환표(knots) 계산 + 편별 WAV 합성
import json, os, subprocess
OUT = '/tmp/audio'; eps = json.load(open('/tmp/eps.json'))
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
MAXT = 1.12; PAD = 0.25
res = {}
for k, v in eps.items():
    segs = v['voice'] or v['caps']; off = 0.0 if v['intro'] else 1.0
    old_end = 3.2 if v['intro'] else 45.0
    knots = [[0.0, 0.0]]; cur_old = 0.0; cur_new = 0.0; plan = []
    for i, (s, e, t) in enumerate(segs):
        d = dur(f'{OUT}/{k}_{i}.mp3')
        gap = s - cur_old; cur_new += gap; cur_old = s; knots.append([cur_old, cur_new])
        D = max(e - s, d / MAXT + PAD); tempo = max(1.0, d / (D - PAD)); 
        plan.append((i, cur_new, tempo, D)); cur_new += D; cur_old = e; knots.append([cur_old, cur_new])
    tail = old_end - cur_old; cur_new += max(tail, 0.6); cur_old = max(old_end, cur_old); knots.append([cur_old, cur_new])
    res[k] = {'knots': knots, 'len': cur_new, 'off': off}
    ins = []; flt = []; mix = []
    for (i, ns, tempo, D) in plan:
        ms = int((ns + off) * 1000); ins += ['-i', f'{OUT}/{k}_{i}.mp3']
        flt.append(f'[{len(flt)}:a]aresample=44100,aformat=channel_layouts=mono,atempo={tempo:.3f},adelay={ms}|{ms}[a{i}]'); mix.append(f'[a{i}]')
    fc = ';'.join(flt) + ';' + ''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:dropout_transition=0,apad=pad_dur=1[o]'
    subprocess.check_call(['ffmpeg','-y','-loglevel','error'] + ins + ['-filter_complex', fc, '-map', '[o]', '-ac', '2', '-ar', '44100', f'{OUT}/ep{k}.wav'])
    print(k, '원래', old_end, '→ 새 길이', round(cur_new + off, 1), '초')
json.dump(res, open('/tmp/timemap.json', 'w'))
