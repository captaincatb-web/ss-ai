# -*- coding: utf-8 -*-
"""
실습용 가상 엑셀 만들기  ─ 실제 데이터가 아닙니다.

  python make_sample.py                  data/2026/ 에 엑셀 2개(평가결과, 영역점수)를 만듭니다
  python make_sample.py --add-year 2025  data/2025/ 에 평가결과 1개를 더 만듭니다 (과거 연도는 ①만 있어도 됩니다)
  python make_sample.py --dirty          일부러 문제 5가지를 섞어서 만듭니다 (점검 연습용)

난수 시드를 고정했으므로 누가 실행해도 같은 파일이 나옵니다.
"""
import argparse
import random
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:
    sys.exit('[오류] openpyxl 이 없습니다.  pip install openpyxl  을 실행한 뒤 다시 하세요.')

BASE_YEAR = 2026
N = 200
SEED = 20261109
INDUSTRIES = ['프레스', '사출', '전장', '가공', '표면처리', '조립']
AREAS = ['품질', '납기', '원가', '대응', '기술']


def grade_of(score):
    return 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 60 else 'D'


def make_world():
    """협력사 200개 × 5개년 점수를 한 번에 정해 둔다 (어떤 연도 파일을 만들어도 서로 맞도록)."""
    rnd = random.Random(SEED)
    world = []
    for i in range(1, N + 1):
        s = rnd.gauss(78.5, 8)
        years = {}
        for y in range(BASE_YEAR - 4, BASE_YEAR + 1):
            s = max(40.0, min(99.0, s + rnd.gauss(0.5, 2.2)))
            years[y] = round(s, 1)
        areas = {a: round(max(40.0, min(100.0, years[BASE_YEAR] + rnd.gauss(0, 5))), 1) for a in AREAS}
        world.append({'code': f'S{i:04d}', 'name': f'협력사 {i:04d}', 'group': rnd.choice(INDUSTRIES),
                      'years': years, 'areas': areas})
    return world


def write_result(path, year, world, dirty):
    """① 평가결과: 제목 줄 + 빈 줄 + 헤더(3행) 구조 — 실제 엑셀처럼 헤더가 맨 위가 아니다."""
    wb = Workbook()
    ws = wb.active
    ws.title = '평가결과'
    ws['A1'] = f'{year}년 협력사 평가결과 (가상 데이터 · 실습용)'
    ws['A1'].font = Font(bold=True, size=14)
    headers = ['협력사 코드', '협력사명', '업종', '종합 점수', '등급', '전년 종합 점수', '전년 등급']
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=j, value=h)
        c.font = Font(bold=True)
    rows = []
    for x in world:
        score = x['years'][year]
        prev = x['years'].get(year - 1)
        rows.append([x['code'], x['name'], x['group'], score, grade_of(score), prev, grade_of(prev) if prev else None])
    if dirty and year == BASE_YEAR:                      # 점검 연습용 문제 4가지(① 코드 없음 ② 중복 ③ 범위 밖 ④ 등급 불일치)
        rows[3][0] = None                                # ① 협력사 코드가 비어 있음
        rows.append(list(rows[6]))                       # ② 같은 코드가 두 번 나옴
        rows[10][3] = 105.0                              # ③ 점수가 0~100 밖
        rows[19][3], rows[19][4] = 85.0, 'A'             # ④ 점수는 85점인데 등급은 A
    for r, row in enumerate(rows, 4):
        for j, v in enumerate(row, 1):
            ws.cell(row=r, column=j, value=v)
    for col, w in zip('ABCDEFG', (13, 16, 12, 11, 7, 15, 9)):
        ws.column_dimensions[col].width = w
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return len(rows)


def write_areas(path, world, dirty):
    """② 영역점수: 2행 헤더(위 칸은 병합 셀 '영역 점수') — 그룹 행 + 컬럼 행 구조."""
    wb = Workbook()
    ws = wb.active
    ws.title = '영역점수'
    ws['B1'] = '영역 점수'
    ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=1 + len(AREAS))
    ws['B1'].alignment = Alignment(horizontal='center')
    ws['B1'].font = Font(bold=True)
    ws.cell(row=2, column=1, value='협력사 코드').font = Font(bold=True)
    for j, a in enumerate(AREAS, 2):
        ws.cell(row=2, column=j, value=a).font = Font(bold=True)
    count = 0
    for x in world:
        if dirty and x['code'] == 'S0030':               # ⑤ 평가결과에는 있는데 영역점수에는 없는 협력사
            continue
        ws.cell(row=3 + count, column=1, value=x['code'])
        for j, a in enumerate(AREAS, 2):
            ws.cell(row=3 + count, column=j, value=x['areas'][a])
        count += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return count


def main():
    ap = argparse.ArgumentParser(description='실습용 가상 엑셀 만들기')
    ap.add_argument('--add-year', type=int, help='과거 연도 평가결과 1개 추가 (예: 2025)')
    ap.add_argument('--dirty', action='store_true', help='문제 5가지를 일부러 섞는다')
    ap.add_argument('--data-dir', default=str(Path(__file__).parent / 'data'))
    a = ap.parse_args()
    data = Path(a.data_dir)
    world = make_world()
    if a.add_year:
        if not (BASE_YEAR - 4 <= a.add_year < BASE_YEAR):
            sys.exit(f'[오류] 추가할 연도는 {BASE_YEAR - 4}~{BASE_YEAR - 1} 사이여야 합니다.')
        n = write_result(data / str(a.add_year) / '평가결과.xlsx', a.add_year, world, False)
        print(f'만들었습니다: data/{a.add_year}/평가결과.xlsx ({n}행)')
        return
    n1 = write_result(data / str(BASE_YEAR) / '평가결과.xlsx', BASE_YEAR, world, a.dirty)
    n2 = write_areas(data / str(BASE_YEAR) / '영역점수.xlsx', world, a.dirty)
    print(f'만들었습니다: data/{BASE_YEAR}/평가결과.xlsx ({n1}행), data/{BASE_YEAR}/영역점수.xlsx ({n2}행)')
    if a.dirty:
        print('※ 문제 5가지를 섞었습니다. build.py 를 실행해 점검 리포트가 모두 찾아내는지 확인하세요.')


if __name__ == '__main__':
    main()
