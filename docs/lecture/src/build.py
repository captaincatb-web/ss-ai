# -*- coding: utf-8 -*-
"""
교육 슬라이드 조립:  head.html + d*.html(슬라이드 묶음) + tail.html  →  ../make/index.html

  python build.py          조립하고 점검(슬라이드 수·제목·이미지)
  이미지는 {{img:이름}} 자리표시자를 ../img/이름.jpg 의 data URI 로 바꿔 넣어 한 파일로 만든다.
  UTF-8 (BOM 없음)으로 저장한다.
"""
import base64
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / 'make' / 'index.html'
IMG = HERE.parent / 'img'


def read(p):
    return p.read_text(encoding='utf-8')


def main():
    chunks = sorted(HERE.glob('d[0-9][0-9]*.html'))
    html = read(HERE / 'head.html') + ''.join(read(c) for c in chunks) + read(HERE / 'tail.html')

    # 이미지 넣기
    missing = []

    def img(m):
        f = IMG / f'{m.group(1)}.jpg'
        if not f.exists():
            missing.append(m.group(1))
            return ''
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read_bytes()).decode('ascii')
    html = re.sub(r'\{\{img:([A-Za-z0-9_]+)\}\}', img, html)

    # 점검
    slides = re.findall(r'<section class="slide[^"]*"[^>]*>', html)
    bad = [s for s in slides if 'data-title="' not in s]
    titles = re.findall(r'data-title="([^"]*)"', html)
    problems = []
    if missing:
        problems.append(f'없는 이미지: {missing}')
    if bad:
        problems.append(f'data-title 없는 슬라이드 {len(bad)}개')
    if len(titles) != len(slides):
        problems.append(f'슬라이드 {len(slides)}개 ≠ 제목 {len(titles)}개')
    if html.count('<section') != html.count('</section>'):
        problems.append('<section> 열고 닫는 수가 다름')
    if '{{' in html:
        problems.append('치환되지 않은 {{…}} 가 남아 있음: ' + ', '.join(sorted(set(re.findall(r'\{\{[^}]*\}\}', html)))[:5]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding='utf-8')          # UTF-8, BOM 없음
    print(f'조립 완료: {OUT}  ({len(html.encode("utf-8")) // 1024} KB, 슬라이드 {len(slides)}개, 묶음 {len(chunks)}개)')
    if problems:
        print('※ 문제:', *problems, sep='\n   ')
        sys.exit(1)


if __name__ == '__main__':
    main()
