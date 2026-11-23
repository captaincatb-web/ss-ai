# 쇼츠 제작 도구 (6편 + 인트로)

`../쇼츠_기획안.md`의 대본을 영상으로 만드는 스크립트입니다. 화면은 HTML로 그리고(Playwright로 프레임 캡처), 나레이션은 TTS로 만들어 ffmpeg로 합칩니다. 결과 영상(`out/*.mp4`)은 용량이 커서 저장소에 올리지 않습니다.

| 파일 | 역할 |
|---|---|
| `shorts.html` | 1080×1920 화면 렌더러 (장면·자막·애니메이션을 시간 함수로 그림) |
| `episodes.js` | 편별 장면 정의 · 자막(= 나레이션 문장) · 시간표. **내용을 고치려면 여기** |
| `render.js` | `node render.js <편 0~6> 20` 프레임(JPG) 저장 |
| `make_audio.py` | 자막 문장을 음성(edge-tts, `ko-KR-SunHiNeural`)으로 변환 |
| `timemap.py` | 나레이션 길이에 맞춰 장면 시간을 늘리고 편별 WAV 합성 |
| `make_srt.py` | 편별 자막 파일(SRT) |
| `mux.sh` | 프레임 + 음성 → `out/ep0~6.mp4`, 이어 붙인 `out/full.mp4` |
| `sheet.js` | 점검용 (장면별 대표 프레임 캡처) |

순서: `node dump.js` → `python3 make_audio.py` → `python3 timemap.py` → `node render.js <n> 20` (0~6) → `./mux.sh` → `python3 make_srt.py`

주의
- 음성은 Microsoft Edge 음성 서비스(edge-tts)로 만들며, **나레이션 문장(공개용 교육 대본)이 외부 서비스로 전송**됩니다. 회사 데이터는 대본에 없습니다. 사내 방송용으로 쓸 때는 사내 정책을 확인하세요.
- 화면의 숫자·업체명은 전부 가상입니다(협력사 5곳 92·84·79·55·빈칸).
- 목소리·속도를 바꾸려면 `make_audio.py`의 `VOICE`, `rate`를 고치고 다시 실행합니다. 사람 목소리로 녹음해 쓰려면 `/tmp/audio/ep<n>.wav` 대신 녹음 파일로 `mux.sh`를 돌리면 됩니다.
