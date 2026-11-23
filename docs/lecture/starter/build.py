# -*- coding: utf-8 -*-
"""
엑셀 → dist/ (정적 대시보드) 빌드

    python build.py                          기본: ./data 를 읽어 ./dist 를 만든다
    python build.py --data-dir D:\\엑셀 --out dist    엑셀 위치를 인자로 지정 (경로를 코드에 적지 않는다)

네 단계:  ① 읽기(Read) → ② 정리(Normalize) → ③ 계산(Compute) → ④ 내보내기(Emit)
  ①②는 "엑셀을 믿지 않는" 단계, ③④는 "화면이 쓰기 좋은 모양을 만드는" 단계입니다.
"""
import argparse
import difflib
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit('[오류] openpyxl 이 없습니다.  pip install openpyxl  을 실행한 뒤 다시 하세요.')

try:
    sys.stdout.reconfigure(errors='replace')      # 콘솔이 못 쓰는 글자가 있어도 멈추지 않게
except AttributeError:
    pass

HERE = Path(__file__).parent
WARNINGS = []        # 점검 중 모은 경고.  경고가 0건이 아니면 배포하지 않는다.
REPORT = []          # data_check.txt 에 적을 줄


def say(tag, msg):
    line = f'[{tag}] {msg}'
    print(line)
    REPORT.append(line)


def warn(msg):
    WARNINGS.append(msg)
    say('경고', msg)


def fail(msg):
    sys.exit(f'[오류] {msg}')


# ───────────── 설정 읽기 ─────────────
def read_settings(path):
    """settings.js 는 'window.SUPPLIER_SETTINGS = {…}' 모양의 JSON 호환 파일. 줄 맨 앞 // 주석만 지운다."""
    lines = [ln for ln in Path(path).read_text(encoding='utf-8').splitlines() if not ln.strip().startswith('//')]
    body = '\n'.join(lines)
    return json.loads(body[body.index('=') + 1:].strip().rstrip(';'))


# ───────────── ① 읽기 : 엑셀 한 파일 → 행 목록 (있는 그대로) ─────────────
def norm(s):
    """비교용 이름: 공백·줄바꿈 제거, 전각→반각, 소문자.  '종합 점수' = '종합점수'"""
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(s if s is not None else ''))).lower()


def read_excel(path, code_names):
    wb = load_workbook(path, data_only=True)            # data_only: 수식이 아니라 저장된 값을 읽는다
    rows = list(wb.worksheets[0].iter_rows(values_only=True))
    want = {norm(n) for n in code_names}
    # 헤더 행: 위쪽 10행 중 '협력사 코드'(또는 동의어)가 들어 있는 행.  제목 줄·빈 줄이 위에 있어도 된다.
    h = next((i for i, r in enumerate(rows[:10]) if any(norm(c) in want for c in r)), None)
    if h is None:
        fail(f'{path.name}: 위쪽 10행에서 "{code_names[0]}" 헤더를 찾지 못했습니다. settings.js 의 columns.code 를 확인하세요.')
    header = [str(c).strip() if c is not None else '' for c in rows[h]]
    # 그룹 행: 헤더 바로 위 줄에 (첫 칸 말고) 값이 있으면 그룹 이름.  병합 셀은 첫 칸에만 값이 있으므로 오른쪽으로 채운다.
    group = [''] * len(header)
    if h > 0 and any(c not in (None, '') for c in rows[h - 1][1:]):
        last = ''
        for j, c in enumerate(rows[h - 1][:len(header)]):
            if c not in (None, ''):
                last = str(c).strip()
            group[j] = last if j > 0 else ''
    keys = [f'{g}.{n}' if g and n else n for g, n in zip(group, header)]       # 예: '영역 점수.품질'
    data = [dict(zip(keys, r)) for r in rows[h + 1:] if any(c not in (None, '') for c in r)]
    return data, keys, h + 1


# ───────────── ② 정리 : 이름·숫자·빈칸 ─────────────
def find_col(keys, names, label, required=True):
    """동의어 목록에서 처음 찾은 열을 돌려준다.  없으면 가장 비슷한 이름을 알려 주고 멈춘다."""
    table = {norm(k): k for k in keys}
    table.update({norm(k.split('.')[-1]): k for k in keys})       # 그룹 이름 없이 마지막 이름만으로도 찾기
    for n in names:
        if norm(n) in table:
            return table[norm(n)]
    if required:
        close = difflib.get_close_matches(norm(names[0]), list(table), n=3, cutoff=0.3)
        fail(f'필수 열 "{label}"({names[0]})을(를) 찾지 못했습니다. 비슷한 이름: {", ".join(table[c] for c in close) or "없음"}\n'
             f'       → 엑셀의 열 이름과 맞는 것을 settings.js 의 columns.{label} 에 동의어로 추가하세요.')
    return None


def num(v):
    """'85.5', ' 87점', '90%' → 숫자, 빈 값·글자 → None"""
    if v in (None, ''):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = re.sub(r'[^\d.\-]', '', str(v))
    try:
        return float(t)
    except ValueError:
        return None


def grade_of(score, cut):
    """등급 계산은 여기 한 곳에서만 한다 (경계값: 90.0 → A, 89.9 → B)"""
    if score >= cut['A']: return 'A'
    if score >= cut['B']: return 'B'
    if score >= cut['C']: return 'C'
    return 'D'


# ───────────── 연도 폴더 하나 읽기 ─────────────
def load_year(folder, S):
    """폴더 안 엑셀들을 읽는다. 파일 이름은 보지 않고, 어떤 열이 있는지(헤더)로 종류를 판별한다."""
    C = S['columns']
    result, areas, info = None, None, []
    for f in sorted(folder.glob('*.xlsx')):
        if f.name.startswith('~$'):                      # 엑셀이 열려 있을 때 생기는 임시 파일
            say('건너뜀', f'{folder.name}/{f.name} (엑셀 임시 파일)')
            continue
        rows, keys, hrow = read_excel(f, C['code'])
        if sum(1 for a in S['areas'] if find_col(keys, [a], a, required=False)) >= 2:
            kind = '영역점수'
            areas = (rows, keys)
        elif find_col(keys, C['score'], 'score', required=False) or find_col(keys, C['grade'], 'grade', required=False):
            find_col(keys, C['score'], 'score')              # 점수 열이 없으면 여기서 안내하고 멈춘다
            kind = '평가결과'
            result = (rows, keys)
        else:
            say('건너뜀', f'{folder.name}/{f.name} (종류를 알 수 없음)')
            continue
        say('읽기', f'{folder.name}/{f.name} → {kind}, 헤더 {hrow}행, {len(rows)}행')
        info.append(kind)
    return result, areas, info


def table_of(result, S):
    """평가결과 행들을 {코드: {...}} 로 정리 (정리 단계 + 점검)"""
    rows, keys = result
    C = S['columns']
    col = {k: find_col(keys, C[k], k, required=(k in ('code', 'score'))) for k in C}
    out, seen = {}, set()
    n_nocode = n_dup = n_range = 0
    n_gradebad, gradebad_ex = 0, []
    for r in rows:
        code = str(r.get(col['code']) or '').strip()
        if not code:
            n_nocode += 1
            continue
        if code in seen:
            n_dup += 1
            continue
        seen.add(code)
        score, prev = num(r.get(col['score'])), num(r.get(col['prev'])) if col['prev'] else None
        if score is None or not 0 <= score <= 100:
            n_range += 1
            continue
        want = grade_of(score, S['gradeCut'])
        given = str(r.get(col['grade']) or '').strip().upper() if col['grade'] else ''
        if given and given != want:
            n_gradebad += 1
            gradebad_ex.append(f'{code}({score}점: 엑셀 {given} ≠ 계산 {want})')
        out[code] = {'code': code,
                     'name': str(r.get(col['name']) or code).strip() if col['name'] else code,
                     'group': str(r.get(col['group']) or '기타').strip() if col['group'] else '기타',
                     'score': score, 'grade': want, 'prev': prev,
                     'prevGrade': grade_of(prev, S['gradeCut']) if prev is not None else None}
    return out, (n_nocode, n_dup, n_range, n_gradebad, gradebad_ex)


# ───────────── ③ 계산 ─────────────
def compute(years, S):
    base = max(y for y, d in years.items() if d['areas'] and d['result'])   # 기준연도 = 두 파일이 모두 있는 가장 큰 연도
    tables = {y: table_of(d['result'], S) for y, d in years.items() if d['result']}
    cur, checks = tables[base]
    n_nocode, n_dup, n_range, n_gradebad, ex = checks
    if n_nocode: warn(f'협력사 코드가 없는 행 {n_nocode}개 → 제외했습니다.')
    if n_dup: warn(f'협력사 코드가 중복된 행 {n_dup}개 → 처음 나온 행만 사용했습니다.')
    if n_range: warn(f'점수가 비었거나 0~100 밖인 행 {n_range}개 → 제외했습니다.')
    if n_gradebad: warn(f'엑셀의 등급과 점수로 계산한 등급이 다른 협력사 {n_gradebad}개 (예: {", ".join(ex[:3])}) → 계산한 등급을 씁니다.')

    # 영역점수 붙이기 + 키 불일치 점검
    arows, akeys = years[base]['areas']
    acode = find_col(akeys, S['columns']['code'], 'code')
    acol = {a: find_col(akeys, [a], a) for a in S['areas']}
    area_by_code = {str(r.get(acode) or '').strip(): r for r in arows}
    only_result = sorted(set(cur) - set(area_by_code))
    only_area = sorted(c for c in set(area_by_code) - set(cur) if c)
    if only_result or only_area:
        warn(f'키 불일치: 평가결과에만 있음 {len(only_result)}개 {only_result[:3]}, 영역점수에만 있음 {len(only_area)}개 {only_area[:3]}')
    yrs = list(range(base - 4, base + 1))
    suppliers = []
    for code, x in cur.items():
        r = area_by_code.get(code)
        x['areas'] = {a: num(r.get(acol[a])) for a in S['areas']} if r else {a: None for a in S['areas']}
        hist = {}
        for y in yrs:                                    # 추이: 기준연도 평가 협력사(코호트)의 과거 점수
            if y in tables:
                hist[y] = (tables[y][0].get(code) or {}).get('score')
            elif y + 1 in tables:                        # 그 해 파일이 없으면 다음 해 파일의 '전년 점수'로 채운다
                hist[y] = (tables[y + 1][0].get(code) or {}).get('prev')
            else:
                hist[y] = None
        x['hist'] = hist
        suppliers.append(x)
    suppliers.sort(key=lambda x: x['code'])

    n = len(suppliers)
    avg = lambda vals: round(sum(vals) / len(vals), 1) if vals else None
    counts = {g: sum(1 for x in suppliers if x['grade'] == g) for g in 'ABCD'}
    summary = {'count': n, 'avgScore': avg([x['score'] for x in suppliers]),
               'avgPrev': avg([x['prev'] for x in suppliers if x['prev'] is not None]), 'gradeCounts': counts}
    avail = [y for y in yrs if any(x['hist'][y] is not None for x in suppliers)]
    meta = {'baseYear': base, 'years': yrs, 'yearsAvailable': avail,
            'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'), 'source': S.get('sourceLabel', '')}
    return {'meta': meta, 'summary': summary, 'suppliers': suppliers}


# ───────────── ④ 내보내기 ─────────────
def emit(model, out):
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    (out / 'data.js').write_text('window.__DATA__ = ' + json.dumps(model, ensure_ascii=False) + ';\n', encoding='utf-8')
    shutil.copy(HERE / 'settings.js', out / 'settings.js')
    html = (HERE / 'src' / 'index.html').read_text(encoding='utf-8').replace('__BUILD__', stamp)    # 캐시 방지용 버전
    (out / 'index.html').write_text(html, encoding='utf-8')
    REPORT.append(f'[결론] {"경고 0건 - 배포해도 좋습니다." if not WARNINGS else f"경고 {len(WARNINGS)}건 - 확인하기 전에는 배포하지 마세요."}')
    (out / 'data_check.txt').write_text('\n'.join(REPORT) + '\n', encoding='utf-8')
    return (out / 'data.js').stat().st_size


def main():
    ap = argparse.ArgumentParser(description='엑셀 → dist/ 빌드')
    ap.add_argument('--data-dir', default=str(HERE / 'data'), help='엑셀 폴더 (연도별 하위 폴더)')
    ap.add_argument('--out', default=str(HERE / 'dist'), help='만들어질 폴더')
    a = ap.parse_args()
    data, out = Path(a.data_dir), Path(a.out)
    S = read_settings(HERE / 'settings.js')
    folders = sorted(p for p in data.glob('*') if p.is_dir() and re.fullmatch(r'\d{4}', p.name)) if data.exists() else []
    if not folders:
        fail(f'엑셀 폴더가 없습니다: {data}\n       data/2026/ 처럼 연도 폴더를 만들고 엑셀을 넣으세요. (연습: python make_sample.py)')
    years = {}
    for f in folders:                                                                # ① 읽기
        result, areas, _ = load_year(f, S)
        years[int(f.name)] = {'result': result, 'areas': areas}
    if not any(d['areas'] and d['result'] for d in years.values()):
        fail('평가결과와 영역점수가 모두 있는 연도 폴더가 없습니다. (기준연도는 두 파일이 다 있어야 합니다)')
    model = compute(years, S)                                                        # ②③ 정리·계산
    m, s = model['meta'], model['summary']
    say('정리', f'기준연도 {m["baseYear"]} · 협력사 {s["count"]}개 · 추이 자료 {len(m["yearsAvailable"])}/5개년 {m["yearsAvailable"]}')
    say('정답값', f'평균 {s["avgScore"]}점(전년 {s["avgPrev"]}) · A {s["gradeCounts"]["A"]} / B {s["gradeCounts"]["B"]} / C {s["gradeCounts"]["C"]} / D {s["gradeCounts"]["D"]}')
    say('점검', f'경고 {len(WARNINGS)}건')
    size = emit(model, out)                                                          # ④ 내보내기
    say('내보내기', f'{out}/ → index.html, settings.js, data.js({size // 1024}KB), data_check.txt')
    print('경고 0건 - 배포해도 좋습니다.' if not WARNINGS else f'경고 {len(WARNINGS)}건 - data_check.txt 를 읽고 원인을 확인하세요.')


if __name__ == '__main__':
    main()
