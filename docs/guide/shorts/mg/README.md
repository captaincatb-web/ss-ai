# 모션그래픽 쇼츠 (v4)

`../../쇼츠_기획안.md` 8장의 최종 나레이션으로 만드는 모션그래픽 영상입니다. 음성의 **단어 타이밍**에 맞춰 글자·도형·숫자가 움직이고, 자막은 말하는 단어가 노란색으로 따라갑니다.

| 파일 | 역할 |
|---|---|
| `episodes.js` | 편별 나레이션(`segs`)과 장면. `data-in="w:단어"` = 그 단어를 말하는 순간 등장 |
| `index.html` | 1080×1920 렌더러(배경 모션, 글자 단위 애니메이션, 선 그리기, 숫자 카운트, 단어 하이라이트 자막) |
| `tts.py` | 음성 + 단어 타이밍(edge-tts, `ko-KR-SunHiNeural`, +6%) → `/tmp/mg_timing.json`, 편별 WAV |
| `render.js` | 30fps 프레임 캡처 (`node render.js <편> 30`), 점검용 `sheet.py` |
| `mux.sh` | `out/ep0~6.mp4`, 이어 붙인 `out/full.mp4` |
| `fonts/` | Pretendard (SIL OFL 1.1, `OFL-LICENSE.txt`) |

순서: `node dump.js` → `python3 tts.py` → `node render.js <0~6> 30` → `./mux.sh`

- 음성은 Microsoft Edge 음성 서비스로 만들어 **나레이션 문장이 외부로 전송**됩니다(공개용 교육 대본, 회사 데이터 없음).
- 화면의 숫자·업체명은 모두 가상입니다. 배경음악은 넣지 않았습니다.
- 이전 슬라이드형 버전은 `../`(shorts 폴더)에 남아 있습니다.
