# -*- coding: utf-8 -*-
"""
가이드 조립:  head.html + [a-e]_*.html(쪽 묶음) + tail.html  →  ../index.html   (UTF-8, BOM 없음)

  python build.py        조립하고 점검한다(쪽 수 · id · 이미지 · 치환 안 된 자리표시자)
  이미지는 {{img:이름}} 을 ../img/이름.jpg 의 data URI 로 바꿔 넣어 한 파일로 만든다.
"""
import base64
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / 'index.html'
IMG = HERE.parent / 'img'


def main():
    chunks = sorted(HERE.glob('[a-z]_*.html'))
    html = (HERE / 'head.html').read_text(encoding='utf-8') + ''.join(c.read_text(encoding='utf-8') for c in chunks) + (HERE / 'tail.html').read_text(encoding='utf-8')
    missing = []

    def img(m):
        f = IMG / f'{m.group(1)}.jpg'
        if not f.exists():
            missing.append(m.group(1))
            return ''
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read_bytes()).decode('ascii')
    html = re.sub(r'\{\{img:([A-Za-z0-9_]+)\}\}', img, html)
    ids = re.findall(r'<section class="sheet[^"]*" id="(p\d+)"', html)
    problems = []
    if missing:
        problems.append(f'없는 이미지: {missing}')
    if len(ids) != html.count('<section class="sheet'):
        problems.append('id 없는 쪽이 있음')
    if len(set(ids)) != len(ids):
        problems.append('중복된 쪽 id')
    if html.count('<section') != html.count('</section>'):
        problems.append('<section> 열고 닫는 수가 다름')
    links = set(re.findall(r'href="#(p\d+)"', html)) - set(ids)
    if links:
        problems.append(f'없는 쪽으로 가는 링크: {sorted(links)}')
    if '{{' in html:
        problems.append('치환되지 않은 {{…}} 가 남아 있음')
    OUT.write_text(html, encoding='utf-8')
    print(f'조립 완료: {OUT}  ({len(html.encode("utf-8")) // 1024} KB, 쪽 {len(ids)}개, 묶음 {len(chunks)}개)')
    if problems:
        print('※ 문제:', *problems, sep='\n   ')
        sys.exit(1)


if __name__ == '__main__':
    main()
