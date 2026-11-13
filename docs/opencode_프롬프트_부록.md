# 협력사 종합평가 대시보드 — opencode 구현 프롬프트 (부록)

> 이 부록은 목업 `종합평가_대시보드_목업.html`에서 **그대로 추출**한 정밀 자료입니다. 본문(`opencode_프롬프트_본문.md`)의 §9 서술과 다르게 보이는 곳이 있으면 **이 부록의 코드가 기준**입니다.
>
> **구성**: A. CSS · B. HTML 뼈대(AI 대화 패널 포함) · C. 설정·컬럼 매핑 · D. 공통 참조 코드(유틸·포맷·툴팁·카드·차트·상태·라우팅) · E. 샘플 데이터 생성기 · F. 골든 값(정답 숫자) · G. 화면 참조 코드(결과 요약·항목별·협력사별)
>
> **사용법**: 자기 구조(파일 분리, 프레임워크 사용 등)에 맞게 옮겨도 되지만 **수치·수식·문구·호출 순서는 바꾸지 않습니다.** 목업은 가상 데이터로 `file://`에서 단독 실행되는 한 파일입니다. 실제 구현에서 달라져야 하는 곳:
> 1. **데이터**: 샘플 생성기(E) 대신 `window.__SUPPLIER_DATA__`를 읽습니다(본문 §6.4). 협력사 식별자는 `code` 대신 `key`를 씁니다.
> 2. **설정**: `CONFIG`(C)는 `config/settings.js`(본문 §11)로 옮기고 `criteria`는 선언형 규칙으로 바꿉니다. 영역 `max`(배점)는 데이터(`{영역}-배점` 중앙값)에서 계산합니다.
> 3. **고정 값**: 「2026-11-09」「최종 갱신 …」「데이터: 가상 샘플 (목업)」「2026년 평가」 같은 문구는 데이터/설정에서 채웁니다.
> 4. **세부항목(④)**: 목업의 `subItems()`는 가상 값을 만듭니다 → 실제는 `data.subItems[key][항목코드]`.
> 5. **협력사별 결과의 기본 선택**: 목업의 「평가조직 3곳 + 등급 하락」은 시연용 → 실제는 목록의 첫 협력사.
> 6. **전년 없는 협력사(신규)**: 목업은 모든 협력사에 전년이 있다고 가정합니다 → 본문 §6.8대로 null을 처리합니다.
> 7. **AI 대화 패널**(섹션 10, 부록 A의 `.chat-*` CSS, 부록 B의 `#chat-root`): **화면과 열고 닫는 동작만** 있고 LLM 호출 코드는 없습니다. `window.SUPPLIER_CHAT.ask`가 정의돼 있으면 그것을 부르고(사내 API는 사용자가 따로 연결), 없으면 「API 미연결」 데모 답변을 보여 줍니다. **이 코드에 LLM 주소·키·호출 코드를 넣지 마세요**(본문 §9.5).
> 8. **옮기지 않아도 되는 미사용 조각**: `ACT.all`, `ACT.d`, `openArea`, `niceMax`, `roundTop`, 샘플의 `change`·`orgGrade` 필드, CSS `.bigtrio` `.ins` `.detail-tag` `.gline` `.seg-ctl`.

---

## 부록 A. CSS (`src/styles.css` 그대로)

```css
:root{
  --page:#f3f5f9; --surface:#fff; --surface-2:#f6f8fb; --ink:#0f172a; --ink-2:#475569; --muted:#64748b;
  --grid:#e6eaf0; --axis:#c5cdd8; --border:rgba(15,23,42,.09); --shadow:0 1px 2px rgba(15,23,42,.04),0 4px 14px rgba(15,23,42,.05);
  --accent:#2a78d6; --accent-ink:#1c5cab; --key-bg:#eef5ff; --key-border:#b7d3f6;
  --ctx:#b4bcc8; --bench:#475569; --track:#dce9fb; --track-bad:#fbe1e0;
  --good-text:#1c5cab; --bad-text:#c62828; --warn-text:#8a5a00;
  --chip-blue:rgba(42,120,214,.12); --chip-bad:rgba(208,59,59,.12); --chip-warn:rgba(250,178,25,.22); --chip-gray:rgba(15,23,42,.06);
  --side:#0f1d3d; --side-ink:#c9d3e6; --side-muted:#8796b5; --side-active:#f5a524; --side-active-ink:#1a1300;
  color-scheme:light;
}
:root[data-theme="dark"]{
  --page:#0d1016; --surface:#161a22; --surface-2:#1c212b; --ink:#eef1f6; --ink-2:#c3cad6; --muted:#8d97a8;
  --grid:#262c38; --axis:#3a4252; --border:rgba(255,255,255,.08); --shadow:none;
  --accent:#3987e5; --accent-ink:#86b6ef; --key-bg:#13233d; --key-border:#1c5cab;
  --ctx:#4a5361; --bench:#c3cad6; --track:#13325c; --track-bad:#4a2326;
  --good-text:#86b6ef; --bad-text:#f07373; --warn-text:#f5b83d;
  --chip-blue:rgba(57,135,229,.18); --chip-bad:rgba(208,59,59,.24); --chip-warn:rgba(250,178,25,.20); --chip-gray:rgba(255,255,255,.07);
  --side:#0a1122; --side-ink:#c9d3e6; --side-muted:#7f8db0;
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--page);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif;-webkit-font-smoothing:antialiased;word-break:keep-all}
button,input,select{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
[hidden]{display:none!important}
.num,.tn{font-variant-numeric:tabular-nums}

/* ── 레이아웃 ── */
.app{display:grid;grid-template-columns:224px minmax(0,1fr);min-height:100vh;background:linear-gradient(to right,var(--side) 224px,transparent 224px)}
.sidebar{background:var(--side);color:var(--side-ink);padding:20px 14px;display:flex;flex-direction:column;gap:22px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:10px;padding:2px 6px}
.brand-mark{width:38px;height:38px;border-radius:10px;border:1.5px solid var(--side-active);display:grid;place-items:center;color:var(--side-active);flex:none}
.brand-t{font-weight:700;font-size:15px;line-height:1.2;color:#fff}
.brand-s{font-size:11px;color:var(--side-muted)}
.nav{display:flex;flex-direction:column;gap:4px}
.nav a{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;color:var(--side-ink);text-decoration:none;font-weight:600;font-size:13.5px;white-space:nowrap}
.nav a small{display:block;font-weight:500;font-size:11px;color:var(--side-muted)}
.nav a:hover{background:rgba(255,255,255,.07)}
.nav a[aria-current="page"]{background:var(--side-active);color:var(--side-active-ink)}
.nav a[aria-current="page"] small{color:rgba(26,19,0,.7)}
.nav svg{width:18px;height:18px;flex:none}
.side-foot{margin-top:auto;font-size:11.5px;color:var(--side-muted);border-top:1px solid rgba(255,255,255,.08);padding-top:14px;display:grid;gap:4px}
.main{min-width:0;padding:20px 24px 48px;display:flex;flex-direction:column;gap:14px}
.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap}
.eyebrow{margin:0;font-size:12px;font-weight:700;color:var(--accent-ink);letter-spacing:.02em}
.topbar h1{margin:2px 0 0;font-size:23px;letter-spacing:-.01em}
.topbar .lead{margin:4px 0 0;color:var(--ink-2);font-size:13.5px}
.top-actions{display:flex;gap:8px;align-items:center}
.btn{height:34px;padding:0 12px;border-radius:8px;border:1px solid var(--border);background:var(--surface);cursor:pointer;font-weight:600;font-size:13px;display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.btn:hover{background:var(--surface-2)}
.btn svg{width:15px;height:15px}
.btn.primary{background:var(--accent);color:#fff;border-color:transparent}
.btn.primary:hover{filter:brightness(1.06);background:var(--accent)}
.btn.sm{height:28px;padding:0 9px;font-size:12px;border-radius:7px}
.btn[aria-pressed="true"]{background:var(--chip-blue);border-color:transparent;color:var(--accent-ink)}
.link{background:none;border:0;padding:0;color:var(--accent-ink);font-weight:700;font-size:12.5px;cursor:pointer;display:inline-flex;align-items:center;gap:3px;white-space:nowrap}
.link:hover{text-decoration:underline}
.filters{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:flex-end;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 12px;box-shadow:var(--shadow)}
.f{display:flex;flex-direction:column;gap:3px;min-width:120px;flex:1}
.f label{font-size:11px;color:var(--muted);font-weight:600}
.f select,.f input{height:34px;border:1px solid var(--border);background:var(--surface-2);border-radius:8px;padding:0 10px;min-width:0}
.active-f{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--ink-2);margin-top:-4px}
.active-f:empty{display:none}
.fchip{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 6px 0 10px;border-radius:999px;background:var(--chip-blue);color:var(--accent-ink);font-weight:600;border:0;cursor:pointer}
.fchip b{font-weight:800}
.empty{background:var(--surface);border:1px dashed var(--axis);border-radius:12px;padding:28px;text-align:center;color:var(--ink-2)}

/* ── 섹션 / 카드 ── */
.page{display:flex;flex-direction:column;gap:14px}
.sec-h{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin:10px 2px -4px}
.sec-h h2{margin:0;font-size:16px;letter-spacing:-.01em}
.sec-h p{margin:0;font-size:12.5px;color:var(--muted)}
.sec-h .no{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--ink);color:var(--surface);font-size:12px;font-weight:800;align-self:center}
.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:14px}
.span-3{grid-column:span 3}.span-4{grid-column:span 4}.span-5{grid-column:span 5}.span-6{grid-column:span 6}.span-7{grid-column:span 7}.span-8{grid-column:span 8}.span-12{grid-column:span 12}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;box-shadow:var(--shadow);min-width:0;display:flex;flex-direction:column;gap:12px}
.card-h{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.card-h h3{margin:0;font-size:14.5px;font-weight:700;display:flex;align-items:center;gap:6px}
.card-h .sub{margin:2px 0 0;font-size:12px;color:var(--muted)}
.tools{display:flex;gap:6px;flex:none;align-items:center}
.info{width:20px;height:20px;border-radius:50%;border:1px solid var(--border);background:var(--surface);color:var(--muted);font-size:11px;font-weight:800;cursor:help;display:inline-grid;place-items:center;padding:0;flex:none}
.tbl-view{display:none}
.card.show-table .chart-view{display:none}
.card.show-table .tbl-view{display:block}
.chart-view{display:flex;flex-direction:column;gap:10px;min-width:0}
.card-f{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-top:auto;padding-top:10px;border-top:1px solid var(--grid)}
.card-f>.btn:only-child{margin-left:auto}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--ink-2)}
.legend:empty{display:none}
.lg{display:inline-flex;align-items:center;gap:6px}
.lg-rect{width:10px;height:10px;border-radius:2px}
.lg-line{width:16px;height:2px;border-radius:1px}
.lg-dash{width:16px;height:0;border-top:2px dashed var(--bench)}
.lg-tick{width:2px;height:12px;background:var(--bench);border-radius:1px}
.muted{color:var(--muted)}
.note{font-size:11.5px;color:var(--muted);margin:0}

/* ── 인사이트 ("그래서?") ── */
.callout{display:flex;gap:8px;align-items:flex-start;padding:9px 11px;border-radius:9px;font-size:12.5px;color:var(--ink-2);background:var(--surface-2)}
.callout svg{width:15px;height:15px;flex:none;margin-top:2px}
.callout b{color:var(--ink)}
.callout.bad{background:var(--chip-bad)} .callout.bad svg{color:var(--bad-text)}
.callout.good{background:var(--chip-blue)} .callout.good svg{color:var(--good-text)}
.callout.warn{background:var(--chip-warn)} .callout.warn svg{color:var(--warn-text)}
.callout .link{margin-left:auto;align-self:center}

/* ── KPI ── */
.kpis{display:grid;grid-template-columns:1.35fr repeat(4,minmax(0,1fr));gap:14px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:6px;min-width:0}
.kpi.key{background:var(--key-bg);border-color:var(--key-border)}
.kpi-top{display:flex;gap:8px;align-items:center;justify-content:space-between}
.kpi-label{font-size:12.5px;color:var(--ink-2);font-weight:700;display:flex;align-items:center;gap:6px}
.kpi-label svg{width:15px;height:15px}
.kpi-val{font-size:26px;font-weight:750;letter-spacing:-.02em;line-height:1.15}
.kpi.key .kpi-val{font-size:34px}
.kpi-val small{font-size:14px;font-weight:600;color:var(--ink-2);margin-left:3px}
.kpi-row{font-size:12px;color:var(--muted);display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.kpi .meter{margin-top:4px}
.kpi .link{margin-top:auto;padding-top:4px}
.atiles{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:10px}
.atile{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px;text-align:left;cursor:pointer;display:flex;flex-direction:column;gap:5px;box-shadow:var(--shadow);min-width:0}
.atile:hover{border-color:var(--axis)}
.atile[aria-pressed="true"]{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset;background:var(--key-bg)}
.atile .nm{font-weight:800;font-size:13px;display:flex;justify-content:space-between;gap:4px}
.atile .nm span{font-weight:600;color:var(--muted);font-size:11px}
.atile .v{font-size:22px;font-weight:750;line-height:1.1;letter-spacing:-.01em}
.atile .st{font-size:11.5px;font-weight:700}
.atile .meter{flex:none;width:100%}

/* ── 차트 부품 ── */
.chart{position:relative;width:100%}
.chart svg{display:block;overflow:visible}
.hb{display:flex;flex-direction:column}
.hb-row{display:grid;grid-template-columns:var(--lw,96px) minmax(0,1fr) var(--vw,52px) var(--ew,0px);column-gap:10px;align-items:center;padding:0 4px;border-radius:6px}
.hb-row:not(.hb-head):hover,.hb-row:focus-visible{background:var(--surface-2)}
.hb-row.click{cursor:pointer}
.hb-head{font-size:11px;color:var(--muted)}
.hb-label{font-size:12.5px;color:var(--ink-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hb-row.hl .hb-label{color:var(--ink);font-weight:700}
.hb-plot{position:relative;height:30px;display:flex;align-items:center}
.hb-head .hb-plot{height:18px}
.hb-bar{height:16px;border-radius:0 4px 4px 0;display:block}
.hb-bench{position:absolute;top:0;bottom:0;border-left:2px dashed var(--bench);opacity:.7}
.hb-bench-l{position:absolute;bottom:2px;transform:translateX(-50%);font-size:11px;color:var(--ink-2);font-weight:700;white-space:nowrap}
.hb-tick{position:absolute;top:6px;bottom:6px;width:3px;background:var(--bench);border-radius:2px;transform:translateX(-1.5px)}
.hb-val{font-size:12.5px;font-weight:700;text-align:right;white-space:nowrap}
.hb-extra{font-size:12px;white-space:nowrap;text-align:right}
.tag{display:inline-flex;align-items:center;height:18px;padding:0 6px;border-radius:5px;font-size:10.5px;font-weight:800;margin-left:6px;vertical-align:1px}
.tag.bad{background:var(--chip-bad);color:var(--bad-text)} .tag.good{background:var(--chip-blue);color:var(--good-text)} .tag.gray{background:var(--chip-gray);color:var(--ink-2)}
.segrows{display:flex;flex-direction:column;gap:10px}
.segrow{display:grid;grid-template-columns:52px minmax(0,1fr);gap:10px;align-items:center}
.segrow .lbl{font-size:12.5px;font-weight:700;color:var(--ink-2)}
.segbar{display:flex;gap:2px;height:30px}
.segbar>span{display:flex;align-items:center;padding:0 8px;font-size:12px;font-weight:700;white-space:nowrap;overflow:hidden;min-width:0}
.segbar>span:first-child{border-radius:4px 0 0 4px}.segbar>span:last-child{border-radius:0 4px 4px 0}
.segbar>span.nolabel{color:transparent!important}
.meter{position:relative;display:block;height:8px;border-radius:4px;background:var(--track);min-width:48px;width:100%;flex:none}
.mcell .meter{flex:1;width:auto}
.link svg{width:14px;height:14px}
.meter>i{position:absolute;left:0;top:0;bottom:0;background:var(--accent);border-radius:4px}
.meter.bad{background:var(--track-bad)} .meter.bad>i{background:#d03b3b}
.meter.ctx>i{background:var(--ctx)}
.meter>b{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--bench);border-radius:1px;transform:translateX(-1px)}
.mcell{display:flex;align-items:center;gap:8px;min-width:120px}
.mcell .v{min-width:38px;text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
.seg{display:flex;gap:2px;align-items:center;min-width:110px}
.seg>span{height:20px;display:flex;align-items:center;min-width:0}
.seg>span::before{content:"";display:block;width:100%;height:8px;background:var(--c)}
.seg>span:first-child::before{border-radius:4px 0 0 4px}.seg>span:last-child::before{border-radius:0 4px 4px 0}.seg>span:only-child::before{border-radius:4px}

/* ── 표 / 칩 / 배지 ── */
.tw{overflow-x:auto}
table.t{width:100%;border-collapse:collapse;font-size:12.5px}
.t th{font-weight:600;color:var(--muted);text-align:left;padding:8px;border-bottom:1px solid var(--grid);white-space:nowrap;font-size:11.5px;background:var(--surface);position:sticky;top:0;z-index:1}
.t td{padding:8px;border-bottom:1px solid var(--grid);white-space:nowrap}
.t .num{text-align:right}
.t tbody tr.click{cursor:pointer}
.t tbody tr.click:hover,.t tbody tr.click:focus-visible{background:var(--surface-2)}
.t tbody tr[aria-selected="true"]{background:var(--chip-blue)}
.t tfoot td{font-weight:700;border-bottom:none}
.t .sub2{display:block;font-size:11px;color:var(--muted);white-space:normal;max-width:260px}
.grade{display:inline-grid;place-items:center;min-width:24px;height:22px;padding:0 6px;border-radius:6px;font-weight:800;font-size:12px}
.grade.lg{height:40px;min-width:48px;font-size:21px;border-radius:9px}
.gmove{display:inline-flex;gap:4px;align-items:center}
.badge{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:999px;font-size:11.5px;font-weight:700;border:1px solid var(--border);color:var(--ink-2);white-space:nowrap}
.badge svg{width:12px;height:12px}
.badge.warn{background:var(--chip-warn);border-color:transparent;color:var(--warn-text)}
.badge.bad{background:var(--chip-bad);border-color:transparent;color:var(--bad-text)}
.badge.good{background:var(--chip-blue);border-color:transparent;color:var(--good-text)}
.badges{display:flex;gap:4px;flex-wrap:wrap}
.delta{font-variant-numeric:tabular-nums;font-weight:700;white-space:nowrap}
.delta.good{color:var(--good-text)}.delta.bad{color:var(--bad-text)}.delta.flat{color:var(--muted)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{height:30px;padding:0 12px;border-radius:999px;border:1px solid var(--border);background:var(--surface);cursor:pointer;font-weight:700;font-size:12.5px;display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.chip i{font-style:normal;font-weight:700;color:var(--muted);font-size:11.5px}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--surface);border-color:var(--ink)}
.chip[aria-pressed="true"] i{color:inherit;opacity:.75}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.search{display:flex;align-items:center;gap:8px;height:36px;border:1px solid var(--border);background:var(--surface-2);border-radius:9px;padding:0 10px;flex:1;min-width:200px;max-width:420px}
.search svg{width:16px;height:16px;color:var(--muted);flex:none}
.search input{border:0;background:transparent;outline:none;flex:1;min-width:0;height:100%}
.toolbar select{height:36px;border:1px solid var(--border);background:var(--surface-2);border-radius:9px;padding:0 10px}
.pager{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--muted)}
.seg-ctl{display:inline-flex;border:1px solid var(--border);border-radius:8px;padding:2px;gap:2px}

/* ── 협력사 상세 ── */
.co-head{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:18px;align-items:start}
.co-name{font-size:20px;font-weight:800;display:flex;gap:8px;align-items:center;flex-wrap:wrap;letter-spacing:-.01em}
.co-meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
.co-score{display:flex;gap:18px;align-items:flex-end;flex-wrap:wrap}
.hero{font-size:52px;font-weight:750;letter-spacing:-.03em;line-height:1;color:var(--ink)}
.hero small{font-size:16px;color:var(--ink-2);font-weight:600;margin-left:4px;letter-spacing:0}
.gbox{display:flex;flex-direction:column;gap:4px;font-size:11.5px;color:var(--muted);font-weight:700}
.gline{display:flex;align-items:center;gap:8px}
details.more{border-top:1px solid var(--grid);padding-top:10px}
details.more summary{cursor:pointer;font-size:12.5px;font-weight:700;color:var(--ink-2)}
.dl{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px 16px;margin:10px 0 0}
.dl dt{font-size:11px;color:var(--muted);font-weight:600}
.dl dd{margin:2px 0 0;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.flow{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.flow li{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:10px;align-items:center;padding:7px 0;position:relative}
.flow li:not(:last-child)::after{content:"";position:absolute;left:13px;top:36px;bottom:-8px;width:2px;background:var(--grid)}
.flow .no{width:28px;height:28px;border-radius:50%;background:var(--surface-2);border:1px solid var(--border);display:grid;place-items:center;font-size:12px;font-weight:800;color:var(--ink-2);position:relative;z-index:1}
.flow li.hl .no{background:var(--ink);color:var(--surface);border-color:var(--ink)}
.flow .tt{font-weight:700;font-size:13px}
.flow .ds{font-size:11.5px;color:var(--muted)}
.flow .rv{display:flex;align-items:center;gap:6px;font-weight:800;font-variant-numeric:tabular-nums}
.sub-list{display:flex;flex-direction:column;gap:8px}
.sub-item{border:1px solid var(--border);border-radius:10px;padding:10px 12px;display:grid;grid-template-columns:1fr auto;gap:2px 10px}
.sub-item .n{font-weight:700;font-size:13px}
.sub-item .v{font-weight:800;font-variant-numeric:tabular-nums;text-align:right}
.sub-item .m{font-size:11.5px;color:var(--muted);grid-column:1/-1}

/* ── 결과 보고 ── */
.rep-head{gap:14px}
.rep-title{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.rep-title h2{margin:0;font-size:20px;letter-spacing:-.01em}
.rep-meta{font-size:12.5px;color:var(--muted);margin-top:4px}
.rep-sum{margin:0;padding:12px 14px 12px 32px;border-radius:10px;background:var(--surface-2);display:grid;gap:6px;font-size:13.5px;color:var(--ink-2)}
.rep-sum b{color:var(--ink)}
.dchg{display:inline-grid;grid-template-columns:1fr 1fr;width:112px;height:16px;vertical-align:middle;margin-right:8px}
.dchg>span{display:flex;align-items:center}
.dchg>span:first-child{justify-content:flex-end;border-right:1px solid var(--axis)}
.dchg i{display:block;height:10px}
.dchg>span:first-child i{background:#d03b3b;border-radius:4px 0 0 4px}
.dchg>span:last-child i{background:var(--accent);border-radius:0 4px 4px 0}
.t tr.sub td{background:var(--surface-2);font-size:12px;color:var(--ink-2)}
.t tr.sub td:first-child{padding-left:26px}
.t tr.sub.hide{display:none}
.t tr.grp{cursor:pointer}
.t tr.grp td:first-child{font-weight:700}
.caret{display:inline-block;width:14px;color:var(--muted)}
.crit{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 12px;border-radius:10px;border:1px dashed var(--axis);font-size:12.5px;color:var(--ink-2)}
.crit .rule{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:999px;background:var(--surface-2);font-weight:700;color:var(--ink)}
.crit .rule i{font-style:normal;font-weight:700;color:var(--muted)}
.crit .op{font-weight:800;color:var(--muted)}
.statrow{display:flex;gap:20px;flex-wrap:wrap;align-items:baseline}
.kpis.k4{grid-template-columns:1.35fr repeat(3,minmax(0,1fr))}
.spark{display:inline-block;vertical-align:middle;overflow:visible}
.gtiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.gtile{background:var(--surface-2);border:1px solid transparent;border-radius:12px;padding:12px;text-align:left;cursor:pointer;display:flex;flex-direction:column;gap:6px;min-width:0}
.gtile:hover{border-color:var(--axis)}
.gtile[aria-pressed="true"]{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset;background:var(--key-bg)}
.gtile .nm{font-weight:800;font-size:13px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.gtile .v{font-size:20px;font-weight:750;line-height:1.1}
.gtile .st{font-size:11.5px;color:var(--muted)}
.detail-only{display:none!important}
body.show-detail .detail-only{display:flex!important}
.detail-tag{display:inline-flex;align-items:center;height:18px;padding:0 6px;border-radius:5px;font-size:10.5px;font-weight:800;background:var(--chip-blue);color:var(--good-text);margin-left:6px}
.rank{display:flex;align-items:center;gap:8px;min-width:150px}
.rank .r{font-weight:800;font-variant-numeric:tabular-nums;min-width:58px;text-align:right}
.rank .p{font-size:11.5px;color:var(--muted);min-width:52px}
.rank .meter{width:52px;min-width:52px;flex:none}
.sec-sub{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin:6px 2px -4px}
.sec-sub h2{margin:0;font-size:16px}
.sec-sub p{margin:0;font-size:12.5px;color:var(--muted)}
.subpanel{border-top:1px solid var(--grid);padding-top:12px;display:flex;flex-direction:column;gap:8px}
.statrow .big{font-size:28px;font-weight:750;letter-spacing:-.01em}
.statrow .big small{font-size:13px;font-weight:600;color:var(--ink-2);margin-left:3px}
@media print{
  @page{size:A4;margin:12mm}
  body{background:#fff}
  .sidebar,.topbar,.filters,.active-f,.no-print,.tools,.info,.card-f .btn,.card-f .link,#tooltip,.chat-root{display:none!important}
  .app{display:block;background:none;padding-right:0!important}.main{padding:0;gap:10px}
  .grid>*{grid-column:span 12!important}
  .tw{overflow:visible}
  .card,.kpi,.ins{box-shadow:none;break-inside:avoid}
  .t tr.sub.hide{display:table-row!important}
  .grid{gap:10px}
}

/* ── 툴팁 ── */
#tooltip{position:fixed;z-index:50;pointer-events:none;background:var(--surface);color:var(--ink);border:1px solid var(--border);border-radius:8px;box-shadow:0 8px 28px rgba(15,23,42,.18);padding:8px 10px;font-size:12px;min-width:120px;max-width:280px}
.tt-title{font-size:11.5px;color:var(--muted);margin-bottom:4px;font-weight:700}
.tt-row{display:flex;align-items:center;gap:8px;line-height:1.65}
.tt-row strong{font-variant-numeric:tabular-nums;font-size:13px}
.tt-key{width:12px;height:2px;border-radius:1px;flex:none}
.tt-label{color:var(--ink-2)}

/* ── AI 대화 패널 (오른쪽 · 화살표 손잡이) ── */
:root{--chat-w:380px;--chat-user:#1c5cab}
.sr-only{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.chat-handle{position:fixed;top:50%;right:0;transform:translateY(-50%);z-index:41;width:30px;height:92px;border:1px solid var(--border);border-right:0;border-radius:12px 0 0 12px;background:var(--surface);color:var(--ink-2);box-shadow:-4px 0 14px rgba(15,23,42,.10);cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:0;transition:right .22s ease,background .15s}
.chat-handle:hover{background:var(--surface-2)}
.chat-handle svg{width:16px;height:16px;flex:none}
.chat-handle .ch-ai{color:var(--accent)}
.chat-handle .chev{transition:transform .22s ease}
.chat-root[data-open="true"] .chat-handle{right:var(--chat-w)}
.chat-root[data-open="true"] .chat-handle .chev{transform:rotate(180deg)}
.chat-panel{position:fixed;top:0;right:0;bottom:0;width:var(--chat-w);max-width:100vw;z-index:40;background:var(--surface);color:var(--ink);border-left:1px solid var(--border);box-shadow:-10px 0 30px rgba(15,23,42,.12);display:flex;flex-direction:column;transform:translateX(100%);visibility:hidden;transition:transform .22s ease,visibility 0s linear .22s}
.chat-root[data-open="true"] .chat-panel{transform:none;visibility:visible;transition:transform .22s ease,visibility 0s}
.chat-h{display:flex;align-items:center;gap:6px;padding:12px 10px 12px 16px;border-bottom:1px solid var(--grid)}
.chat-h .ttl{display:flex;align-items:center;gap:10px;min-width:0;flex:1}
.chat-h .ttl>i{width:30px;height:30px;border-radius:10px;background:var(--chip-blue);color:var(--accent-ink);display:grid;place-items:center;flex:none}
.chat-h .ttl>i svg{width:17px;height:17px}
.chat-h .ttl>span{min-width:0}
#chat-status{flex:none}
.chat-h .ttl b{display:block;font-size:14.5px;line-height:1.25}
.chat-h .ttl small{display:block;font-size:11px;color:var(--muted);line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.icon-btn{width:30px;height:30px;border-radius:8px;border:1px solid transparent;background:none;color:var(--ink-2);display:grid;place-items:center;cursor:pointer;padding:0;flex:none}
.icon-btn:hover{background:var(--surface-2);border-color:var(--border)}
.icon-btn svg{width:16px;height:16px}
.chat-ctx{display:flex;align-items:center;gap:8px;padding:8px 16px;border-bottom:1px solid var(--grid);font-size:12px;color:var(--ink-2);min-width:0}
.chat-ctx .chip{height:26px;padding:0 10px;font-size:12px;flex:none}
.chat-ctx .txt{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chat-log{flex:1;min-height:0;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:14px}
.chat-empty{margin:auto 0;display:flex;flex-direction:column;gap:14px}
.chat-empty .hi{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;padding:6px 0}
.chat-empty .hi>i{width:46px;height:46px;border-radius:15px;background:var(--chip-blue);color:var(--accent-ink);display:grid;place-items:center;margin-bottom:4px}
.chat-empty .hi>i svg{width:24px;height:24px}
.chat-empty .hi b{font-size:16px}
.chat-empty .hi span{font-size:12.5px;color:var(--muted)}
.sugg{display:flex;flex-direction:column;gap:8px}
.sugg button{text-align:left;padding:10px 12px;border:1px solid var(--border);border-radius:10px;background:var(--surface);font-size:13px;font-weight:600;cursor:pointer;display:flex;gap:8px;align-items:center;line-height:1.35}
.sugg button:hover{background:var(--surface-2);border-color:var(--axis)}
.sugg button svg{width:14px;height:14px;color:var(--accent);flex:none}
.msg{display:flex;gap:8px;align-items:flex-start;min-width:0}
.msg.user{justify-content:flex-end}
.msg .av{width:26px;height:26px;border-radius:50%;background:var(--chip-blue);color:var(--accent-ink);display:grid;place-items:center;flex:none}
.msg .av svg{width:14px;height:14px}
.msg-col{display:flex;flex-direction:column;min-width:0;max-width:100%}
.msg.user .msg-col{align-items:flex-end;max-width:88%}
.msg.ai .msg-col{max-width:calc(100% - 34px)}
.bub{padding:9px 12px;border-radius:14px;font-size:13.5px;line-height:1.55;overflow-wrap:anywhere;min-width:0}
.msg.user .bub{background:var(--chat-user);color:#fff;border-bottom-right-radius:4px;white-space:pre-wrap}
.msg.ai .bub{background:var(--surface-2);border:1px solid var(--border);border-top-left-radius:4px}
.msg.ai .bub.err{background:var(--chip-bad);border-color:transparent}
.bub p{margin:0}
.bub p+p,.bub p+ul,.bub p+ol,.bub ul+p,.bub ol+p{margin-top:6px}
.bub ul,.bub ol{margin:0;padding-left:18px}
.bub li+li{margin-top:2px}
.bub code{font:12px/1.4 ui-monospace,Consolas,monospace;background:var(--chip-gray);padding:1px 5px;border-radius:4px}
.msg .meta{display:flex;gap:8px;align-items:center;font-size:11px;color:var(--muted);margin-top:4px;min-height:20px}
.msg .meta .link{font-size:11px;font-weight:600;color:var(--muted)}
.msg .meta .link:hover{color:var(--accent-ink)}
.msg .meta .badge{height:18px;font-size:10.5px;padding:0 6px}
.dots{display:inline-flex;gap:4px;align-items:center;height:18px}
.dots i{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:chatdot 1.1s infinite ease-in-out}
.dots i:nth-child(2){animation-delay:.15s}
.dots i:nth-child(3){animation-delay:.3s}
@keyframes chatdot{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}
.chat-f{padding:10px 14px 12px;border-top:1px solid var(--grid);display:flex;flex-direction:column;gap:6px}
.chat-box{display:flex;gap:8px;align-items:flex-end;border:1px solid var(--border);background:var(--surface-2);border-radius:12px;padding:6px 6px 6px 12px}
.chat-box:focus-within{border-color:var(--accent);box-shadow:0 0 0 2px var(--chip-blue)}
.chat-box textarea{flex:1;resize:none;border:0;background:transparent;outline:none;font:inherit;color:inherit;line-height:1.5;min-height:24px;max-height:120px;padding:5px 0;min-width:0}
.chat-send{width:34px;height:34px;border-radius:9px;border:0;background:var(--accent);color:#fff;display:grid;place-items:center;cursor:pointer;flex:none;padding:0}
.chat-send svg{width:16px;height:16px}
.chat-send:disabled{background:var(--chip-gray);color:var(--muted);cursor:not-allowed}
.chat-note{font-size:11px;color:var(--muted);text-align:center}
/* 넓은 화면(1480px 이상)에서는 패널이 본문을 옆으로 밀고, 그보다 좁으면 본문 위에 겹쳐서 열림 */
@media (min-width:1480px){
  .app{transition:padding-right .22s ease}
  .app.chat-open{padding-right:var(--chat-w)}
}
/* 패널이 본문 폭을 줄인 만큼 반응형 기준을 함께 올림 (1320+380, 1180+380) */
@media (min-width:1480px) and (max-width:1699px){
  .app.chat-open .kpis,.app.chat-open .kpis.k4{grid-template-columns:repeat(3,minmax(0,1fr))}
  .app.chat-open .kpis .kpi.key{grid-column:span 3}
  .app.chat-open .atiles{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media (min-width:1480px) and (max-width:1559px){
  .app.chat-open .span-3,.app.chat-open .span-4,.app.chat-open .span-5{grid-column:span 6}
  .app.chat-open .span-6,.app.chat-open .span-7,.app.chat-open .span-8{grid-column:span 12}
  .app.chat-open .co-head{grid-template-columns:1fr}
  .app.chat-open .dl{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media (max-width:760px){
  .chat-panel{width:100vw}
  .chat-handle{top:auto;bottom:16px;right:16px;transform:none;width:48px;height:48px;border:0;border-radius:50%;background:var(--accent);color:#fff;box-shadow:0 6px 18px rgba(15,23,42,.28);flex-direction:row;gap:0}
  .chat-handle .ch-ai{color:#fff;width:22px;height:22px}
  .chat-handle .chev{display:none}
  .chat-root[data-open="true"] .chat-handle{display:none}
}
@media (prefers-reduced-motion:reduce){
  .chat-panel,.chat-handle,.chat-handle .chev,.app{transition:none!important}
  .dots i{animation:none;opacity:.6}
}

/* ── 반응형 ── */
@media (max-width:1320px){.kpis,.kpis.k4{grid-template-columns:repeat(3,minmax(0,1fr))}.kpis .kpi.key{grid-column:span 3}.atiles{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:1180px){.span-3,.span-4,.span-5{grid-column:span 6}.span-6,.span-7,.span-8{grid-column:span 12}.co-head{grid-template-columns:1fr}.dl{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:1024px){
  .app{grid-template-columns:1fr;background:none}
  .sidebar{height:auto;flex-direction:row;align-items:center;padding:10px 16px;gap:14px;z-index:20}
  .nav{flex-direction:row}.nav a small{display:none}
  .side-foot,.brand-s{display:none}
  .main{padding:16px}
}
@media (max-width:760px){
  .grid>*{grid-column:span 12}
  .kpis,.kpis.k4,.atiles{grid-template-columns:repeat(2,minmax(0,1fr))}.kpis .kpi.key{grid-column:span 2}
  .dl{grid-template-columns:repeat(2,minmax(0,1fr))}
  .brand{display:none}
  .nav a{padding:8px 10px;font-size:13px}
  .f{flex:1 1 calc(50% - 5px);min-width:0}
  .topbar h1{font-size:20px}
  .bigtrio .v{font-size:19px}
  .hero{font-size:48px}
}
@media (max-width:420px){.nav svg{display:none}}
```

---

## 부록 B. HTML 뼈대 (`src/index.html` 그대로)

- `AI 대화 패널`(`#chat-root`)은 `.app` 밖, 툴팁 다음에 있습니다(본문 §9.5).
- 아래 `<body>` 안의 `<script>`는 **데이터(`data.js`)와 앱(`app.js`)** 두 개입니다. 목업은 이 둘을 한 파일에 넣었습니다.
- 화면 안의 고정 값(`2026년 협력사 종합평가`, `2026년 평가`, `최종 갱신 …`, `데이터: …`)은 데이터에서 채웁니다.
- 필터 `select`의 `option`(전체 + 값 목록)은 스크립트가 채웁니다.

```html
<!doctype html>
<html lang="ko" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>협력사 종합평가</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 20V12M10 20V6M15 20v-9M20 20V4"/></svg></div>
      <div><div class="brand-t">협력사<br>종합평가</div><div class="brand-s">Supplier Evaluation</div></div>
    </div>
    <nav class="nav" aria-label="화면">
      <a href="#report" data-page="report"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></svg><span>결과 요약<small>핵심 결과 · 5개년 · 인쇄</small></span></a>
      <a href="#area" data-page="area"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 5v8l-8 5-8-5V8z"/><path d="M12 8l4 2.5v3L12 16l-4-2.5v-3z"/></svg><span>항목별 결과<small>영역 · 평가항목 · 추이</small></span></a>
      <a href="#company" data-page="company"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V8l6-4v17M10 21h10V10l-6-2"/><path d="M14 13h2M14 17h2M6.5 11h1M6.5 15h1"/></svg><span>협력사별 결과<small>목록 · 항목 순위 · 추이</small></span></a>
    </nav>
    <div class="side-foot">
      <span>최종 갱신 2026-11-09 10:30</span>
      <span>데이터: 가상 샘플 (목업)</span>
    </div>
  </aside>

  <main class="main">
    <header class="topbar">
      <div>
        <p class="eyebrow">2026년 협력사 종합평가</p>
        <h1 id="page-title">결과 요약</h1>
        <p class="lead" id="page-lead"></p>
      </div>
      <div class="top-actions">
        <button class="btn" id="detail-btn" type="button" aria-pressed="false" title="세부 표·목록을 함께 펼쳐 봅니다">상세 보기</button>
        <button class="btn" id="theme-btn" type="button" aria-pressed="false">다크 모드</button>
      </div>
    </header>

    <section class="filters" aria-label="필터 (모든 화면에 적용)">
      <div class="f"><label for="f-year">평가 연도</label><select id="f-year"><option>2026년 평가</option></select></div>
      <div class="f"><label for="f-org">평가조직</label><select id="f-org"></select></div>
      <div class="f"><label for="f-region">권역명</label><select id="f-region"></select></div>
      <div class="f"><label for="f-inout">내/외자</label><select id="f-inout"></select></div>
      <div class="f"><label for="f-unit">평가단위</label><select id="f-unit"></select></div>
      <div class="f"><label for="f-group">세부업종그룹</label><select id="f-group"></select></div>
      <div class="f"><label for="f-grade">D/T 최종 등급</label><select id="f-grade"></select></div>
    </section>
    <div class="active-f" id="active-f" aria-live="polite"></div>

    <div class="empty" id="empty" hidden>조건에 맞는 협력사가 없습니다. 필터를 조정해 주세요.</div>
    <section class="page" id="page-report" hidden></section>
    <section class="page" id="page-area" hidden></section>
    <section class="page" id="page-company" hidden></section>
  </main>
</div>
<div id="tooltip" role="tooltip" hidden></div>

<div class="chat-root" id="chat-root" data-open="false">
  <button class="chat-handle" id="chat-handle" type="button" aria-controls="chat-panel" aria-expanded="false" aria-label="AI 대화 열기" title="AI 대화">
    <svg class="ch-ai" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>
    <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>
  </button>
  <aside class="chat-panel" id="chat-panel" role="complementary" aria-label="AI 대화" aria-hidden="true">
    <header class="chat-h">
      <div class="ttl">
        <i aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg></i>
        <span><b id="chat-name">AI 어시스턴트</b><small>현재 화면 기준으로 질문해요</small></span>
      </div>
      <span class="badge warn" id="chat-status">API 미연결</span>
      <button class="icon-btn" id="chat-new" type="button" aria-label="새 대화" title="새 대화"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button>
      <button class="icon-btn" id="chat-close" type="button" aria-label="AI 대화 닫기" title="닫기"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></button>
    </header>
    <div class="chat-ctx" id="chat-ctx"></div>
    <div class="chat-log" id="chat-log"></div>
    <div class="sr-only" id="chat-live" role="status" aria-live="polite"></div>
    <footer class="chat-f">
      <form class="chat-box" id="chat-form" autocomplete="off">
        <textarea id="chat-input" rows="1" placeholder="질문을 입력하세요 · Enter로 전송" title="Enter: 전송 · Shift+Enter: 줄바꿈" aria-label="질문 입력"></textarea>
        <button class="chat-send" id="chat-send" type="submit" aria-label="보내기" disabled><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg></button>
      </form>
      <div class="chat-note">AI 답변은 부정확할 수 있습니다. 중요한 수치는 화면에서 확인하세요.</div>
    </footer>
  </aside>
</div>

<script src="data.js"></script>   <!-- window.__SUPPLIER_DATA__ (샘플 모드에서는 없어도 됨) -->
<script src="app.js"></script>
</body>
</html>
```

---

## 부록 C. 설정 · 엑셀 컬럼 매핑 (목업 기준)

`CONFIG`는 목업의 값입니다(등급 구간 확정, 나머지 임시). 실제 구현에서는 본문 §11의 `settings.js`로 옮깁니다. `COLUMNS`는 **엑셀 컬럼 이름 ↔ 모델 필드** 기본 매핑입니다(동의어는 `settings.columns`에 추가).

```js
/* =====================================================================
   1. 설정 — 사내 기준값으로 교체 (등급 구간 · 영역명/배점 · 목표 · 코드 목록)
   ===================================================================== */
const GRADE_CUT = { A: 90, B: 80, C: 60 };               // ★ 확정: 90점 이상 A, 80점 이상 B, 60점 이상 C, 60점 미만 D
const CONFIG = {
  year: 2026, prevYear: 2025,
  grades: ['A','B','C','D'],                             // 높은 등급 → 낮은 등급
  gradeCut: GRADE_CUT,                                   // 점수 이상(≥), 그 외 D
  gradeGroup: { A:'우수', B:'양호', C:'개선 필요', D:'부진' },   // 등급 이름표 ※ 임시 (사내 용어로 교체)
  areas: [                                                // 2번 파일 영역(T~A). 영역명은 TQRDC 관례로 둔 예시 ※ 사내 명칭으로 교체
    { code:'T', name:'기술', max:15 }, { code:'Q', name:'품질', max:25 }, { code:'R', name:'대응', max:10 }, { code:'D', name:'납기', max:15 },
    { code:'C', name:'원가', max:15 }, { code:'E', name:'환경', max:5 },  { code:'F', name:'재무', max:10 }, { code:'A', name:'기타', max:5 },
  ],
  targets: { avgScore: 85 },                            // 목표·기준선 ※ 예시 (평균 점수 목표)
  /* 부진사 · 우수사 후보 기준 — ※ 임시 기준. 확정 기준을 받으면 rules만 교체 (mode: any = 하나라도 해당, all = 모두 해당) */
  criteria: {
    poor: { name:'부진사', fixed:false, mode:'any', rules: [
      { label:`D등급 (${GRADE_CUT.C}점 미만)`, test: x => x.grade === 'D' },
      { label:'전년 대비 2단계 이상 하락', test: x => x.move <= -2 },
    ] },
    excellent: { name:'우수사 후보', fixed:false, mode:'all', rules: [
      { label:`A등급 (${GRADE_CUT.A}점 이상)`, test: x => x.grade === 'A' },
      { label:'전년 대비 등급 하락 없음', test: x => x.move >= 0 },
      { label:'등급 조정·거래중단 예정 아님', test: x => !x.adjTarget && !x.stopPlan },
    ] },
  },
  orgs: ['A사업부','B사업부','C사업부','D사업부','E사업부'],
  regions: [ {code:'R1',name:'수도권'}, {code:'R2',name:'충청권'}, {code:'R3',name:'영남권'}, {code:'R4',name:'호남권'}, {code:'R5',name:'해외'} ],
  units: ['평가단위 A','평가단위 B','평가단위 C'],
  groups: ['전장','기계가공','사출','프레스','소재','기타'],
  bonusMax: 3,
};

/* 엑셀 컬럼 ↔ 화면 필드 매핑 (opencode 구현 시 이 표 기준으로 파싱)
   1번은 2단 헤더: [평가결과] / [전년도 결과] 그룹으로 같은 이름의 컬럼을 구분 */
const COLUMNS = {
  '1_평가결과': {
    dt:'D/T 코드', code:'협력사 코드', name:'협력사명', confirmed:'협력사 확인', org:'평가조직', regionCode:'권역 코드', region:'권역명',
    inout:'내/외자', unit:'평가단위', subUnitCode:'세부 평가단위 코드', subUnit:'세부 평가단위명', group:'세부업종그룹',
    max:'[평가결과] 배점', genRaw:'[평가결과] 일반항목 평점', gen:'[평가결과] 일반항목 환산점수', bonus:'[평가결과] 가산점',
    score:'[평가결과] 평가 점수', change:'[평가결과] 점수 변동', dtScore:'[평가결과] D/T 종합 점수', grade:'[평가결과] D/T 최종 등급',
    'prev.max':'[전년도 결과] 배점', 'prev.genRaw':'[전년도 결과] 일반항목 평점', 'prev.gen':'[전년도 결과] 일반항목 환산점수',
    'prev.bonus':'[전년도 결과] 가산점', 'prev.score':'[전년도 결과] 평가 점수', 'prev.dtScore':'[전년도 결과] D/T 종합 점수', 'prev.grade':'[전년도 결과] D/T 최종 등급',
  },
  '2_GT상세': {
    generalOrg:'일반 조직', org:'평가조직', gt:'G/T 코드', dt:'D/T 코드', code:'협력사 코드', name:'협력사명', regionCode:'권역 코드', region:'권역명',
    country:'국가', inout:'내/외자', industry:'업종', subUnitCode:'세부 평가단위 코드', subUnit:'세부 평가단위명', main:'주거래', rep:'대표코드',
    size:'기업 규모', mold:'금형', stopPlan:'거래중단예정일', stopDate:'거래중단일',
    max:'배점', genRaw:'일반항목 평점', gen:'일반항목 환산점수', bonus:'가산점', score:'평가 점수', orgGrade:'평가조직 등급',
    dtScore:'D/T 종합 점수', weight:'D/T 등급 반영비중-거래비중', weighted:'D/T 거래비중별 개별합계', weightedSum:'D/T 거래비중별 총합계',
    preGrade:'D/T 조정 전 등급', adjTarget:'등급 조정 대상', grade:'D/T 최종 등급', prevGrade:'D/T 전년도 등급',
    gtScore:'G/T 종합 점수', gtGrade:'G/T 등급', gtWeight:'G/T 등급 반영비중-거래비중',
    area:'{영역}-배점, {영역}-평점, {영역}-환산점수, {영역}-배점(비중), {영역}-평점(비중)  (영역 = T,Q,R,D,C,E,F,A)',
  },
  '3_평가항목': {
    dt:'D/T 코드', code:'협력사 코드', name:'협력사명', org:'평가조직', unit:'평가단위', subUnitCode:'세부 평가단위 코드', subUnit:'세부 평가단위명',
    classType:'분류체계 유형', classCode:'분류체계', itemCode:'평가항목 코드', itemName:'평가항목명',
    max:'배점', raw:'평점', conv:'환산평점', convChange:'환산평점 변동', prevConv:'이전 환산평점', na:'미적용 여부', np:'무실적 여부',
  },
  '4_세부항목': {
    dt:'D/T 코드', code:'협력사 코드', name:'협력사명', org:'평가조직', unit:'평가단위', subUnitCode:'세부 평가단위 코드', subUnit:'세부 평가단위명',
    itemCode:'평가항목 코드', itemName:'평가항목명', owner:'세부 등록 주체', max:'배점', raw:'평점', conv:'환산 평점',
    subCode:'세부항목 코드', subName:'세부항목명', subValue:'세부항목 값',
  },
};
```

---

## 부록 D. 공통 참조 코드 (유틸 · 포맷 · 툴팁 · 카드 · 차트 · 상태 · 라우팅)

섹션 3(유틸·팔레트·툴팁·카드·표·칩·CSV) · 섹션 4(차트) · 섹션 5(상태·필터·목록 정의) · 섹션 6(공통 부품) · 섹션 10(**AI 대화 패널**) · 섹션 11(화면 전환·필터·테마·초기화)입니다. **차트 수치(여백, 선 굵기, 글자 크기)와 포맷 함수는 이 코드가 기준**입니다.

```js
/* =====================================================================
   3. 공통 유틸 · 색 · 툴팁 · 카드 · 칩 · CSV
   ===================================================================== */
const $ = (q, r = document) => r.querySelector(q);
const NS = 'http://www.w3.org/2000/svg';
function setAttrs(e, a) {
  if (!a) return;
  for (const [k, v] of Object.entries(a)) {
    if (v == null || v === false) continue;
    if (k === 'style') e.style.cssText = v;
    else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? '' : v);
  }
}
function addKids(e, kids) { for (const k of kids.flat(Infinity)) { if (k == null || k === false) continue; e.append(k instanceof Node ? k : document.createTextNode(String(k))); } }
function h(tag, attrs, ...kids) { const e = document.createElement(tag); setAttrs(e, attrs); addKids(e, kids); return e; }
function s(tag, attrs, ...kids) { const e = document.createElementNS(NS, tag); setAttrs(e, attrs); addKids(e, kids); return e; }
/* 숫자는 단순하게: 점수 소수 1자리, 비율 정수(10% 미만만 소수 1자리), 건수 천 단위 */
const fmt = {
  n: v => Math.round(v).toLocaleString('ko-KR'),
  sc: v => (Math.round(v * 10) / 10).toFixed(1),
  pct: v => { const r = Math.round(v * 10) / 10; return (Math.abs(r) < 10 && !Number.isInteger(r) ? r.toFixed(1) : String(Math.round(r))) + '%'; },
  sgn: (v, d = 1) => { const r = Math.round(v * 10 ** d) / 10 ** d; return (r > 0 ? '+' : r < 0 ? '−' : '±') + Math.abs(r).toFixed(d); },
};
const avg = (arr, f) => arr.length ? arr.reduce((a, x) => a + f(x), 0) / arr.length : 0;
const sum = (arr, f) => arr.reduce((a, x) => a + f(x), 0);
const countBy = (arr, f) => arr.reduce((m, x) => { const k = f(x); m[k] = (m[k] || 0) + 1; return m; }, {});
const pctOf = (n, d) => d ? n / d * 100 : 0;

/* 색은 의미가 있을 때만: 파랑 = 좋음/강조, 빨강 = 나쁨/문제, 회색 = 맥락. 등급은 A(진한 파랑) – B(연한 파랑) – C(연한 빨강) – D(진한 빨강) 발산 척도 (dataviz 검증 통과) */
const PALETTE = {
  light: {
    surface:'#ffffff', grid:'#e6eaf0', axis:'#c5cdd8', muted:'#64748b', ink:'#0f172a', ink2:'#475569', bench:'#475569',
    accent:'#2a78d6', ctx:'#b4bcc8', bad:'#d03b3b', prev:'#8b95a5',
    grade: { A:'#1c5cab', B:'#5598e7', C:'#ef8f8c', D:'#c93434' },
  },
  dark: {
    surface:'#161a22', grid:'#262c38', axis:'#3a4252', muted:'#8d97a8', ink:'#eef1f6', ink2:'#c3cad6', bench:'#c3cad6',
    accent:'#3987e5', ctx:'#4a5361', bad:'#e05252', prev:'#7d8797',
    grade: { A:'#9ec5f4', B:'#2a78d6', C:'#a64444', D:'#f07373' },
  },
};
let P = PALETTE.light;
function lum(hex) { const c = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255).map(v => v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
const inkOn = fill => lum(fill) > 0.36 ? '#0b0b0b' : '#ffffff';     // 채움 위 글자: 밝기 기준 흰/검정
const gradeColor = g => P.grade[g];

const tipEl = $('#tooltip');
function showTip(x, y, title, rows) {
  tipEl.replaceChildren();
  if (title) tipEl.append(h('div', { class:'tt-title' }, title));
  for (const r of rows) tipEl.append(h('div', { class:'tt-row' }, r.color ? h('span', { class:'tt-key', style:`background:${r.color}` }) : null, h('strong', null, r.value), r.label ? h('span', { class:'tt-label' }, r.label) : null));
  tipEl.hidden = false;
  const b = tipEl.getBoundingClientRect();
  let L = x + 14, T = y + 14;
  if (L + b.width > innerWidth - 8) L = x - b.width - 14;
  if (T + b.height > innerHeight - 8) T = y - b.height - 14;
  tipEl.style.left = Math.max(8, L) + 'px'; tipEl.style.top = Math.max(8, T) + 'px';
}
const hideTip = () => { tipEl.hidden = true; };
/* 마크마다 hover + 키보드 focus 툴팁 (툴팁 값은 표 보기·직접 라벨로도 확인 가능) */
function bindTip(el, fn, focusable = true) {
  if (focusable) el.setAttribute('tabindex', '0');
  const t0 = fn();
  el.setAttribute('aria-label', [t0.title, ...t0.rows.map(r => `${r.label || ''} ${r.value}`)].filter(Boolean).join(', '));
  const show = (x, y) => { const t = fn(); showTip(x, y, t.title, t.rows); };
  el.addEventListener('pointermove', e => show(e.clientX, e.clientY));
  el.addEventListener('pointerleave', hideTip);
  el.addEventListener('focus', () => { const r = el.getBoundingClientRect(); show(r.left + Math.min(r.width / 2, 40), r.top); });
  el.addEventListener('blur', hideTip);
}
function delta(v, unit = '', { goodUp = true, digits = 1, suffix = '' } = {}) {
  const r = Math.round(v * 10 ** digits) / 10 ** digits;
  const cls = r === 0 ? 'flat' : ((r > 0) === goodUp ? 'good' : 'bad');
  const sym = r > 0 ? '▲' : r < 0 ? '▼' : '–';
  return h('span', { class:'delta ' + cls }, `${sym} ${Math.abs(r).toFixed(digits)}${unit}`, suffix ? h('span', { class:'muted', style:'font-weight:500' }, ' ' + suffix) : null);
}
const gradeChip = (g, lg) => { const f = gradeColor(g); return h('span', { class:'grade' + (lg ? ' lg' : ''), style:`background:${f};color:${inkOn(f)}`, title:`${g}등급 (${CONFIG.gradeGroup[g]})` }, g); };
const gmove = (a, b) => h('span', { class:'gmove' }, gradeChip(a), h('span', { class:'muted' }, '→'), gradeChip(b));
const ICON = {
  warn:'<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>', up:'<path d="M12 19V5M5 12l7-7 7 7"/>', down:'<path d="M12 5v14M5 12l7 7 7-7"/>',
  users:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0M16 4.5a3.5 3.5 0 010 7M21.5 20a6.5 6.5 0 00-4-6"/>',
  gauge:'<path d="M4 18a8 8 0 1116 0"/><path d="M12 18l4-6"/>', star:'<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/>',
  adjust:'<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
  info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>', stop:'<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
  arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>', download:'<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>', search:'<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>', trend:'<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>',
  bulb:'<path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.4 1 1.1 1 1.8V17h5v-1.3c0-.7.4-1.4 1-1.8A6 6 0 0012 3z"/>',
  sparkle:'<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  copy:'<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 012-2h9"/>', chat:'<path d="M21 12a8 8 0 01-11.6 7.1L4 20l1-4.6A8 8 0 1121 12z"/>',
};
const icon = name => { const e = s('svg', { viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':2, 'stroke-linecap':'round', 'stroke-linejoin':'round', 'aria-hidden':'true' }); e.innerHTML = ICON[name]; return e; };
const badge = (text, kind, ic) => h('span', { class:'badge' + (kind ? ' ' + kind : '') }, ic ? icon(ic) : null, text);
const link = (text, onclick) => h('button', { class:'link', type:'button', onclick }, text, icon('arrow'));
const callout = (kind, ic, kids, action) => h('div', { class:'callout ' + kind }, icon(ic), h('span', null, kids), action || null);
function meter(f, { tone = '', tick = null, label = '' } = {}) {
  const m = h('span', { class:'meter ' + tone, role:'img', 'aria-label': label || null }, h('i', { style:`width:${(clamp(f, 0, 1) * 100).toFixed(1)}%` }));
  if (tick != null) m.append(h('b', { style:`left:${(clamp(tick, 0, 1) * 100).toFixed(1)}%` }));
  return m;
}
const mcell = (f, text, opt) => h('span', { class:'mcell' }, meter(f, opt), h('span', { class:'v' }, text));
function segBar(parts, unit = '개사') {      // 얇은 분할 막대 (표 안 등급 구성)
  const total = sum(parts, p => p.value);
  const el = h('div', { class:'seg' });
  parts.filter(p => p.value > 0).forEach(p => {
    const sp = h('span', { style:`flex:${p.value} 1 0;--c:${p.color}` });
    bindTip(sp, () => ({ title: p.label, rows: [{ value:`${fmt.n(p.value)}${unit}`, label: fmt.pct(pctOf(p.value, total)), color: p.color }] }));
    el.append(sp);
  });
  return el;
}
const gradeParts = counts => CONFIG.grades.map(g => ({ label:`${g}등급`, value: counts[g] || 0, color: gradeColor(g) }));

/* 카드: 제목 · 설명 · (i)사용 항목 · 표 보기 · 본문 · 하단 행동 */
const TABLES = {};
function card(id, span, title, sub, { table, src, tools, detail } = {}) {
  const tv = table ? h('button', { class:'btn sm', type:'button', 'aria-pressed':'false', onclick: e => toggleTable(id, e.currentTarget) }, '표') : null;
  const info = src ? h('button', { class:'info', type:'button' }, 'i') : null;
  if (info) bindTip(info, () => ({ title:'사용 항목 (엑셀 컬럼)', rows: [{ value: src }] }), false);
  return h('article', { class:`card span-${span}` + (detail ? ' detail-only' : ''), id },
    h('header', { class:'card-h' }, h('div', null, h('h3', null, title, info), sub ? h('p', { class:'sub' }, sub) : null), h('div', { class:'tools' }, tools || null, tv)),
    h('div', { class:'legend' }),
    h('div', { class:'chart-view' }),
    table ? h('div', { class:'tbl-view tw' }) : null,
    h('div', { class:'card-f', hidden: true }));
}
const body = id => $(`#${id} .chart-view`);
const foot = (id, ...kids) => { const f = $(`#${id} .card-f`); f.replaceChildren(...kids.flat().filter(Boolean)); f.hidden = !f.childNodes.length; };
function legend(id, items) { $(`#${id} .legend`).replaceChildren(...items.map(it => h('span', { class:'lg' }, h('span', { class:'lg-' + (it.type || 'rect'), style: it.color ? `background:${it.color}` : null }), it.label))); }
function toggleTable(id, btn) {
  const c = document.getElementById(id), on = !c.classList.contains('show-table');
  c.classList.toggle('show-table', on); btn.setAttribute('aria-pressed', String(on)); btn.textContent = on ? '차트' : '표';
  if (on) renderTableView(id); else renderAll();
}
function setTable(id, cols, rows) { TABLES[id] = { cols, rows }; if (document.getElementById(id)?.classList.contains('show-table')) renderTableView(id); }
function renderTableView(id) { const t = TABLES[id], box = $(`#${id} .tbl-view`); if (t && box) box.replaceChildren(simpleTable(t.cols, t.rows)); }
function simpleTable(cols, rows, { onRow, footer, selected } = {}) {   // cols: [{label, num}]
  const tr = (r, i) => {
    const row = h('tr', onRow ? { class:'click', tabindex:'0', 'aria-selected': selected === i ? 'true' : null } : null, r.map((v, k) => h('td', { class: cols[k].num ? 'num' : null }, v)));
    if (onRow) { row.addEventListener('click', () => onRow(i)); row.addEventListener('keydown', e => { if (e.key === 'Enter') onRow(i); }); }
    return row;
  };
  return h('table', { class:'t' },
    h('thead', null, h('tr', null, cols.map(c => h('th', { class: c.num ? 'num' : null }, c.label)))),
    h('tbody', null, rows.map(tr)),
    footer ? h('tfoot', null, h('tr', null, footer.map((v, k) => h('td', { class: cols[k].num ? 'num' : null }, v)))) : null);
}
function chipGroup(opts, cur, onPick, label) {
  return h('div', { class:'chips', role:'group', 'aria-label': label }, opts.map(o => h('button', { class:'chip', type:'button', 'aria-pressed': String(o.v === cur), onclick: () => onPick(o.v) }, o.label, o.n != null ? h('i', null, fmt.n(o.n)) : null)));
}
function pager(total, page, size, onPage) {
  const pages = Math.max(1, Math.ceil(total / size));
  return h('div', { class:'pager' }, `${fmt.n(total)}개사 중 ${fmt.n(total ? (page - 1) * size + 1 : 0)}–${fmt.n(Math.min(total, page * size))}`,
    h('button', { class:'btn sm', type:'button', disabled: page <= 1 || null, onclick: () => onPage(page - 1), 'aria-label':'이전 페이지' }, '‹'),
    h('span', { class:'tn' }, `${page} / ${pages}`),
    h('button', { class:'btn sm', type:'button', disabled: page >= pages || null, onclick: () => onPage(page + 1), 'aria-label':'다음 페이지' }, '›'));
}
function downloadCSV(name, header, rows) {           // 엑셀에서 한글이 깨지지 않도록 BOM 포함
  const esc = v => { const t = String(v ?? ''); return /[",\n]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t; };
  const csv = '﻿' + [header, ...rows].map(r => r.map(esc).join(',')).join('\r\n');
  const a = h('a', { href: URL.createObjectURL(new Blob([csv], { type:'text/csv;charset=utf-8' })), download: name });
  document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
}

/* =====================================================================
   4. 차트 부품 (순수 SVG/HTML — 사내 차트 라이브러리로 교체 가능)
   규칙: 기본 회색 + 의미 있는 막대만 색 · 점선 = 기준선(목표/평균) · 값은 막대 끝에 직접 표기
   ===================================================================== */
function niceMax(v) { if (v <= 0) return 1; const p = 10 ** Math.floor(Math.log10(v)), n = v / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p; }
const roundTop = (x, y, w, hh, r) => { if (hh <= 0) return ''; r = Math.min(r, hh, w / 2); return `M${x} ${y + hh}V${y + r}Q${x} ${y} ${x + r} ${y}H${x + w - r}Q${x + w} ${y} ${x + w} ${y + r}V${y + hh}Z`; };
const tnum = 'font-variant-numeric:tabular-nums';
const width = (box, min) => Math.max(box.clientWidth || 0, min);
const text = (x, y, t, o = {}) => s('text', { x, y, 'font-size': o.size || 11, fill: o.fill || P.muted, 'text-anchor': o.anchor || 'start', 'font-weight': o.weight || null, style: o.num ? tnum : null }, t);

/* 가로 막대 목록 — rows: [{key,label,value,tone:'bad'|'key',tag,tagKind,tick,extra,tip}] */
function hbars(box, rows, { max = 100, min = 0, bench, fmtV = fmt.sc, lw = 96, vw = 52, ew = 0, onClick, tipLabel = '' } = {}) {
  box.replaceChildren();
  const x = v => clamp((v - min) / (max - min), 0, 1) * 100;
  const wrap = h('div', { class:'hb', style:`--lw:${lw}px;--vw:${vw}px;--ew:${ew}px` });
  if (bench) wrap.append(h('div', { class:'hb-row hb-head' }, h('span'), h('span', { class:'hb-plot' }, h('span', { class:'hb-bench-l', style:`left:${x(bench.value)}%` }, bench.label)), h('span'), h('span')));
  for (const r of rows) {
    const color = r.tone === 'bad' ? P.bad : r.tone === 'key' ? P.accent : P.ctx;
    const plot = h('span', { class:'hb-plot' }, h('span', { class:'hb-bar', style:`width:${x(r.value)}%;background:${color}` }));
    if (bench) plot.append(h('span', { class:'hb-bench' , style:`left:${x(bench.value)}%` }));
    if (r.tick != null) plot.append(h('span', { class:'hb-tick', style:`left:${x(r.tick)}%` }));
    const row = h('div', { class:'hb-row' + (r.tone ? ' hl' : '') + (onClick ? ' click' : '') },
      h('span', { class:'hb-label', title: r.label }, r.label, r.tag ? h('span', { class:'tag ' + (r.tagKind || 'bad') }, r.tag) : null),
      plot, h('span', { class:'hb-val tn' }, fmtV(r.value)), h('span', { class:'hb-extra' }, r.extra ?? ''));
    bindTip(row, () => ({ title: r.label, rows: [{ value: fmtV(r.value), label: tipLabel, color }, ...(r.tick != null ? [{ value: fmtV(r.tick), label: r.tickLabel || '비교값', color: P.bench }] : []), ...(bench ? [{ value: fmtV(bench.value), label: bench.label.replace(/\s[\d.]+$/, ''), color: P.bench }] : []), ...(r.tip || [])] }));
    if (onClick) { row.addEventListener('click', () => onClick(r)); row.addEventListener('keydown', e => { if (e.key === 'Enter') onClick(r); }); }
    wrap.append(row);
  }
  box.append(wrap);
}

/* 굵은 분할 막대 (등급 구성 — 전체를 한눈에, 칸에 비율 표기) */
function segRows(box, rows) {
  box.replaceChildren();
  const wrap = h('div', { class:'segrows' }), segs = [];
  for (const r of rows) {
    const bar = h('div', { class:'segbar', role:'img', 'aria-label': `${r.label} 등급 구성 ` + CONFIG.grades.map(g => `${g} ${fmt.pct(pctOf(r.counts[g] || 0, r.total))}`).join(', ') });
    for (const g of CONFIG.grades) {
      const v = r.counts[g] || 0; if (!v) continue;
      const f = gradeColor(g), sp = h('span', { style:`flex:${v} 1 0;background:${f};color:${inkOn(f)}` }, `${g} ${fmt.pct(pctOf(v, r.total))}`);
      bindTip(sp, () => ({ title:`${r.label} · ${g}등급 (${CONFIG.gradeGroup[g]})`, rows: [{ value:`${fmt.n(v)}개사`, label: fmt.pct(pctOf(v, r.total)), color: f }] }), false);
      bar.append(sp); segs.push(sp);
    }
    wrap.append(h('div', { class:'segrow' }, h('span', { class:'lbl' }, r.label), bar));
  }
  box.append(wrap);
  requestAnimationFrame(() => segs.forEach(sp => sp.classList.toggle('nolabel', sp.scrollWidth > sp.clientWidth + 1)));
}

/* 스파크라인 (5개년 · 회색 선 + 올해 점) */
function sparkline(values, { w = 80, hh = 24, fmtV = fmt.sc, name = '' } = {}) {
  const pts = values.map((v, i) => v == null ? null : [i, v]).filter(Boolean);
  const svg = s('svg', { width: w, height: hh, class:'spark', role:'img', 'aria-label': `${name} 5개년 ` + values.map((v, i) => `${YEARS[i]} ${v == null ? '없음' : fmtV(v)}`).join(', ') });
  if (pts.length < 2) { svg.append(text(2, hh - 8, '–')); return svg; }
  const vs = pts.map(p => p[1]), lo = Math.min(...vs), hi = Math.max(...vs), pad = (hi - lo || 1) * 0.2;
  const X = i => 4 + i * (w - 10) / (values.length - 1), Y = v => hh - 4 - (v - lo + pad) / (hi - lo + 2 * pad) * (hh - 8);
  svg.append(s('path', { d: pts.map((p, k) => `${k ? 'L' : 'M'}${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(''), fill:'none', stroke: P.prev, 'stroke-width': 2, 'stroke-linejoin':'round', 'stroke-linecap':'round' }));
  const last = pts[pts.length - 1];
  svg.append(s('circle', { cx: X(last[0]), cy: Y(last[1]), r: 3.5, fill: P.accent, stroke: P.surface, 'stroke-width': 1.5 }));
  bindTip(svg, () => ({ title:`${name} 5개년`, rows: values.map((v, i) => ({ value: v == null ? '–' : fmtV(v), label:`${YEARS[i]}년` })) }), false);
  return svg;
}

/* 연도별 선 차트 — series: [{name, values, color, main}] · 점선 = 기준(목표·등급 기준) · pointChip(i) = 점 위 등급 표시 */
function lineYears(box, { series, bench, fmtV = fmt.sc, height = 230, pointChip } = {}) {
  box.replaceChildren();
  const W = width(box, 260), H = height, m = { l: 34, r: 46, t: pointChip ? 30 : 18, b: 26 }, iw = W - m.l - m.r, ih = H - m.t - m.b, n = YEARS.length;
  const all = series.flatMap(se => se.values).filter(v => v != null).concat(bench ? [bench.value] : []);
  const lo = Math.floor(Math.min(...all) - 2), hi = Math.ceil(Math.max(...all) + 2);
  const x = i => m.l + i * iw / (n - 1), y = v => m.t + ih - (v - lo) / (hi - lo) * ih;
  const svg = s('svg', { width: W, height: H, role:'img', 'aria-label': series.map(se => `${se.name}: ` + se.values.map((v, i) => `${YEARS[i]} ${v == null ? '없음' : fmtV(v)}`).join(', ')).join(' / ') });
  const step = Math.max(1, Math.ceil((hi - lo) / 4));
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) { const yy = Math.round(y(v)) + 0.5; svg.append(s('line', { x1: m.l, x2: W - m.r, y1: yy, y2: yy, stroke: P.grid }), text(m.l - 6, yy + 4, v, { anchor:'end', num: true })); }
  YEARS.forEach((yr, i) => svg.append(text(x(i), H - 7, yr, { anchor:'middle', num: true, weight: i === n - 1 ? 700 : null, fill: i === n - 1 ? P.ink : P.muted })));
  if (bench) { const by = y(bench.value); svg.append(s('line', { x1: m.l, x2: W - m.r, y1: by, y2: by, stroke: P.bench, 'stroke-width': 1.5, 'stroke-dasharray':'5 4' }), text(m.l + 6, by - 6, bench.label, { size: 11.5, weight: 700, fill: P.ink2 })); }
  const ends = [];
  for (const se of series) {
    const segs = []; let cur = [];
    se.values.forEach((v, i) => { if (v == null) { if (cur.length) segs.push(cur); cur = []; } else cur.push([x(i), y(v)]); });
    if (cur.length) segs.push(cur);
    for (const sg of segs) {
      const d = sg.map((p, k) => `${k ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('');
      if (se.main && sg.length > 1) svg.append(s('path', { d: `${d}L${sg[sg.length - 1][0]} ${m.t + ih}L${sg[0][0]} ${m.t + ih}Z`, fill: se.color, 'fill-opacity': 0.08 }));
      svg.append(s('path', { d, fill:'none', stroke: se.color, 'stroke-width': 2, 'stroke-linejoin':'round' }));
    }
    se.values.forEach((v, i) => { if (v != null && (se.main || i === n - 1)) svg.append(s('circle', { cx: x(i), cy: y(v), r: se.main ? 4.5 : 3.5, fill: se.color, stroke: P.surface, 'stroke-width': 2 })); });
    const lv = se.values[n - 1]; if (lv != null) ends.push({ y: y(lv), t: fmtV(lv), main: se.main });
  }
  if (ends.length === 2 && Math.abs(ends[0].y - ends[1].y) < 14) { const [a, b] = ends[0].y < ends[1].y ? ends : [ends[1], ends[0]]; a.y -= 7; b.y += 7; }
  ends.forEach(e => svg.append(text(x(n - 1) + 9, e.y + 4, e.t, { size: e.main ? 13 : 11.5, weight: e.main ? 800 : 600, fill: e.main ? P.ink : P.muted, num: true })));
  if (pointChip) series.find(se => se.main).values.forEach((v, i) => {
    if (v == null) return; const g = pointChip(i); if (!g) return; const f = gradeColor(g), cx = x(i), cy = y(v) - 18;
    svg.append(s('rect', { x: cx - 9, y: cy - 9, width: 18, height: 16, rx: 4, fill: f }), text(cx, cy + 3, g, { anchor:'middle', size: 11, weight: 800, fill: inkOn(f) }));
  });
  YEARS.forEach((yr, i) => {
    const hit = s('rect', { x: x(i) - iw / (n - 1) / 2, y: 0, width: iw / (n - 1), height: H, fill:'transparent' });
    bindTip(hit, () => ({ title:`${yr}년`, rows: series.map(se => ({ value: se.values[i] == null ? '–' : fmtV(se.values[i]), label: se.name, color: se.color })).concat(pointChip && pointChip(i) ? [{ value: pointChip(i), label:'등급' }] : []) }));
    svg.append(hit);
  });
  box.append(svg);
}

/* 순위: 값이 높을수록 1위. 상위 20% = 파랑, 하위 20% = 빨강, 그 외 회색 */
function ranker(values) {
  const arr = values.filter(v => v != null).sort((a, b) => b - a);
  return v => { if (v == null) return null; let lo = 0, hi = arr.length; while (lo < hi) { const mid = (lo + hi) >> 1; if (arr[mid] > v) lo = mid + 1; else hi = mid; } const rank = lo + 1; return { rank, total: arr.length, top: rank / arr.length * 100 }; };
}
const rankText = r => r.top <= 50 ? `상위 ${fmt.pct(Math.max(r.top, 0.1))}` : `하위 ${fmt.pct(Math.max((r.total - r.rank + 1) / r.total * 100, 0.1))}`;
function rankCell(r) {
  if (!r) return '–';
  const tone = r.top <= 20 ? '' : r.top > 80 ? 'bad' : 'ctx';
  return h('span', { class:'rank' }, h('span', { class:'r' }, `${fmt.n(r.rank)}위`), meter(1 - (r.rank - 1) / Math.max(1, r.total), { tone, label:`${r.rank}위 / ${r.total}` }), h('span', { class:'p' }, rankText(r)));
}

/* =====================================================================
   5. 상태 · 필터 · 공통 정의
   ===================================================================== */
const state = {
  page:'', detail:false, area:null, company:null, coItem:null, coOpen: new Set(), rpOpen: new Set(), rpAll: false,
  list:{ q:'', chip:'all', sort:'score_desc', page:1 },
  filters:{ org:'', region:'', inout:'', unit:'', group:'', grade:'' },
};
const FILTER_LABEL = { org:'평가조직', region:'권역명', inout:'내/외자', unit:'평가단위', group:'세부업종그룹', grade:'D/T 최종 등급' };
function filtered() {
  const f = state.filters;
  return SUP.filter(x => (!f.org || x.evals.some(e => e.org === f.org)) && (!f.region || x.region === f.region) && (!f.inout || x.inout === f.inout)
    && (!f.unit || x.unit === f.unit) && (!f.group || x.group === f.group) && (!f.grade || x.grade === f.grade));
}
const areaAvg = (L, code, key = 'areas') => avg(L.filter(x => x[key][code].conv != null), x => x[key][code].conv);
const nearA = x => x.dtScore >= CONFIG.gradeCut.A - 5 && x.dtScore < CONFIG.gradeCut.A;
const ACT = {      // 조치 대상 분류
  all:  { label:'전체',          f: x => x.move < 0 || x.grade === 'D' || x.adjTarget || !!x.stopPlan },
  down: { label:'등급 하락',      f: x => x.move < 0 },
  drop2:{ label:'2단계 이상 하락', f: x => x.move <= -2 },
  d:    { label:'D등급',         f: x => x.grade === 'D' },
  adj:  { label:'등급 조정 대상',  f: x => x.adjTarget },
  stop: { label:'거래중단 예정',   f: x => !!x.stopPlan },
};
const LIST = {     // 협력사 목록 칩
  all:  { label:'전체', f: () => true }, up: { label:'등급 상승', f: x => x.move > 0 }, down: ACT.down, drop2: ACT.drop2,
  poor: { label:'부진사', f: x => critPass(CONFIG.criteria.poor, x) }, exc: { label:'우수사 후보', f: x => critPass(CONFIG.criteria.excellent, x) },
  nearA:{ label:'A 승급 후보', f: nearA }, cd: { label:'C·D 등급', f: x => GI[x.grade] >= 2 }, adj: ACT.adj, stop: ACT.stop,
};
const reasons = x => h('span', { class:'badges' },
  x.move <= -2 ? badge(`${-x.move}단계 하락`, 'bad', 'down') : x.move < 0 ? badge('등급 하락', 'bad', 'down') : null,
  x.grade === 'D' ? badge('D등급', 'bad') : null, x.adjTarget ? badge('등급 조정', 'warn', 'adjust') : null,
  x.stopPlan ? badge(`거래중단 예정 ${x.stopPlan.slice(5)}`, 'warn', 'stop') : null);
const nameCell = x => h('span', null, h('b', null, x.name), h('span', { class:'sub2' }, x.code));
function go(page) { if (location.hash === '#' + page) route(); else location.hash = '#' + page; }   // hashchange → route
function openCompany(code) { state.company = code; state.coItem = null; go('company'); requestAnimationFrame(() => $('#co-head')?.scrollIntoView({ behavior:'smooth', block:'start' })); }
function openList(chip) { state.list.chip = chip; state.list.page = 1; state.list.q = ''; go('company'); }
function openArea(code) { state.area = code; go('area'); }
function applyFilter(key, value) { state.filters[key] = value; const el = $('#f-' + key); if (el) el.value = value; renderAll(); }
const secHead = (no, title, desc) => h('div', { class:'sec-h' }, h('span', { class:'no' }, no), h('h2', null, title), desc ? h('p', null, desc) : null);
const setLead = t => { $('#page-lead').textContent = t; };

/* =====================================================================
   6. 공통 부품 (결과 요약 · 항목별 · 협력사별)
   ===================================================================== */
function dchg(v, maxAbs, unit = '', w = 96) {   // 0을 가운데 둔 증감 막대: 오른쪽 파랑 = 상승, 왼쪽 빨강 = 하락
  const f = clamp(Math.abs(v) / (maxAbs || 1), 0, 1) * 100;
  return h('span', { style:'white-space:nowrap' }, h('span', { class:'dchg', style:`width:${w}px`, 'aria-hidden':'true' }, h('span', null, v < 0 ? h('i', { style:`width:${f}%` }) : null), h('span', null, v > 0 ? h('i', { style:`width:${f}%` }) : null)), delta(v, unit));
}
const critPass = (c, x) => { const m = c.rules.filter(r => r.test(x)).length; return c.mode === 'all' ? m === c.rules.length : m > 0; };
const critLine = c => h('div', { class:'crit' }, badge(c.fixed ? '확정 기준' : '임시 기준', c.fixed ? 'good' : 'warn', c.fixed ? null : 'warn'), h('span', null, c.rules.map(r => r.label).join(c.mode === 'all' ? ' · 그리고 · ' : ' · 또는 · ')));
const areaGaps = (x, base) => CONFIG.areas.map((a, j) => ({ a, v: x.areas[a.code].conv, d: x.areas[a.code].conv == null ? null : x.areas[a.code].conv - base[j] })).filter(r => r.d != null);
const bigAreaMove = x => CONFIG.areas.map(a => ({ a, d: x.areas[a.code].conv != null && x.prevAreas[a.code].conv != null ? x.areas[a.code].conv - x.prevAreas[a.code].conv : 0 })).reduce((m, r) => Math.abs(r.d) > Math.abs(m.d) ? r : m);
const csvBtn = (label, file, header, rows) => h('button', { class:'btn primary sm', type:'button', onclick: () => downloadCSV(file, header, rows()) }, icon('download'), label);
const supSub = (x, extra) => h('span', null, h('b', null, x.name), h('span', { class:'sub2' }, [x.code, x.org, x.group, extra].filter(Boolean).join(' · ')));
const filterText = () => Object.entries(state.filters).filter(([, v]) => v).map(([k, v]) => `${FILTER_LABEL[k]} ${v}`).join(' · ') || '전체';
function kpi({ key, label, ic, value, unit, delta: d, extra, action }) {
  return h('div', { class:'kpi' + (key ? ' key' : '') },
    h('div', { class:'kpi-top' }, h('span', { class:'kpi-label' }, icon(ic), label)),
    h('div', { class:'kpi-val' }, value, unit ? h('small', null, unit) : null), h('div', { class:'kpi-row' }, d), extra || null, action || null);
}
function itemStats(L, area) {      // 평가항목 평균 (미적용·무실적 제외)
  return ITEMS.map((c, i) => ({ c, i })).filter(({ c }) => c.area === area).map(({ c, i }) => {
    let n = 0, cur = 0, prev = 0, na = 0, np = 0;
    for (const x of L) { const it = x.items[i]; if (it.na) { na++; continue; } if (it.np) { np++; continue; } n++; cur += it.r; prev += it.pr; }
    return { ...c, idx: i, n, value: n ? cur / n * 100 : 0, prev: n ? prev / n * 100 : 0, na, np };
  });
}
/* 펼침 표: 영역 행을 누르면 평가항목 행이 열림 (인쇄 시 모두 펼침) */
function expandTable(cols, groups, { isOpen, onToggle, onSub, selSub } = {}) {
  const tb = h('tbody');
  for (const g of groups) {
    const open = isOpen(g.key);
    const tr = h('tr', { class:'grp', tabindex:'0', 'aria-expanded': String(open) }, g.cells.map((v, k) => h('td', { class: cols[k].num ? 'num' : null }, k ? v : [h('span', { class:'caret' }, open ? '▾' : '▸'), v])));
    const tog = () => onToggle(g.key);
    tr.addEventListener('click', tog); tr.addEventListener('keydown', e => { if (e.key === 'Enter') tog(); });
    tb.append(tr);
    g.subs.forEach((sub, i) => {
      const r = h('tr', { class:'sub' + (open ? '' : ' hide') + (onSub ? ' click' : ''), tabindex: onSub ? '0' : null, 'aria-selected': selSub && selSub(g.key, i) ? 'true' : null }, sub.map((v, k) => h('td', { class: cols[k].num ? 'num' : null }, v)));
      if (onSub) { r.addEventListener('click', () => onSub(g.key, i)); r.addEventListener('keydown', e => { if (e.key === 'Enter') onSub(g.key, i); }); }
      tb.append(r);
    });
  }
  return h('div', { class:'tw' }, h('table', { class:'t' }, h('thead', null, h('tr', null, cols.map(c => h('th', { class: c.num ? 'num' : null }, c.label)))), tb));
}
const gradeLegend = id => legend(id, CONFIG.grades.map(g => ({ color: gradeColor(g), label:`${g} ${CONFIG.gradeGroup[g]}` })));

/* =====================================================================
   10. AI 대화 패널 — 오른쪽 패널 + 화살표 손잡이 (디자인·동작). 사내 LLM API는 window.SUPPLIER_CHAT.ask 로 연결
   ===================================================================== */
/* ★ 사내 API 연결 자리 — 이 스크립트보다 먼저 한 번만 정의하면 됩니다. (키·주소·호출 코드는 여기 없음)
   window.SUPPLIER_CHAT = {
     name: '사내 AI',                                                       // (선택) 패널 제목
     ask: async ({ message, history, context }) => '답변'                    // 문자열 또는 { text: '답변' }
   };
   · history = 이번 질문 앞의 대화 [{ role: 'user' | 'assistant', text }] (최근 20개)
   · context = 화면 정보 { screen, hash, year, filters, count, detail, summary, selected } — 패널의 '현재 화면 포함'을 끄면 null
   · 답변 글자는 마크다운 일부(**굵게**, `코드`, - 목록, 1. 목록)를 보여 줍니다. 연결 전에는 'API 미연결' 안내 답변(데모 응답)이 나옵니다. */
const CHAT = { open: false, busy: false, useCtx: true, gen: 0, msgs: [] };
const chatApi = () => (window.SUPPLIER_CHAT && typeof window.SUPPLIER_CHAT.ask === 'function') ? window.SUPPLIER_CHAT : null;
const chatEls = { root: $('#chat-root'), handle: $('#chat-handle'), panel: $('#chat-panel'), ctx: $('#chat-ctx'), log: $('#chat-log'), live: $('#chat-live'), form: $('#chat-form'), input: $('#chat-input'), send: $('#chat-send') };

function chatContext() {            // 질문과 함께 보낼 현재 화면 정보 (필요한 만큼만)
  const L = filtered(), n = L.length;
  const c = { screen: TITLES[state.page], hash: '#' + state.page, year: CONFIG.year, filters: Object.fromEntries(Object.entries(state.filters).filter(([, v]) => v).map(([k, v]) => [FILTER_LABEL[k], v])), count: n, detail: state.detail };
  if (n) { const gc = countBy(L, x => x.grade); c.summary = { avgDtScore: Math.round(avg(L, x => x.dtScore) * 10) / 10, grades: Object.fromEntries(CONFIG.grades.map(g => [g, gc[g] || 0])) }; }
  if (state.page === 'company' && BY_CODE.has(state.company)) { const x = BY_CODE.get(state.company); c.selected = { type: '협력사', code: x.code, name: x.name, grade: x.grade, dtScore: x.dtScore }; }
  if (state.page === 'area' && state.area) c.selected = { type: '영역', code: state.area, name: AREA[state.area].name };
  return c;
}
function chatSuggestions() {        // 화면에 따라 달라지는 추천 질문
  if (state.page === 'area' && state.area) { const a = aname(state.area); return [`${a} 영역 점수가 낮은 이유가 뭘까?`, `${a}에서 먼저 개선할 평가항목은?`, '전년 대비 가장 좋아진 영역은 어디야?']; }
  if (state.page === 'company' && BY_CODE.has(state.company)) { const nm = BY_CODE.get(state.company).name; return [`${nm} 결과를 3줄로 요약해줘`, `${nm}의 약점 영역과 개선 방향은?`, `${nm}의 5개년 추이를 설명해줘`]; }
  return ['이번 결과를 3줄로 요약해줘', '등급이 하락한 협력사의 공통점은?', '부진사 목록과 원인을 정리해줘', '전년 대비 가장 좋아진 업종은?'];
}
function chatRich(text) {           // 안전한 간이 마크다운 → DOM (innerHTML을 쓰지 않음)
  const box = h('div'); let list = null, kind = '';
  const inline = (s, parent) => { s.split(/(\*\*[^*]+\*\*|`[^`]+`)/).forEach(t => { if (!t) return; if (t.length > 4 && t.startsWith('**') && t.endsWith('**')) parent.append(h('b', null, t.slice(2, -2))); else if (t.length > 2 && t.startsWith('`') && t.endsWith('`')) parent.append(h('code', null, t.slice(1, -1))); else parent.append(document.createTextNode(t)); }); return parent; };
  for (const raw of String(text).split('\n')) {
    const line = raw.trimEnd(), ul = line.match(/^\s*[-*•]\s+(.*)/), ol = line.match(/^\s*\d+[.)]\s+(.*)/);
    if (ul || ol) { const k = ul ? 'ul' : 'ol'; if (!list || kind !== k) { list = h(k); kind = k; box.append(list); } list.append(inline((ul || ol)[1], h('li'))); continue; }
    list = null; if (line.trim()) box.append(inline(line, h('p')));
  }
  return box;
}
const hhmm = d => `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
function chatMsgEl(m) {
  if (m.role === 'user') return h('div', { class: 'msg user' }, h('div', { class: 'msg-col' }, h('div', { class: 'bub' }, m.text), h('div', { class: 'meta' }, hhmm(m.at))));
  const av = h('span', { class: 'av', 'aria-hidden': 'true' }, icon('sparkle'));
  if (m.role === 'typing') return h('div', { class: 'msg ai' }, av, h('div', { class: 'msg-col' }, h('div', { class: 'bub', role: 'status', 'aria-label': '답변 작성 중' }, h('span', { class: 'dots' }, h('i'), h('i'), h('i')))));
  const act = m.error ? h('button', { class: 'link', type: 'button', onclick: () => chatRetry() }, '다시 시도') : h('button', { class: 'link', type: 'button', onclick: e => chatCopy(m.text, e.currentTarget) }, icon('copy'), '복사');
  return h('div', { class: 'msg ai' }, av, h('div', { class: 'msg-col' }, h('div', { class: 'bub' + (m.error ? ' err' : '') }, m.error ? h('p', null, m.text) : chatRich(m.text)), h('div', { class: 'meta' }, hhmm(m.at), m.demo ? badge('데모 응답', 'warn') : null, act)));
}
function renderChatLog() {
  const log = chatEls.log; log.replaceChildren();
  if (!CHAT.msgs.length) log.append(h('div', { class: 'chat-empty' },
    h('div', { class: 'hi' }, h('i', null, icon('sparkle')), h('b', null, '무엇을 도와드릴까요?'), h('span', null, '화면의 결과를 바탕으로 질문해 보세요.')),
    h('div', { class: 'sugg' }, chatSuggestions().map(q => h('button', { type: 'button', onclick: () => chatSendMsg(q) }, icon('chat'), q)))));
  else CHAT.msgs.forEach(m => log.append(chatMsgEl(m)));
  log.scrollTop = log.scrollHeight;
}
function renderChatContext() {      // 화면이 바뀔 때마다 호출 (renderAll)
  const c = chatEls.ctx, L = filtered(), sel = chatContext().selected;
  const txt = `${TITLES[state.page]} · ${filterText()} · ${fmt.n(L.length)}개사${sel ? ` · 선택: ${sel.name}` : ''}`;
  c.replaceChildren(
    h('button', { class: 'chip', type: 'button', 'aria-pressed': String(CHAT.useCtx), title: '켜면 현재 화면 정보를 질문과 함께 보냅니다', onclick: () => { CHAT.useCtx = !CHAT.useCtx; renderChatContext(); } }, '현재 화면 포함'),
    h('span', { class: 'txt', title: txt }, CHAT.useCtx ? txt : '화면 정보를 보내지 않음'));
  if (!CHAT.msgs.length) renderChatLog();      // 처음 화면의 추천 질문은 화면 상태를 따라감
}
function renderChatHeader() { const api = chatApi(); $('#chat-name').textContent = (api && api.name) || 'AI 어시스턴트'; $('#chat-status').hidden = !!api; }
function setChat(open, { focus = true } = {}) {
  CHAT.open = open; const e = chatEls;
  e.root.dataset.open = String(open); e.panel.setAttribute('aria-hidden', String(!open)); $('.app').classList.toggle('chat-open', open);
  e.handle.setAttribute('aria-expanded', String(open)); e.handle.setAttribute('aria-label', open ? 'AI 대화 닫기' : 'AI 대화 열기');
  if (open) { renderChatHeader(); renderChatContext(); renderChatLog(); if (focus) requestAnimationFrame(() => e.input.focus({ preventScroll: true })); }
  else if (focus && e.panel.contains(document.activeElement)) e.handle.focus();
}
const chatAutosize = () => { const t = chatEls.input; t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight, 120) + 'px'; chatEls.send.disabled = CHAT.busy || !t.value.trim(); };
const chatBusy = b => { CHAT.busy = b; chatAutosize(); };
async function chatAsk(message) {
  const api = chatApi(), history = CHAT.msgs.filter(m => m.role === 'user' || (m.role === 'assistant' && !m.error)).slice(0, -1).slice(-20).map(m => ({ role: m.role, text: m.text }));
  const context = CHAT.useCtx ? chatContext() : null;
  if (api) { const r = await api.ask({ message, history, context }), text = typeof r === 'string' ? r : r && r.text; if (!text) throw new Error('빈 답변'); return { text }; }
  await new Promise(res => setTimeout(res, 750));
  return { demo: true, text: `**사내 API가 아직 연결되지 않았습니다.**\n연결하면 이 자리에 답변이 표시됩니다.\n- 질문: ${message}\n- 함께 보낼 화면 정보: ${context ? `${context.screen} · ${filterText()} · ${fmt.n(context.count)}개사` : '없음'}` };
}
async function chatSendMsg(text) {
  text = String(text || '').trim(); if (!text || CHAT.busy) return;
  const gen = CHAT.gen, typing = { role: 'typing' };
  CHAT.msgs.push({ role: 'user', text, at: new Date() }, typing); chatEls.input.value = ''; chatBusy(true); renderChatLog();
  let reply;
  try { const r = await chatAsk(text); reply = { role: 'assistant', text: r.text, demo: r.demo, at: new Date() }; }
  catch (err) { reply = { role: 'assistant', text: '답변을 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.', error: true, at: new Date() }; }
  if (gen !== CHAT.gen) return;                  // 그 사이 '새 대화'를 눌렀으면 늦게 온 답변은 버림
  CHAT.msgs.splice(CHAT.msgs.indexOf(typing), 1, reply); chatBusy(false); renderChatLog(); chatEls.live.textContent = reply.text;
}
function chatRetry() {
  const last = [...CHAT.msgs].reverse().find(m => m.role === 'user'); if (!last) return;
  CHAT.msgs = CHAT.msgs.filter(m => !(m.role === 'assistant' && m.error)); CHAT.msgs.splice(CHAT.msgs.lastIndexOf(last), 1); chatSendMsg(last.text);
}
async function chatCopy(text, btn) {
  try { await navigator.clipboard.writeText(text); }
  catch (e) { const t = h('textarea', { style: 'position:fixed;opacity:0' }); t.value = text; document.body.append(t); t.select(); try { document.execCommand('copy'); } catch (e2) { /* 복사 불가 환경은 무시 */ } t.remove(); }
  const old = btn.lastChild.textContent; btn.lastChild.textContent = '복사됨'; setTimeout(() => { btn.lastChild.textContent = old; }, 1200);
}
chatEls.handle.addEventListener('click', () => setChat(!CHAT.open));
$('#chat-close').addEventListener('click', () => setChat(false));
$('#chat-new').addEventListener('click', () => { CHAT.gen++; CHAT.msgs = []; chatBusy(false); renderChatLog(); chatEls.input.focus(); });
chatEls.form.addEventListener('submit', e => { e.preventDefault(); chatSendMsg(chatEls.input.value); });
chatEls.input.addEventListener('input', chatAutosize);
chatEls.input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.keyCode !== 229) { e.preventDefault(); chatSendMsg(chatEls.input.value); } });   // 한글 입력 중 Enter(조합 확정)는 전송하지 않음
chatEls.panel.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); setChat(false); } });
renderChatHeader(); chatAutosize();

/* =====================================================================
   11. 화면 전환 · 필터 · 테마 · 초기화
   ===================================================================== */
const PAGES = ['report', 'area', 'company'];
const TITLES = { report:'결과 요약', area:'항목별 결과', company:'협력사별 결과' };
const BUILT = {}, BUILDERS = { report: buildReport, area: buildArea, company: buildCompany }, RENDERERS = { report: renderReport, area: renderArea, company: renderCompany };
function route() {
  const p = (location.hash || '#report').slice(1), next = PAGES.includes(p) ? p : 'report';
  if (next !== state.page) window.scrollTo(0, 0);
  state.page = next;
  document.querySelectorAll('.nav a').forEach(a => { if (a.dataset.page === next) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  $('#page-title').textContent = TITLES[next];
  document.title = `${TITLES[next]} · 협력사 종합평가`;
  renderAll();
}
function resetFilters() { Object.keys(state.filters).forEach(k => { state.filters[k] = ''; const el = $('#f-' + k); if (el) el.value = ''; }); state.area = null; renderAll(); }
function renderActiveFilters() {
  const on = Object.entries(state.filters).filter(([, v]) => v);
  $('#active-f').replaceChildren(...(on.length ? [h('span', null, '적용 중인 필터'), ...on.map(([k, v]) => h('button', { class:'fchip', type:'button', 'aria-label':`${FILTER_LABEL[k]} ${v} 필터 해제`, onclick: () => applyFilter(k, '') }, `${FILTER_LABEL[k]} `, h('b', null, v), ' ✕')), h('button', { class:'link', type:'button', onclick: resetFilters }, '모두 해제')] : []));
}
function renderAll() {
  hideTip(); renderActiveFilters();
  const L = filtered(), empty = L.length === 0;
  $('#empty').hidden = !empty;
  PAGES.forEach(k => { $('#page-' + k).hidden = empty || k !== state.page; });
  if (empty) { setLead('조건에 맞는 협력사가 없습니다.'); renderChatContext(); return; }
  if (!BUILT[state.page]) { BUILDERS[state.page](); BUILT[state.page] = true; }
  RENDERERS[state.page](L);
  renderChatContext();                           // 화면이 정해진 뒤에 갱신 (선택 영역·선택 협력사가 이 안에서 정해짐)
}
function fillSelect(id, values) { $('#' + id).replaceChildren(h('option', { value:'' }, '전체'), ...values.map(v => h('option', { value: v }, v))); }
fillSelect('f-org', CONFIG.orgs); fillSelect('f-region', CONFIG.regions.map(r => r.name)); fillSelect('f-inout', ['내자', '외자']);
fillSelect('f-unit', CONFIG.units); fillSelect('f-group', CONFIG.groups); fillSelect('f-grade', CONFIG.grades);
Object.keys(state.filters).forEach(k => $('#f-' + k).addEventListener('change', e => { state.filters[k] = e.target.value; if (k !== 'grade') state.area = null; renderAll(); }));

/* 상세 보기: 기본은 핵심만, 켜면 세부 카드·표·목록이 함께 펼쳐짐 */
$('#detail-btn').addEventListener('click', e => {
  state.detail = !state.detail; document.body.classList.toggle('show-detail', state.detail);
  e.currentTarget.setAttribute('aria-pressed', String(state.detail)); e.currentTarget.textContent = state.detail ? '상세 보기 켜짐' : '상세 보기';
  if (!state.detail) { state.coItem = null; }
  renderAll();
});

/* 기본은 라이트(참고 디자인과 동일), 버튼으로 다크 전환 — 다크 색은 별도 검증값 */
function applyTheme(t) {
  document.documentElement.dataset.theme = t; P = PALETTE[t];
  const b = $('#theme-btn'); b.setAttribute('aria-pressed', String(t === 'dark')); b.textContent = t === 'dark' ? '라이트 모드' : '다크 모드';
}
$('#theme-btn').addEventListener('click', () => {
  const t = P === PALETTE.dark ? 'light' : 'dark'; applyTheme(t);
  try { localStorage.setItem('supplier-dash-theme', t); } catch (e) { /* 저장 불가 환경 무시 */ }
  renderAll();
});
let savedTheme = 'light';
try { savedTheme = localStorage.getItem('supplier-dash-theme') === 'dark' ? 'dark' : 'light'; } catch (e) { /* 무시 */ }
applyTheme(savedTheme);

let lastW = 0, rTimer;
new ResizeObserver(en => { const w = Math.round(en[0].contentRect.width); if (w === lastW) return; lastW = w; clearTimeout(rTimer); rTimer = setTimeout(renderAll, 120); }).observe($('.main'));
window.addEventListener('hashchange', route);
route();
```

---

## 부록 E. 샘플 데이터 생성기 (개발·검증용, 난수 호출 순서 그대로)

시드 `20261109`(협력사 1,248개), 5개년 이력 시드 `5150`. **난수 호출 순서를 바꾸면 부록 F의 골든 값이 달라집니다.**

```js
/* =====================================================================
   2. 가상 샘플 데이터 — 실제 구현에서는 엑셀 4종 파싱 결과로 교체
   해석(가정): 배점 = 적용 항목 배점 합(미적용·무실적 제외), 평점 = 득점 합, 환산점수 = 평점 ÷ 배점 × 100,
              평가 점수 = 일반항목 환산점수 + 가산점, D/T 종합 점수 = Σ(평가조직별 평가 점수 × 거래비중)
   ===================================================================== */
function mulberry32(a){ return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const rnd = mulberry32(20261109);
const gauss = () => { let u = 0, v = 0; while (!u) u = rnd(); while (!v) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
const pick = (arr, w) => { if (!w) return arr[Math.floor(rnd() * arr.length)]; let x = rnd() * w.reduce((a, b) => a + b, 0); for (let i = 0; i < arr.length; i++) { x -= w[i]; if (x <= 0) return arr[i]; } return arr[arr.length - 1]; };
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const r1 = x => Math.round(x * 10) / 10;
const GI = Object.fromEntries(CONFIG.grades.map((g, i) => [g, i]));   // 0 = 최상위 등급
const gradeOf = v => { const c = CONFIG.gradeCut; return v >= c.A ? 'A' : v >= c.B ? 'B' : v >= c.C ? 'C' : 'D'; };
const AREA = Object.fromEntries(CONFIG.areas.map(a => [a.code, a]));
const aname = code => `${AREA[code].name}(${code})`;

/* 평가항목 카탈로그 (3번: 분류체계 = 영역 코드, 분류체계 유형 = 정량/정성 ※ 가정) */
const ITEMS = [];
const ITEM_COUNT = { T:3, Q:4, R:2, D:3, C:3, E:2, F:3, A:2 };
for (const a of CONFIG.areas) {
  const n = ITEM_COUNT[a.code];
  for (let k = 1; k <= n; k++) {
    const no = String(k).padStart(2, '0');
    ITEMS.push({ code: a.code + no, name: `${a.name} 평가항목 ${no}`, area: a.code, classType: k % 2 ? '정량' : '정성', max: a.max / n, bias: (rnd() - 0.5) * 0.14 });
  }
}
const AREA_BIAS = { T:0.01, Q:-0.04, R:0.03, D:0, C:-0.02, E:0.05, F:-0.01, A:0.04 };
const ORG_BIAS = Object.fromEntries(CONFIG.orgs.map(o => [o, (rnd() - 0.5) * 0.04]));
const GROUP_BIAS = Object.fromEntries(CONFIG.groups.map(g => [g, (rnd() - 0.5) * 0.05]));
const COUNTRIES = ['중국','베트남','멕시코','인도','미국'];

function scoreFromItems(items, key) {             // key: 'r' 당해 | 'pr' 이전
  let max = 0, raw = 0; const areas = {};
  for (const a of CONFIG.areas) areas[a.code] = { max: 0, raw: 0 };
  items.forEach((it, i) => {
    if (it.na || it.np) return;
    const c = ITEMS[i]; max += c.max; raw += c.max * it[key];
    areas[c.area].max += c.max; areas[c.area].raw += c.max * it[key];
  });
  for (const a of Object.values(areas)) a.conv = a.max ? a.raw / a.max * 100 : null;
  return { max: r1(max), raw: r1(raw), conv: max ? r1(raw / max * 100) : 0, areas };
}

const N = 1248;
const SUP = [];
for (let i = 0; i < N; i++) {
  const region = pick(CONFIG.regions, [32, 20, 26, 10, 12]);
  const foreign = region.code === 'R5';
  const group = pick(CONFIG.groups, [22, 18, 16, 14, 12, 18]);
  const org = pick(CONFIG.orgs, [26, 22, 20, 18, 14]);
  const unitIdx = Math.floor(rnd() * CONFIG.units.length);
  const weak = rnd() < 0.03;                                  // 일부는 크게 낮게 (D등급 표본)
  const base = 0.845 + gauss() * 0.072 + ORG_BIAS[org] + GROUP_BIAS[group] - (weak ? 0.2 + rnd() * 0.08 : 0);
  const crash = rnd() < 0.015;                                // 전년보다 크게 하락한 협력사 (2단계 이상 하락 표본)
  const prevGap = 0.012 + gauss() * 0.035 - (crash ? 0.13 + rnd() * 0.04 : 0);
  const items = ITEMS.map(c => {
    const soft = v => v > 0.9 ? 0.9 + 0.1 * Math.tanh((v - 0.9) / 0.1) : v;      // 100% 상한에 몰리지 않게
    const r = clamp(soft(base + AREA_BIAS[c.area] + c.bias + gauss() * 0.06), 0.25, 1);
    const pr = clamp(soft(r - prevGap + gauss() * 0.04), 0.25, 1);
    const roll = rnd();
    return { r: Math.round(r * 1000) / 1000, pr: Math.round(pr * 1000) / 1000, na: roll < 0.03, np: roll >= 0.03 && roll < 0.05 };
  });
  const cur = scoreFromItems(items, 'r'), prv = scoreFromItems(items, 'pr');
  const bonus = rnd() < 0.32 ? r1(rnd() * CONFIG.bonusMax) : 0;
  const pbonus = rnd() < 0.30 ? r1(rnd() * CONFIG.bonusMax) : 0;
  const score = r1(Math.min(100, cur.conv + bonus));
  const pscore = r1(Math.min(100, prv.conv + pbonus));

  // 평가조직별 평가 → 거래비중으로 D/T 종합 점수 (2번 파일)
  const extra = pick([0, 1, 2], [55, 32, 13]);
  const pool = CONFIG.orgs.filter(o => o !== org);
  for (let k = pool.length - 1; k > 0; k--) { const j = Math.floor(rnd() * (k + 1)); [pool[k], pool[j]] = [pool[j], pool[k]]; }
  const others = pool.slice(0, extra);
  const w0 = extra ? 0.5 + rnd() * 0.3 : 1;
  const evals = [{ org, weight: w0, score }];
  let rest = 1 - w0;
  others.forEach((o, k) => { const w = k === others.length - 1 ? rest : rest * (0.4 + rnd() * 0.3); rest -= w; evals.push({ org: o, weight: w, score: r1(clamp(score + gauss() * 3.2, 35, 100)) }); });
  const subCode = `U-${'ABC'[unitIdx]}${1 + Math.floor(rnd() * 3)}`;
  evals.forEach(e => { e.weight = Math.round(e.weight * 1000) / 10; });
  evals[evals.length - 1].weight = r1(100 - evals.slice(0, -1).reduce((a, e) => a + e.weight, 0));   // 합계 100%
  evals.forEach(e => { e.grade = gradeOf(e.score); e.weighted = r1(e.score * e.weight / 100); e.subUnitCode = subCode; });
  const dtScore = r1(evals.reduce((a, e) => a + e.weighted, 0));
  const pdt = r1(clamp(pscore + gauss() * 0.8, 30, 100));
  const preGrade = gradeOf(dtScore);
  const cuts = [CONFIG.gradeCut.A, CONFIG.gradeCut.B, CONFIG.gradeCut.C], near = cuts.reduce((m, c) => Math.abs(dtScore - c) < Math.abs(dtScore - m) ? c : m, cuts[0]);
  const adjTarget = Math.abs(dtScore - near) < 2.5 && rnd() < 0.12;      // 등급 조정은 기준점 근처에서만 (기준 바로 아래 → 한 단계 위, 바로 위 → 한 단계 아래)
  const grade = adjTarget ? CONFIG.grades[clamp(GI[preGrade] + (dtScore < near ? -1 : 1), 0, CONFIG.grades.length - 1)] : preGrade;
  const gtScore = r1(clamp(dtScore + gauss() * 0.9, 30, 100));
  const code = `V${100000 + i * 7 + Math.floor(rnd() * 7)}`;
  const prevGrade = gradeOf(pdt);

  SUP.push({
    idx: i, code, name: `협력사 ${String(i + 1).padStart(4, '0')}`, rep: rnd() < 0.85 ? code : `V${100000 + Math.floor(rnd() * N) * 7}`,
    dt: `DT${String(3000 + Math.floor(i / 1.6)).padStart(5, '0')}`, gt: `GT${String(500 + Math.floor(i / 4)).padStart(4, '0')}`,
    org, generalOrg: CONFIG.orgs.indexOf(org) < 2 ? '1본부' : '2본부',
    region: region.name, regionCode: region.code, country: foreign ? pick(COUNTRIES) : '한국', inout: foreign || rnd() < 0.03 ? '외자' : '내자',
    unit: CONFIG.units[unitIdx], subUnitCode: subCode, subUnit: `세부단위 ${subCode.slice(2)}`,
    group, industry: `${group} ${1 + Math.floor(rnd() * 3)}`, size: pick(['대기업','중견','중소'], [10, 30, 60]),
    main: rnd() < 0.35 ? 'Y' : 'N', mold: rnd() < 0.42 ? 'Y' : 'N',
    stopPlan: rnd() < 0.012 ? `2026-12-${String(1 + Math.floor(rnd() * 28)).padStart(2, '0')}` : null, stopDate: null,
    confirmed: rnd() < 0.923 ? 'Y' : 'N',
    max: cur.max, genRaw: cur.raw, gen: cur.conv, bonus, score, change: r1(score - pscore),
    dtScore, preGrade, adjTarget, grade, gtScore, gtGrade: gradeOf(gtScore), orgGrade: evals[0].grade,
    move: GI[prevGrade] - GI[grade],                         // +: 상승, -: 하락 (단계 수)
    evals, items, areas: cur.areas, prevAreas: prv.areas,
    prev: { max: prv.max, genRaw: prv.raw, gen: prv.conv, bonus: pbonus, score: pscore, dtScore: pdt, grade: prevGrade },
  });
}
const BY_CODE = new Map(SUP.map(s => [s.code, s]));

/* 5개년 이력 — 실제 구현: 연도별 1·2번 파일을 쌓아 같은 구조로 채움 (2025 = [전년도 결과], 2026 = [평가결과])
   x.hist[연도] = { dt: D/T 종합 점수, grade: D/T 최종 등급, areas: { T: 환산점수, ... } } · 그 해에 평가가 없으면 null(신규 협력사) */
const YEARS = [CONFIG.year - 4, CONFIG.year - 3, CONFIG.year - 2, CONFIG.prevYear, CONFIG.year];
{
  const r2 = mulberry32(5150);
  const g2 = () => { let u = 0, v = 0; while (!u) u = r2(); while (!v) v = r2(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  for (const x of SUP) {
    const roll = r2(), join = roll < 0.86 ? YEARS[0] : roll < 0.91 ? YEARS[1] : roll < 0.96 ? YEARS[2] : YEARS[3];   // 첫 평가 연도
    const drift = 0.9 + g2() * 0.9;
    const pa = Object.fromEntries(CONFIG.areas.map(a => [a.code, x.prevAreas[a.code].conv]));
    x.hist = {};
    for (const y of YEARS.slice(0, 3)) {
      if (y < join) { x.hist[y] = null; continue; }
      const k = CONFIG.prevYear - y, dt = r1(clamp(x.prev.dtScore - drift * k + g2() * 1.6, 30, 100));
      x.hist[y] = { dt, grade: gradeOf(dt), areas: Object.fromEntries(CONFIG.areas.map(a => [a.code, pa[a.code] == null ? null : clamp(pa[a.code] - (drift + g2() * 0.5) * k + g2() * 2.2, 25, 100)])) };
    }
    x.hist[CONFIG.prevYear] = { dt: x.prev.dtScore, grade: x.prev.grade, areas: pa };
    x.hist[CONFIG.year] = { dt: x.dtScore, grade: x.grade, areas: Object.fromEntries(CONFIG.areas.map(a => [a.code, x.areas[a.code].conv])) };
  }
}
const yearAvg = (L, f) => YEARS.map(y => { const v = L.map(x => x.hist[y] ? f(x.hist[y]) : null).filter(v => v != null); return v.length ? avg(v, t => t) : null; });
```

---

## 부록 F. 골든 값 (샘플 모드, 필터 없음, 라이트 모드)

부록 E를 그대로 이식하고 본문 §7 규칙으로 계산하면 **아래 숫자가 똑같이 나와야 합니다**(개수는 정확히, 점수는 ±0.1). 화면이 이 숫자·문구와 다르면 구현이 목업과 다른 것입니다.

### F-1. 전체
| 항목 | 값 |
|---|---|
| 협력사 수 | 1,248 |
| 평균 D/T 종합 점수 (올해 / 전년) | **82.9** / 81.6 |
| 등급별 개수 올해 (A·B·C·D) | A 211 · B 648 · C 372 · D 17 |
| 등급별 개수 전년 (A·B·C·D) | A 173 · B 609 · C 443 · D 23 |
| 연도별 평균 점수 (2022→2026) | 79.2 → 80.0 → 80.7 → 81.6 → 82.9 |
| 연도별 평가 협력사 수 | 1,061 → 1,120 → 1,193 → 1,248 → 1,248 |
| 연도별 A등급 비율 % | 9.1 → 11.2 → 12.2 → 13.9 → 16.9 |
| 등급 조정 대상 · 거래중단 예정 · 협력사 확인 Y | 51 · 18 · 1,138 |

### F-2. 영역별 평균
| 영역 | 올해 평균 | 전년 평균 | 5개년 평균 (2022→2026) | 70점 미만 % |
|---|---|---|---|---|
| 기술(T) | 85.0 | 83.7 | 81.3 → 82.0 → 82.9 → 83.7 → 85.0 | 4.3 |
| 품질(Q) | 78.5 | 77.4 | 75.0 → 75.7 → 76.6 → 77.4 → 78.5 | 14.0 |
| 대응(R) | 90.4 | 88.5 | 86.1 → 86.9 → 87.7 → 88.5 → 90.4 | 1.8 |
| 납기(D) | 84.1 | 82.7 | 80.1 → 80.9 → 81.8 → 82.7 → 84.1 | 5.2 |
| 원가(C) | 76.9 | 75.9 | 73.7 → 74.4 → 75.1 → 75.9 → 76.9 | 18.8 |
| 환경(E) | 89.0 | 87.3 | 84.8 → 85.5 → 86.4 → 87.3 → 89.0 | 2.4 |
| 재무(F) | 81.8 | 80.6 | 78.1 → 79.0 → 80.0 → 80.6 → 81.8 | 7.8 |
| 기타(A) | 84.8 | 83.5 | 81.0 → 81.7 → 82.6 → 83.5 → 84.8 | 5.1 |

### F-3. 세부업종그룹
| 세부업종그룹 | 협력사 수 | 올해 평균 | 전년 대비 |
|---|---|---|---|
| 전장 | 290 | 82.3 | +1.5 |
| 기계가공 | 214 | 83.4 | +1.0 |
| 사출 | 202 | 82.3 | +1.1 |
| 프레스 | 175 | 84.5 | +1.5 |
| 소재 | 154 | 82.0 | +1.5 |
| 기타 | 213 | 83.3 | +1.3 |

### F-4. 협력사 목록 칩 개수
| 칩 | 개수 |
|---|---|
| 전체 | 1,248 |
| 등급 상승 | 229 |
| 등급 하락 | 107 |
| 2단계 이상 하락 | 1 |
| 부진사 | 18 |
| 우수사 후보 | 198 |
| A 승급 후보 | 317 |
| C·D 등급 | 389 |
| 등급 조정 대상 | 51 |
| 거래중단 예정 | 18 |

### F-5. 점수 변화 TOP 3 (상승 / 하락)
| 구분 | 협력사 | 전년 → 올해 | 변화 | 등급 |
|---|---|---|---|---|
| 상승 1 | 협력사 0246 | 65.5 → 81.6 | +16.1 | C → B |
| 상승 2 | 협력사 0043 | 64.5 → 78.0 | +13.5 | C → C |
| 상승 3 | 협력사 1189 | 71.0 → 84.1 | +13.1 | C → B |
| 하락 1 | 협력사 0046 | 88.6 → 71.5 | -17.1 | B → C |
| 하락 2 | 협력사 1024 | 93.0 → 77.9 | -15.1 | A → C |
| 하락 3 | 협력사 1105 | 76.4 → 61.7 | -14.7 | C → C |

### F-6. 부진사 · 우수사 후보 (임시 기준)
- 부진사 **18개사** — 점수 낮은 순 앞 3: 협력사 0176 42.1점(D), 협력사 0557 42.3점(D), 협력사 0027 44.3점(D)
- 우수사 후보 **198개사** — 점수 높은 순 앞 3: 협력사 1164 99.6점(A), 협력사 0086 99.5점(A), 협력사 0102 99.4점(A)

### F-7. 협력사 0001 (샘플 첫 협력사)
- **협력사 0001** (코드 V100002, 대표 평가조직 D사업부): D/T 종합 점수 78.2(전년 76.8), 등급 C → C, 전체 953위 / 1,248 (하위 24%)
- 5개년 D/T 종합 점수: 72.1 → 73.6 → 76.1 → 76.8 → 78.2
- 영역 환산점수(순위): 기술(T) 82.4(815위), 품질(Q) 75.3(839위), 대응(R) 96.1(305위), 납기(D) 70.7(1,177위), 원가(C) 70.3(1,001위), 환경(E) 81.0(1,082위), 재무(F) 74.1(1,061위), 기타(A) 73.8(1,137위)
- 평가조직 행(조직 · 거래비중% · 점수 · 등급): D사업부 52.5% 79.4 C / A사업부 47.5% 76.9 C

### F-8. 품질(Q) 영역 평가항목 평균
| 평가항목 | 올해 평균 | 전년 평균 | 미적용 | 무실적 |
|---|---|---|---|---|
| Q01 | 77.5 | 76.4 | 40 | 26 |
| Q02 | 79.0 | 77.9 | 37 | 23 |
| Q03 | 83.5 | 82.3 | 45 | 19 |
| Q04 | 73.9 | 72.9 | 33 | 17 |

### F-9. 화면 문구
※ KPI 문구는 카드 안의 글자를 줄바꿈 없이 이어 붙인 것(`textContent`)이라 띄어쓰기가 없습니다. 화면에서는 줄이 나뉘어 보입니다.

**결과 요약** (필터 없음, 샘플 모드)
- `lead`: 「대상 전체 · 평가 협력사 1,248개사 · 기준일 2026-11-09」
- 결론 1: 「평균 82.9점 — 전년 대비 ▲ 1.3점, 2022년 대비 ▲ 3.7점. 목표 85점 까지 2.1점」
- 결론 2: 「등급 구성 — A 17% (+3.0%p) · B 52% · C 30% · D 1.4% — 전년 대비 개선」
- 결론 3: 「가장 많이 오른 영역 대응(R) +1.8 · 가장 낮은 영역 원가(C) 76.9점 · 부진사 18개사 · 우수사 후보 198개사 (임시 기준)」
- KPI 1: 「평균 D/T 종합 점수82.9점▲ 1.3점 전년 대비2022~2026목표 85점까지 2.1점」
- KPI 2: 「A등급 (90점 이상)17%▲ 3.0%p 전년 대비2022~2026」
- KPI 3: 「C·D 등급 (80점 미만)31%▼ 6.2%p 전년 대비2022~2026」
- KPI 4: 「부진사 · 우수사 후보18 · 198개사임시 기준부진사 명단우수사 후보 명단」

**항목별 결과** (필터 없음)
- `lead`: 「가장 낮은 영역 원가(C) 76.9점 · 가장 많이 오른 영역 대응(R) +1.8 · 선택: 원가(C)」 — 기본 선택 영역 = `C`

**협력사별 결과** (필터 없음, 처음 열었을 때)
- 기본 선택 협력사: 협력사 0287 — D/T 89.4점, A → B, 전체 248위(상위 20%), 평가조직 3곳
- `lead`: 「1,248개사 · 목록 1,248개사 (전체) · 선택: 협력사 0287 B등급 89.4점 · 전체 248위」
- 결론 callout: 「B등급 89.4점 — 전년 A에서 1단계 하락. 전체 248위(상위 20%). 순위가 가장 높은 항목 기술(T) 51위, 가장 낮은 항목 재무(F) 635위.」

---

## 부록 G. 화면 참조 코드 (결과 요약 · 항목별 결과 · 협력사별 결과)

본문 §9 명세의 **정답 구현**입니다. 카드 id, 제목, 부제, 문구, 열 구성, 호출하는 계산식이 모두 들어 있습니다.

```js
/* =====================================================================
   7. 결과 요약 — 핵심 숫자 → ①등급 → ②5개년 추이 → ③항목별 증감 → ④변화 큰 업종·협력사 → ⑤부진사·우수사 후보
   ===================================================================== */
function buildReport() {
  const expand = h('button', { class:'btn sm', type:'button', id:'rp-expand', onclick: () => { state.rpAll = !state.rpAll; state.rpOpen.clear(); renderAll(); } }, '모두 펼치기');
  const PC = CONFIG.criteria.poor, EC = CONFIG.criteria.excellent;
  $('#page-report').replaceChildren(
    h('div', { class:'card rep-head', id:'rp-head' }),
    h('div', { class:'kpis k4', id:'rp-kpis' }),
    secHead(1, '등급 결과', `D/T 최종 등급 · ${CONFIG.year} vs ${CONFIG.prevYear}`),
    h('div', { class:'grid' }, card('rp-grade', 12, '등급별 협력사 수와 비율', null, { src:'[평가결과]·[전년도 결과] D/T 최종 등급 (1번)' })),
    secHead(2, '5개년 추이', `${YEARS[0]}~${CONFIG.year}년`),
    h('div', { class:'grid' },
      card('rp-trend', 6, '평균 D/T 종합 점수', '점선 = 목표', { table: true, src:'연도별 1번 파일 D/T 종합 점수' }),
      card('rp-gtrend', 6, '등급 구성', '연도별 비율', { table: true, src:'연도별 1번 파일 D/T 최종 등급' })),
    secHead(3, '항목별 점수 증감', '영역을 누르면 평가항목이 펼쳐집니다'),
    h('div', { class:'grid' }, card('rp-areas', 12, '영역 · 평가항목별 전년 · 올해 점수', null, { tools: expand, src:'{영역}-환산점수 (2번), 환산평점·이전 환산평점 (3번), 점수 항목 (1번)' })),
    secHead(4, '변화가 큰 업종 · 협력사', 'D/T 종합 점수 전년 대비'),
    h('div', { class:'grid' }, card('rp-ind', 12, '업종별 평균 점수 변화', '세부업종그룹 · 전년 대비 · 5개년 추이 · 누르면 필터 적용', { src:'세부업종그룹, D/T 종합 점수 (1번), 연도별 D/T 종합 점수' })),
    h('div', { class:'grid' },
      card('rp-up', 6, '점수 상승 협력사', '전년 대비 · 행을 누르면 협력사 상세', { src:'협력사명·코드, 평가조직, 세부업종그룹, D/T 종합 점수·등급, {영역}-환산점수 (1·2번)' }),
      card('rp-down', 6, '점수 하락 협력사', '전년 대비 · 행을 누르면 협력사 상세', { src:'협력사명·코드, 평가조직, 세부업종그룹, D/T 종합 점수·등급, {영역}-환산점수 (1·2번)' })),
    h('div', { class:'grid' },
      card('rp-ind2', 5, '업종(세부) 변화 상위 · 하위 5', '업종 단위 · 협력사 10개사 이상', { detail: true, src:'업종 (2번), D/T 종합 점수 (1번)' }),
      card('rp-org', 7, '평가조직별 결과', '평가조직 단위 평가 점수 · 등급 구성', { detail: true, src:'평가조직, 평가 점수, 평가조직 등급 (2번)' })),
    secHead(5, '부진사 · 우수사 후보', PC.fixed && EC.fixed ? '확정 기준' : '기준 확정 전 — 임시 기준'),
    h('div', { class:'grid' },
      card('rp-poor', 6, PC.name, null, { src:'D/T 최종 등급, D/T 종합 점수, 전년도 등급 (1번)' }),
      card('rp-exc', 6, EC.name, null, { src:'D/T 종합 점수, D/T 최종 등급, 등급 조정 대상, 거래중단예정일 (1·2번)' })));
}

function renderReport(L) {
  const n = L.length, T = CONFIG.targets, PC = CONFIG.criteria.poor, EC = CONFIG.criteria.excellent;
  const avgDt = avg(L, x => x.dtScore), avgPrev = avg(L, x => x.prev.dtScore);
  const gc = countBy(L, x => x.grade), gp = countBy(L, x => x.prev.grade);
  const share = (c, keys) => pctOf(keys.reduce((a, g) => a + (c[g] || 0), 0), n);
  const sa = share(gc, ['A']), saP = share(gp, ['A']), cd = share(gc, ['C','D']), cdP = share(gp, ['C','D']);   // sa = A등급 비율, cd = C·D 등급 비율
  const yAvg = yearAvg(L, t => t.dt);
  const yShare = keys => YEARS.map(y => { const v = L.filter(x => x.hist[y]); return v.length ? pctOf(v.filter(x => keys.includes(x.hist[y].grade)).length, v.length) : null; });
  const areasStat = CONFIG.areas.map(a => ({ a, prev: areaAvg(L, a.code, 'prevAreas'), cur: areaAvg(L, a.code), years: yearAvg(L, t => t.areas[a.code]) })).map(r => ({ ...r, d: r.cur - r.prev }));
  const poor = L.filter(x => critPass(PC, x)).sort((a, b) => a.dtScore - b.dtScore), exc = L.filter(x => critPass(EC, x)).sort((a, b) => b.dtScore - a.dtScore);
  const aUp = [...areasStat].sort((a, b) => b.d - a.d)[0], aLow = [...areasStat].sort((a, b) => a.cur - b.cur)[0];
  const d5 = yAvg[0] == null ? null : avgDt - yAvg[0], gap = T.avgScore - avgDt;
  setLead(`대상 ${filterText()} · 평가 협력사 ${fmt.n(n)}개사 · 기준일 2026-11-09`);

  // 머리 — 결론 3줄
  const better = sa > saP && cd <= cdP, worse = sa < saP && cd > cdP;
  $('#rp-head').replaceChildren(
    h('div', { class:'rep-title' },
      h('div', null, h('h2', null, `${CONFIG.year}년 협력사 종합평가 결과`), h('div', { class:'rep-meta' }, `대상: ${filterText()} · 평가 협력사 ${fmt.n(n)}개사 · 기준일 2026-11-09`)),
      h('div', { class:'tools no-print' }, h('button', { class:'btn primary', type:'button', onclick: () => window.print() }, '인쇄 · PDF 저장'))),
    h('ol', { class:'rep-sum' },
      h('li', null, '평균 ', h('b', null, `${fmt.sc(avgDt)}점`), ' — 전년 대비 ', delta(avgDt - avgPrev, '점'), d5 != null ? [`, ${YEARS[0]}년 대비 `, delta(d5, '점')] : '', `. 목표 ${T.avgScore}점 ${gap > 0 ? `까지 ${gap.toFixed(1)}점` : '달성'}`),
      h('li', null, '등급 구성 — A ', h('b', null, fmt.pct(sa)), ` (${fmt.sgn(sa - saP)}%p) · B ${fmt.pct(pctOf(gc.B || 0, n))} · C ${fmt.pct(pctOf(gc.C || 0, n))} · D ${fmt.pct(pctOf(gc.D || 0, n))} — 전년 대비 `, h('b', null, better ? '개선' : worse ? '악화' : '비슷')),
      h('li', null, '가장 많이 오른 영역 ', h('b', null, `${aname(aUp.a.code)} ${fmt.sgn(aUp.d)}`), ' · 가장 낮은 영역 ', h('b', null, `${aname(aLow.a.code)} ${fmt.sc(aLow.cur)}점`), ` · ${PC.name} `, h('b', null, `${fmt.n(poor.length)}개사`), ` · ${EC.name} `, h('b', null, `${fmt.n(exc.length)}개사`), PC.fixed && EC.fixed ? '' : h('span', { class:'muted' }, ' (임시 기준)'))));

  // 핵심 숫자 4개 (가장 중요한 평균 점수 강조, 모두 5개년 추이 포함)
  const sparkRow = (vals, txt, f = fmt.sc) => h('div', { class:'kpi-row' }, sparkline(vals, { fmtV: f, name: txt }), h('span', null, `${YEARS[0]}~${CONFIG.year}`));
  $('#rp-kpis').replaceChildren(
    kpi({ key: true, label:'평균 D/T 종합 점수', ic:'gauge', value: fmt.sc(avgDt), unit:'점', delta: delta(avgDt - avgPrev, '점', { suffix:'전년 대비' }), extra: [sparkRow(yAvg, '평균 점수'), h('div', { class:'kpi-row' }, gap > 0 ? `목표 ${T.avgScore}점까지 ${gap.toFixed(1)}점` : `목표 ${T.avgScore}점 달성`)] }),
    kpi({ label:`A등급 (${CONFIG.gradeCut.A}점 이상)`, ic:'star', value: fmt.pct(sa).replace('%', ''), unit:'%', delta: delta(sa - saP, '%p', { suffix:'전년 대비' }), extra: sparkRow(yShare(['A']), 'A등급 비율', fmt.pct) }),
    kpi({ label:`C·D 등급 (${CONFIG.gradeCut.B}점 미만)`, ic:'warn', value: fmt.pct(cd).replace('%', ''), unit:'%', delta: delta(cd - cdP, '%p', { goodUp: false, suffix:'전년 대비' }), extra: sparkRow(yShare(['C','D']), 'C·D 등급 비율', fmt.pct) }),
    kpi({ label:`${PC.name} · ${EC.name}`, ic:'adjust', value: `${fmt.n(poor.length)} · ${fmt.n(exc.length)}`, unit:'개사', delta: h('span', null, PC.fixed && EC.fixed ? '확정 기준' : '임시 기준'),
      action: h('div', { class:'kpi-row' }, link(`${PC.name} 명단`, () => openList('poor')), link(`${EC.name} 명단`, () => openList('exc'))) }));

  // ① 등급
  gradeLegend('rp-grade');
  segRows(body('rp-grade'), [{ label: String(CONFIG.year), counts: gc, total: n }, { label: String(CONFIG.prevYear), counts: gp, total: n }]);
  const cntCell = c => h('span', null, h('b', null, fmt.n(c)), h('span', { class:'muted' }, ` (${fmt.pct(pctOf(c, n))})`));
  body('rp-grade').append(h('div', { class:'tw' }, simpleTable([{ label:'등급' }, { label:'구분' }, { label:`${CONFIG.year} 개수 (비율)`, num: true }, { label:`${CONFIG.prevYear} 개수 (비율)`, num: true }, { label:'증감', num: true }],
    CONFIG.grades.map(g => [gradeChip(g), CONFIG.gradeGroup[g], cntCell(gc[g] || 0), cntCell(gp[g] || 0), delta((gc[g] || 0) - (gp[g] || 0), '개사', { goodUp: GI[g] <= 1, digits: 0 })]),
    { footer: ['합계', '', fmt.n(n), fmt.n(n), ''] })));
  foot('rp-grade', h('span', { class:'note' }, '증감 색: A·B 등급은 늘면 파랑, C·D 등급은 줄면 파랑'),
    csvBtn('내려받기', '등급분포.csv', ['등급','구분',`${CONFIG.year}`,`${CONFIG.year} 비율(%)`,`${CONFIG.prevYear}`,`${CONFIG.prevYear} 비율(%)`], () => CONFIG.grades.map(g => [g, CONFIG.gradeGroup[g], gc[g] || 0, pctOf(gc[g] || 0, n).toFixed(1), gp[g] || 0, pctOf(gp[g] || 0, n).toFixed(1)])));

  // ② 5개년 추이
  lineYears(body('rp-trend'), { series: [{ name:'평균 D/T 종합 점수', values: yAvg, color: P.accent, main: true }], bench: { value: T.avgScore, label:`목표 ${T.avgScore}` } });
  setTable('rp-trend', [{ label:'연도' }, { label:'평균 D/T 종합 점수', num: true }, { label:'평가 협력사', num: true }], YEARS.map((y, i) => [String(y), yAvg[i] == null ? '–' : fmt.sc(yAvg[i]), fmt.n(L.filter(x => x.hist[y]).length)]));
  gradeLegend('rp-gtrend');
  const yRows = YEARS.map(y => { const v = L.filter(x => x.hist[y]); return { label: String(y), counts: countBy(v, x => x.hist[y].grade), total: v.length }; });
  segRows(body('rp-gtrend'), yRows);
  const yA = yShare(['A']);
  body('rp-gtrend').append(callout(yA[4] >= yA[0] ? 'good' : 'bad', 'trend', [`A등급 비율 ${YEARS[0]}년 `, h('b', null, fmt.pct(yA[0])), ' → ', `${CONFIG.year}년 `, h('b', null, fmt.pct(yA[4]))]));
  setTable('rp-gtrend', [{ label:'연도' }, ...CONFIG.grades.map(g => ({ label: g, num: true })), { label:'협력사', num: true }], yRows.map(r => [r.label, ...CONFIG.grades.map(g => fmt.pct(pctOf(r.counts[g] || 0, r.total))), fmt.n(r.total)]));

  // ③ 항목별 증감 (영역 → 평가항목)
  $('#rp-expand').textContent = state.rpAll ? '모두 접기' : '모두 펼치기';
  const items = Object.fromEntries(CONFIG.areas.map(a => [a.code, itemStats(L, a.code)]));
  const maxA = Math.max(...areasStat.map(r => Math.abs(r.d)), ...Object.values(items).flat().map(it => Math.abs(it.value - it.prev)), 0.1);
  const IR = [['배점', x => x.max, x => x.prev.max], ['일반항목 평점', x => x.genRaw, x => x.prev.genRaw], ['일반항목 환산점수', x => x.gen, x => x.prev.gen], ['가산점', x => x.bonus, x => x.prev.bonus], ['평가 점수', x => x.score, x => x.prev.score], ['D/T 종합 점수', x => x.dtScore, x => x.prev.dtScore]]
    .map(([label, c, p]) => ({ label, cur: avg(L, c), prev: avg(L, p) })).map(r => ({ ...r, d: r.cur - r.prev }));
  body('rp-areas').replaceChildren(
    expandTable([{ label:'영역 / 평가항목' }, { label:'배점', num: true }, { label:'전년', num: true }, { label:'올해', num: true }, { label:'증감' }, { label:'5개년 추이' }],
      areasStat.map(r => ({ key: r.a.code, cells: [aname(r.a.code), String(r.a.max), fmt.sc(r.prev), h('b', null, fmt.sc(r.cur)), dchg(r.d, maxA), sparkline(r.years, { name: aname(r.a.code) })],
        subs: items[r.a.code].map(it => [it.name, fmt.sc(it.max), fmt.sc(it.prev), fmt.sc(it.value), dchg(it.value - it.prev, maxA), '']) })),
      { isOpen: k => state.detail || state.rpAll || state.rpOpen.has(k), onToggle: k => { if (state.rpOpen.has(k)) state.rpOpen.delete(k); else state.rpOpen.add(k); state.rpAll = false; renderAll(); } }),
    h('details', { class:'more', open: state.detail || null }, h('summary', null, '점수 구성 항목 (1번 파일) 전년 · 올해 보기'),
      h('div', { class:'tw', style:'margin-top:8px' }, simpleTable([{ label:'점수 항목' }, { label:'전년', num: true }, { label:'올해', num: true }, { label:'증감' }], IR.map(r => [r.label, fmt.sc(r.prev), fmt.sc(r.cur), dchg(r.d, Math.max(...IR.map(q => Math.abs(q.d)), 0.1))])))));
  foot('rp-areas', h('span', { class:'note' }, '전년 = 이전 환산평점 기준 · 미적용·무실적 제외 평균'),
    csvBtn('내려받기', '항목별_증감.csv', ['구분','영역/평가항목','배점','전년','올해','증감'], () => areasStat.flatMap(r => [['영역', aname(r.a.code), r.a.max, fmt.sc(r.prev), fmt.sc(r.cur), fmt.sc(r.d)], ...items[r.a.code].map(it => ['평가항목', it.name, fmt.sc(it.max), fmt.sc(it.prev), fmt.sc(it.value), fmt.sc(it.value - it.prev)])])));

  // ④ 업종 · 협력사 변화
  const gs = CONFIG.groups.map(g => { const gl = L.filter(x => x.group === g); return { key: g, n: gl.length, cur: avg(gl, x => x.dtScore), d: avg(gl, x => x.dtScore - x.prev.dtScore), years: yearAvg(gl, t => t.dt) }; }).filter(r => r.n).sort((a, b) => b.d - a.d);
  body('rp-ind').replaceChildren(h('div', { class:'gtiles' }, gs.map((r, i) => {
    const t = h('button', { class:'gtile', type:'button', 'aria-pressed': String(state.filters.group === r.key), onclick: () => applyFilter('group', state.filters.group === r.key ? '' : r.key) },
      h('span', { class:'nm' }, r.key, i === 0 ? h('span', { class:'tag good' }, '변화 최대') : i === gs.length - 1 && gs.length > 1 ? h('span', { class:'tag gray' }, '변화 최소') : null),
      h('span', { class:'v' }, delta(r.d, '점')), sparkline(r.years, { w: 110, name: r.key }),
      h('span', { class:'st' }, `평균 ${fmt.sc(r.cur)}점 · ${fmt.n(r.n)}개사`));
    t.setAttribute('aria-label', `${r.key} 전년 대비 ${fmt.sgn(r.d)}점, 평균 ${fmt.sc(r.cur)}점`);
    return t;
  })));
  foot('rp-ind', csvBtn('내려받기', '업종별_점수변화.csv', ['세부업종그룹','협력사 수','올해 평균','전년 대비', ...YEARS.map(y => `${y} 평균`)], () => gs.map(r => [r.key, r.n, fmt.sc(r.cur), fmt.sc(r.d), ...r.years.map(v => v == null ? '' : fmt.sc(v))])));
  const TOPN = state.detail ? 10 : 5, mv = L.map(x => ({ x, d: x.dtScore - x.prev.dtScore })), ups = [...mv].sort((a, b) => b.d - a.d).slice(0, TOPN), downs = [...mv].sort((a, b) => a.d - b.d).slice(0, TOPN);
  const maxM = Math.max(...ups.concat(downs).map(r => Math.abs(r.d)), 0.1);
  const mvCard = (id, list, label, sortKey) => {
    body(id).replaceChildren(h('div', { class:'tw' }, simpleTable([{ label:'협력사 · 가장 크게 변한 영역' }, { label:'전년 → 올해', num: true }, { label:'변화' }, { label:'등급' }],
      list.map(({ x, d }) => { const bm = bigAreaMove(x); return [supSub(x, bm.d ? `${aname(bm.a.code)} ${fmt.sgn(bm.d)}` : ''), `${fmt.sc(x.prev.dtScore)} → ${fmt.sc(x.dtScore)}`, dchg(d, maxM, '점', 56), gmove(x.prev.grade, x.grade)]; }),
      { onRow: i => openCompany(list[i].x.code) })));
    foot(id, link('협력사 목록에서 전체 보기', () => { state.list.sort = sortKey; openList('all'); }),
      csvBtn('내려받기', `점수${label}_TOP${TOPN}.csv`, ['협력사명','협력사 코드','평가조직','세부업종그룹','전년도 D/T 종합 점수','D/T 종합 점수','변화','전년도 등급','D/T 최종 등급'],
        () => list.map(({ x, d }) => [x.name, x.code, x.org, x.group, fmt.sc(x.prev.dtScore), fmt.sc(x.dtScore), fmt.sc(d), x.prev.grade, x.grade])));
  };
  mvCard('rp-up', ups, '상승', 'up'); mvCard('rp-down', downs, '하락', 'down');
  $('#rp-up .card-h h3').firstChild.textContent = `점수 상승 협력사 TOP ${TOPN}`; $('#rp-down .card-h h3').firstChild.textContent = `점수 하락 협력사 TOP ${TOPN}`;

  // ⑤ 부진사 · 우수사 후보
  const base = CONFIG.areas.map(a => areaAvg(L, a.code));
  const critCard = (id, c, list, weak) => {
    const top = list.slice(0, state.detail ? 20 : 5);
    body(id).replaceChildren(critLine(c),
      h('div', { class:'statrow' }, h('div', { class:'big' }, fmt.n(list.length), h('small', null, `개사 · 전체의 ${fmt.pct(pctOf(list.length, n))}`))),
      top.length ? h('div', { class:'tw' }, simpleTable([{ label:'협력사' }, { label:'점수', num: true }, { label:'등급' }, { label: weak ? '해당 기준' : '가장 강한 영역' }],
        top.map(x => { const g = areaGaps(x, base), s2 = g.reduce((m, r) => r.d > m.d ? r : m, g[0]);
          return [supSub(x), h('b', null, fmt.sc(x.dtScore)), gmove(x.prev.grade, x.grade), weak ? h('span', { class:'badges' }, c.rules.filter(r => r.test(x)).map(r => badge(r.label, 'bad'))) : (s2 ? `${aname(s2.a.code)} ${fmt.sc(s2.v)}` : '–')]; }),
        { onRow: i => openCompany(top[i].code) })) : h('p', { class:'note' }, '해당하는 협력사가 없습니다.'));
    foot(id, link(`전체 명단 ${fmt.n(list.length)}개사 보기`, () => openList(weak ? 'poor' : 'exc')),
      csvBtn('명단 내려받기', `${c.name}_명단.csv`, ['협력사명','협력사 코드','평가조직','세부업종그룹','D/T 종합 점수','전년도 D/T 종합 점수','전년도 등급','D/T 최종 등급','해당 기준'],
        () => list.map(x => [x.name, x.code, x.org, x.group, fmt.sc(x.dtScore), fmt.sc(x.prev.dtScore), x.prev.grade, x.grade, c.rules.filter(r => r.test(x)).map(r => r.label).join(' / ')])));
  };
  critCard('rp-poor', PC, poor, true);
  critCard('rp-exc', EC, exc, false);

  if (!state.detail) return;   // ── 상세 보기 ──
  const inds = [...new Set(L.map(x => x.industry))].map(k => { const il = L.filter(x => x.industry === k); return { key: k, group: il[0].group, n: il.length, cur: avg(il, x => x.dtScore), d: avg(il, x => x.dtScore - x.prev.dtScore) }; }).filter(r => r.n >= 10).sort((a, b) => b.d - a.d);
  const maxI2 = Math.max(...inds.map(r => Math.abs(r.d)), 0.1), indRow = r => [h('b', null, r.key), r.group, fmt.n(r.n), fmt.sc(r.cur), dchg(r.d, maxI2, '점', 64)];
  const sec = t => [h('span', { class:'tag gray', style:'margin:0' }, t), '', '', '', ''];
  body('rp-ind2').replaceChildren(inds.length ? h('div', { class:'tw' }, simpleTable([{ label:'업종' }, { label:'그룹' }, { label:'협력사', num: true }, { label:'올해', num: true }, { label:'전년 대비' }],
    [sec('변화 큰 업종 5'), ...inds.slice(0, 5).map(indRow), sec('변화 작은 업종 5'), ...inds.slice(-5).reverse().map(indRow)])) : h('p', { class:'note' }, '협력사 10개사 이상인 업종이 없습니다.'));
  const allEv = L.flatMap(x => x.evals.map(e => ({ e, x })));
  const orgs = CONFIG.orgs.map(o => { const ev = allEv.filter(r => r.e.org === o); const g = countBy(ev, r => r.e.grade); return { o, n: ev.length, v: avg(ev, r => r.e.score), d: avg(ev, r => r.e.score - r.x.prev.score), g, poor: ev.filter(r => critPass(PC, r.x)).length, exc: ev.filter(r => critPass(EC, r.x)).length }; }).filter(r => r.n);
  body('rp-org').replaceChildren(h('div', { class:'tw' }, simpleTable([{ label:'평가조직' }, { label:'협력사', num: true }, { label:'평균', num: true }, { label:'전년 대비', num: true }, { label:'등급 구성' }, { label: PC.name, num: true }, { label: EC.name, num: true }],
    orgs.map(r => [h('b', null, r.o), fmt.n(r.n), fmt.sc(r.v), delta(r.d), segBar(gradeParts(r.g)), fmt.n(r.poor), fmt.n(r.exc)]))));
}

/* =====================================================================
   8. 항목별 결과 — 영역 카드(5개년) → 선택 영역: 추이 · 평가항목 · 하위 협력사 (+상세: 항목 상세표 · 업종그룹 비교)
   ===================================================================== */
function buildArea() {
  $('#page-area').replaceChildren(
    h('div', { class:'atiles', id:'ar-tiles', role:'group', 'aria-label':'영역 선택' }),
    h('div', { id:'ar-sec' }),
    h('div', { class:'grid' },
      card('ar-trend', 4, '5개년 추이', '선택 영역 vs 전체 영역 평균', { table: true, src:'연도별 2번 파일 {영역}-환산점수' }),
      card('ar-items', 4, '평가항목별 점수', '점선 = 영역 평균 · 오른쪽 = 전년 대비', { table: true, src:'평가항목 코드·명, 환산평점, 이전 환산평점 (3번)' }),
      card('ar-low', 4, '하위 협력사 5', '행을 누르면 협력사 상세', { src:'{영역}-환산점수 (2번), D/T 최종 등급 (1번)' })),
    h('div', { class:'grid' },
      card('ar-detail', 7, '평가항목 상세표', '선택 영역의 모든 평가항목', { detail: true, src:'분류체계 유형, 배점, 환산평점, 이전 환산평점, 미적용 여부, 무실적 여부 (3번)' }),
      card('ar-group', 5, '업종그룹별 점수', '선택 영역 · 낮은 순', { detail: true, src:'세부업종그룹 (1번), {영역}-환산점수 (2번)' })));
}
function renderArea(L) {
  const st = CONFIG.areas.map(a => {
    const vals = L.map(x => x.areas[a.code].conv).filter(v => v != null);
    return { key: a.code, label: aname(a.code), max: a.max, cur: avg(vals, v => v), prev: areaAvg(L, a.code, 'prevAreas'), years: yearAvg(L, t => t.areas[a.code]), low: pctOf(vals.filter(v => v < 70).length, vals.length) };
  });
  const mean = avg(st, a => a.cur), byLow = [...st].sort((a, b) => a.cur - b.cur), byUp = [...st].sort((a, b) => (b.cur - b.prev) - (a.cur - a.prev));
  if (!state.area) state.area = byLow[0].key;
  const sel = st.find(a => a.key === state.area);
  setLead(`가장 낮은 영역 ${byLow[0].label} ${fmt.sc(byLow[0].cur)}점 · 가장 많이 오른 영역 ${byUp[0].label} ${fmt.sgn(byUp[0].cur - byUp[0].prev)} · 선택: ${sel.label}`);

  $('#ar-tiles').replaceChildren(...st.map(a => {
    const d = a.cur - mean, tone = d <= -2 ? 'bad' : '';
    const b = h('button', { class:'atile', type:'button', 'aria-pressed': String(a.key === sel.key), onclick: () => { state.area = a.key; renderAll(); } },
      h('span', { class:'nm' }, a.label, h('span', null, `배점 ${a.max}`)),
      h('span', { class:'v' }, fmt.sc(a.cur)), delta(a.cur - a.prev, '', { suffix:'전년 대비' }),
      sparkline(a.years, { w: 96, name: a.label }),
      h('span', { class:'st', style: tone ? 'color:var(--bad-text)' : 'color:var(--muted)' }, tone ? `평균보다 ${Math.abs(d).toFixed(1)} 낮음` : d >= 2 ? `평균보다 ${d.toFixed(1)} 높음` : '평균 수준'));
    b.setAttribute('aria-label', `${a.label} ${fmt.sc(a.cur)}점, 전년 대비 ${fmt.sgn(a.cur - a.prev)}`);
    return b;
  }));
  $('#ar-sec').replaceChildren(h('div', { class:'sec-sub' }, h('h2', null, `${sel.label} 상세`), h('p', null, '다른 영역은 위 카드를 눌러 선택')));

  const meanYears = YEARS.map((_, i) => avg(st.filter(a => a.years[i] != null), a => a.years[i]));
  lineYears(body('ar-trend'), { series: [{ name: sel.label, values: sel.years, color: P.accent, main: true }, { name:'전체 영역 평균', values: meanYears, color: P.prev }] });
  legend('ar-trend', [{ type:'line', color: P.accent, label: sel.label }, { type:'line', color: P.prev, label:'전체 영역 평균' }]);
  setTable('ar-trend', [{ label:'연도' }, { label: sel.label, num: true }, { label:'전체 영역 평균', num: true }], YEARS.map((y, i) => [String(y), sel.years[i] == null ? '–' : fmt.sc(sel.years[i]), fmt.sc(meanYears[i])]));

  const its = itemStats(L, sel.key), worst = [...its].sort((a, b) => a.value - b.value)[0];
  hbars(body('ar-items'), its.map(it => ({ key: it.code, label: it.name.replace(`${AREA[it.area].name} `, ''), value: it.value, tone: it.value <= sel.cur - 2 ? 'bad' : null, tag: it === worst && it.value <= sel.cur - 2 ? '최저' : null, extra: delta(it.value - it.prev), tip: [{ value:`${fmt.n(it.na)} · ${fmt.n(it.np)}건`, label:'미적용 · 무실적' }] })),
    { bench: { value: sel.cur, label:`평균 ${fmt.sc(sel.cur)}` }, lw: 116, ew: 56, tipLabel:'평균 환산평점' });
  setTable('ar-items', [{ label:'평가항목' }, { label:'평균', num: true }, { label:'전년', num: true }, { label:'증감', num: true }], its.map(it => [it.name, fmt.sc(it.value), fmt.sc(it.prev), fmt.sgn(it.value - it.prev)]));
  foot('ar-items', worst.value <= sel.cur - 2 ? callout('bad', 'warn', [h('b', null, worst.name), ` ${fmt.sc(worst.value)}점 — 가장 낮음`]) : h('p', { class:'note' }, '평가항목 간 차이가 크지 않습니다.'));

  const lowAll = L.filter(x => x.areas[sel.key].conv != null).sort((a, b) => a.areas[sel.key].conv - b.areas[sel.key].conv), low = lowAll.slice(0, 5), under70 = lowAll.filter(x => x.areas[sel.key].conv < 70);
  body('ar-low').replaceChildren(h('div', { class:'tw' }, simpleTable([{ label:'협력사' }, { label:`${sel.key}-환산점수` }, { label:'등급' }],
    low.map(x => [supSub(x), mcell(x.areas[sel.key].conv / 100, fmt.sc(x.areas[sel.key].conv), { tone: x.areas[sel.key].conv < 70 ? 'bad' : 'ctx' }), gradeChip(x.grade)]), { onRow: i => openCompany(low[i].code) })));
  foot('ar-low', h('span', { class:'note' }, `70점 미만 ${fmt.n(under70.length)}개사 (${fmt.pct(sel.low)})`),
    csvBtn('명단 내려받기', `${AREA[sel.key].name}_70점미만.csv`, ['협력사명','협력사 코드','평가조직','세부업종그룹',`${sel.key}-환산점수`,'이전 환산점수','D/T 최종 등급'],
      () => under70.map(x => [x.name, x.code, x.org, x.group, fmt.sc(x.areas[sel.key].conv), x.prevAreas[sel.key].conv == null ? '' : fmt.sc(x.prevAreas[sel.key].conv), x.grade])));

  if (!state.detail) return;   // ── 상세 보기 ──
  body('ar-detail').replaceChildren(h('div', { class:'tw' }, simpleTable([{ label:'코드' }, { label:'평가항목명' }, { label:'유형' }, { label:'배점', num: true }, { label:'평균', num: true }, { label:'전년', num: true }, { label:'증감', num: true }, { label:'70점 미만', num: true }, { label:'미적용', num: true }, { label:'무실적', num: true }],
    its.map(it => { const v = L.filter(x => !x.items[it.idx].na && !x.items[it.idx].np); return [it.code, it.name, it.classType, fmt.sc(it.max), h('b', null, fmt.sc(it.value)), fmt.sc(it.prev), delta(it.value - it.prev), fmt.pct(pctOf(v.filter(x => x.items[it.idx].r < 0.7).length, v.length)), fmt.n(it.na), fmt.n(it.np)]; }))));
  const grp = CONFIG.groups.map(g => { const gl = L.filter(x => x.group === g && x.areas[sel.key].conv != null); return { g, n: gl.length, v: avg(gl, x => x.areas[sel.key].conv), low: pctOf(gl.filter(x => x.areas[sel.key].conv < 70).length, gl.length) }; }).filter(r => r.n).sort((a, b) => a.v - b.v);
  body('ar-group').replaceChildren(h('div', { class:'tw' }, simpleTable([{ label:'세부업종그룹' }, { label:'점수', num: true }, { label:'영역 평균 대비', num: true }, { label:'70점 미만', num: true }, { label:'협력사', num: true }],
    grp.map(r => [h('b', null, r.g), fmt.sc(r.v), delta(r.v - sel.cur), fmt.pct(r.low), fmt.n(r.n)]))));
}

/* =====================================================================
   9. 협력사별 결과 — 목록(검색·칩·정렬) → 한눈에 보기 → 5개년 추이 · 항목별 점수와 순위(→ 평가항목 → 세부항목)
   ===================================================================== */
const SORTS = {
  score_desc:['D/T 종합 점수 높은 순', (a, b) => b.dtScore - a.dtScore], score_asc:['D/T 종합 점수 낮은 순', (a, b) => a.dtScore - b.dtScore],
  up:['점수 상승 큰 순', (a, b) => (b.dtScore - b.prev.dtScore) - (a.dtScore - a.prev.dtScore)], down:['점수 하락 큰 순', (a, b) => (a.dtScore - a.prev.dtScore) - (b.dtScore - b.prev.dtScore)],
  name:['협력사명 순', (a, b) => a.name.localeCompare(b.name)],
};
const PAGE_SIZE = 10;
function listFiltered(L) {
  const q = state.list.q.trim().toLowerCase();
  return L.filter(LIST[state.list.chip].f).filter(x => !q || x.name.toLowerCase().includes(q) || x.code.toLowerCase().includes(q)).sort(SORTS[state.list.sort][1]);
}
function subItems(x, i) {      // 4번 파일 형태의 가상 세부항목
  const r = mulberry32(x.idx * 131 + i * 7 + 1), k = 2 + Math.floor(r() * 3), c = ITEMS[i];
  return Array.from({ length: k }, (_, j) => { const t = Math.floor(r() * 4); return { code:`${c.code}-${j + 1}`, name:`세부항목 ${c.code}-${j + 1}`, value: t === 0 ? `${(80 + r() * 20).toFixed(1)}%` : t === 1 ? `${Math.floor(r() * 5)}건` : t === 2 ? `${(1 + r() * 9).toFixed(1)}일` : (r() < 0.85 ? 'Y' : 'N'), owner: ['협력사','평가조직','시스템'][Math.floor(r() * 3)] }; });
}
function buildCompany() {
  $('#page-company').replaceChildren(
    secHead(1, '협력사 목록', '검색 · 상태 칩으로 찾고, 행을 누르면 아래에 상세가 열립니다'),
    h('div', { class:'grid' }, card('co-list', 12, '협력사 결과', null, { src:'협력사명·코드, 평가조직, 세부업종그룹, D/T 종합 점수(연도별), D/T 최종 등급 (1·2번)' })),
    h('div', { id:'co-head' }),
    h('div', { class:'grid' }, card('co-sum', 12, '한눈에 보기', null, { src:'D/T 종합 점수, D/T 최종 등급, D/T 전년도 등급, G/T 종합 점수·등급, 평가 점수, 일반항목 환산점수, 가산점, 협력사 식별 항목 (1·2번)' })),
    h('div', { class:'grid' },
      card('co-trend', 4, '5개년 추이', '점 위 = 그해 등급 · 회색 = 전체 평균', { table: true, src:'연도별 1번 파일 D/T 종합 점수·D/T 최종 등급' }),
      card('co-rank', 8, '항목별 점수와 순위', '영역을 누르면 평가항목 순위, 평가항목을 누르면 세부항목', { src:'{영역}-환산점수 (2번), 평가항목 환산평점·이전 환산평점 (3번), 세부항목 (4번)' })));
  const sortSel = h('select', { id:'co-sort', 'aria-label':'정렬' }, Object.entries(SORTS).map(([v, [l]]) => h('option', { value: v }, l)));
  $('#co-list .chart-view').before(h('div', { class:'toolbar' },
    h('label', { class:'search' }, icon('search'), h('input', { id:'co-q', type:'search', placeholder:'협력사명 또는 코드 검색', autocomplete:'off', 'aria-label':'협력사 검색' })),
    sortSel, h('button', { class:'btn primary', type:'button', id:'co-csv' }, icon('download'), '목록 내려받기')), h('div', { id:'co-chips' }));
  let t;
  $('#co-q').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { state.list.q = e.target.value; state.list.page = 1; renderAll(); }, 180); });
  sortSel.addEventListener('change', e => { state.list.sort = e.target.value; state.list.page = 1; renderAll(); });
  $('#co-csv').addEventListener('click', () => {
    const list = listFiltered(filtered());
    downloadCSV(`협력사목록_${LIST[state.list.chip].label}.csv`, ['협력사명','협력사 코드','평가조직','권역명','세부업종그룹', ...YEARS.map(y => `${y} D/T 종합 점수`), '전년도 등급','D/T 최종 등급', ...CONFIG.areas.map(a => `${a.code}-환산점수`)],
      list.map(x => [x.name, x.code, x.org, x.region, x.group, ...YEARS.map(y => x.hist[y] ? fmt.sc(x.hist[y].dt) : ''), x.prev.grade, x.grade, ...CONFIG.areas.map(a => x.areas[a.code].conv == null ? '' : fmt.sc(x.areas[a.code].conv))]));
  });
}
function selectCompany(code, scroll) { state.company = code; state.coItem = null; state.coOpen.clear(); renderAll(); if (scroll) requestAnimationFrame(() => $('#co-head').scrollIntoView({ behavior:'smooth', block:'start' })); }

function renderCompany(L) {
  const base = CONFIG.areas.map(a => areaAvg(L, a.code));
  const rankDt = ranker(L.map(x => x.dtScore)), rankArea = Object.fromEntries(CONFIG.areas.map(a => [a.code, ranker(L.map(x => x.areas[a.code].conv))]));
  const rankItem = ITEMS.map((c, i) => ranker(L.map(x => x.items[i].na || x.items[i].np ? null : x.items[i].r)));
  const itemAvg = ITEMS.map((c, i) => avg(L.filter(o => !o.items[i].na && !o.items[i].np), o => o.items[i].r * 100));
  const list = listFiltered(L), pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
  state.list.page = clamp(state.list.page, 1, pages);
  if (!state.company || !BY_CODE.has(state.company)) state.company = (list.find(o => o.evals.length === 3 && o.move < 0) || list[0] || L[0]).code;
  const x = BY_CODE.get(state.company);

  // ① 목록
  $('#co-chips').replaceChildren(chipGroup(Object.entries(LIST).map(([v, o]) => ({ v, label: o.label, n: L.filter(o.f).length })), state.list.chip, v => { state.list.chip = v; state.list.page = 1; renderAll(); }, '상태로 거르기'));
  $('#co-sort').value = state.list.sort;
  if (document.activeElement !== $('#co-q')) $('#co-q').value = state.list.q;
  const rows = list.slice((state.list.page - 1) * PAGE_SIZE, state.list.page * PAGE_SIZE);
  body('co-list').replaceChildren(rows.length ? h('div', { class:'tw' }, simpleTable(
    [{ label:'순위', num: true }, { label:'협력사' }, { label:'D/T 종합 점수' }, { label:'전년 대비', num: true }, { label:'등급 (전년 → 당해)' }, { label:'5개년' }, { label:'비고' }],
    rows.map(o => [fmt.n(rankDt(o.dtScore).rank), supSub(o), mcell(o.dtScore / 100, fmt.sc(o.dtScore), { tone: GI[o.grade] >= 3 ? 'bad' : 'ctx' }), delta(o.dtScore - o.prev.dtScore), gmove(o.prev.grade, o.grade), sparkline(YEARS.map(y => o.hist[y] ? o.hist[y].dt : null), { name: o.name }), reasons(o)]),
    { onRow: i => selectCompany(rows[i].code, true), selected: rows.findIndex(o => o.code === x.code) }))
    : (() => { const q = state.list.q.trim().toLowerCase(), elsewhere = q ? L.filter(o => o.name.toLowerCase().includes(q) || o.code.toLowerCase().includes(q)).length : 0;
      return callout('', 'search', [`'${LIST[state.list.chip].label}'에는 해당 협력사가 없습니다.`, elsewhere ? [' 전체에서는 ', h('b', null, `${fmt.n(elsewhere)}개사`), '가 일치합니다.'] : ''], elsewhere ? link('전체에서 보기', () => { state.list.chip = 'all'; state.list.page = 1; renderAll(); }) : null); })());
  foot('co-list', h('span', { class:'note' }, '순위 = D/T 종합 점수 기준 (필터 적용 범위 안)'), pager(list.length, state.list.page, PAGE_SIZE, p => { state.list.page = p; renderAll(); }));

  // ② 상세 머리
  const at = list.findIndex(o => o.code === x.code);
  const nav = (txt, k) => h('button', { class:'btn sm', type:'button', disabled: at < 0 || !list[at + k] || null, onclick: () => selectCompany(list[at + k].code, false) }, txt);
  $('#co-head').replaceChildren(h('div', { class:'sec-h', style:'justify-content:space-between' },
    h('div', { style:'display:flex;gap:10px;align-items:baseline;flex-wrap:wrap' }, h('span', { class:'no' }, '2'), h('h2', null, `협력사 상세 — ${x.name}`), h('p', null, `${x.code} · 목록 ${at < 0 ? '밖' : `${at + 1}번째`}`)),
    h('div', { class:'tools' }, nav('‹ 이전 협력사', -1), nav('다음 협력사 ›', 1))));

  // 한눈에 보기 — 결론 한 줄 + 핵심 숫자 (상세 정보는 펼치기)
  const ranks = CONFIG.areas.map(a => ({ a, r: rankArea[a.code](x.areas[a.code].conv), v: x.areas[a.code].conv })).filter(o => o.r);
  const best = ranks.reduce((m, o) => o.r.rank < m.r.rank ? o : m, ranks[0]), worstR = ranks.reduce((m, o) => o.r.rank > m.r.rank ? o : m, ranks[0]);
  const rk = rankDt(x.dtScore), d5 = (() => { const f = YEARS.find(y => x.hist[y]); return f && f !== CONFIG.year ? { y: f, d: x.dtScore - x.hist[f].dt } : null; })();
  const moveTxt = x.move < 0 ? `전년 ${x.prev.grade}에서 ${-x.move}단계 하락` : x.move > 0 ? `전년 ${x.prev.grade}에서 ${x.move}단계 상승` : '전년과 같은 등급';
  const tone = x.move < 0 || GI[x.grade] >= 3 ? 'bad' : x.move > 0 ? 'good' : '';
  const field = (k, v) => h('div', null, h('dt', null, k), h('dd', { title: String(v) }, v));
  const step = (no, tt, ds, rv, hl) => h('li', { class: hl ? 'hl' : null }, h('span', { class:'no' }, no), h('div', { style:'min-width:0' }, h('div', { class:'tt' }, tt), h('div', { class:'ds' }, ds)), h('div', { class:'rv' }, rv));
  body('co-sum').replaceChildren(h('div', { class:'co-head' },
    h('div', { style:'display:flex;flex-direction:column;gap:10px;min-width:0' },
      h('div', { class:'co-name' }, x.name, badge(`${x.grade}등급 ${CONFIG.gradeGroup[x.grade]}`, GI[x.grade] <= 1 ? 'good' : GI[x.grade] === 2 ? 'warn' : 'bad'),
        critPass(CONFIG.criteria.poor, x) ? badge(CONFIG.criteria.poor.name, 'bad', 'warn') : null, critPass(CONFIG.criteria.excellent, x) ? badge(CONFIG.criteria.excellent.name, 'good', 'star') : null,
        x.adjTarget ? badge('등급 조정 대상', 'warn', 'adjust') : null, x.stopPlan ? badge(`거래중단 예정 ${x.stopPlan}`, 'bad', 'stop') : null),
      h('div', { class:'co-meta' }, [x.org + (x.evals.length > 1 ? ` 외 ${x.evals.length - 1}곳` : ''), `${x.region} · ${x.country}`, `${x.group} · ${x.industry}`, x.size].map(t2 => badge(t2))),
      callout(tone, tone === 'bad' ? 'warn' : 'bulb', [h('b', null, `${x.grade}등급 ${fmt.sc(x.dtScore)}점`), ` — ${moveTxt}. 전체 ${fmt.n(rk.rank)}위(${rankText(rk)}). `,
        '순위가 가장 높은 항목 ', h('b', null, `${aname(best.a.code)} ${fmt.n(best.r.rank)}위`), ', 가장 낮은 항목 ', h('b', null, `${aname(worstR.a.code)} ${fmt.n(worstR.r.rank)}위`), '.']),
      h('details', { class:'more', open: state.detail || null }, h('summary', null, '등급 산출 근거'), h('ol', { class:'flow', style:'margin-top:8px' },
        step(1, '평가조직별 평가', x.evals.map(e => `${e.org} ${fmt.sc(e.score)}점`).join(' · '), x.evals.map(e => gradeChip(e.grade))),
        step(2, '거래비중 반영', x.evals.map(e => `${e.org} ${fmt.pct(e.weight)}`).join(' + '), `Σ ${fmt.sc(sum(x.evals, e => e.weighted))}`),
        step(3, 'D/T 조정 전 등급', `A≥${CONFIG.gradeCut.A} · B≥${CONFIG.gradeCut.B} · C≥${CONFIG.gradeCut.C} · D<${CONFIG.gradeCut.C}`, gradeChip(x.preGrade)),
        step(4, '등급 조정', x.adjTarget ? '조정 대상 → 최종 등급 변경' : '조정 대상 아님', x.adjTarget ? badge('조정', 'warn', 'adjust') : badge('없음')),
        step(5, 'D/T 최종 등급 · G/T 등급', `G/T 종합 점수 ${fmt.sc(x.gtScore)}`, [gradeChip(x.grade), gradeChip(x.gtGrade)], true))),
      h('details', { class:'more', open: state.detail || null }, h('summary', null, '기본 정보 (코드 · 조직)'), h('dl', { class:'dl' },
        field('협력사 코드', x.code), field('대표코드', x.rep), field('D/T 코드', x.dt), field('G/T 코드', x.gt), field('일반 조직', x.generalOrg), field('평가조직', x.evals.map(e => e.org).join(', ')),
        field('평가단위', x.unit), field('세부 평가단위', `${x.subUnit} (${x.subUnitCode})`), field('권역', `${x.region} (${x.regionCode})`), field('내/외자', x.inout), field('주거래 · 금형', `${x.main} · ${x.mold}`), field('협력사 확인', x.confirmed)))),
    h('div', { style:'display:flex;flex-direction:column;gap:8px' },
      h('div', { class:'co-score' }, h('div', { class:'gbox' }, 'D/T 종합 점수', h('div', { class:'hero' }, fmt.sc(x.dtScore), h('small', null, '점'))),
        h('div', { class:'gbox' }, `${CONFIG.year}`, gradeChip(x.grade, true)), h('div', { class:'gbox' }, `${CONFIG.prevYear}`, gradeChip(x.prev.grade, true)), h('div', { class:'gbox' }, 'G/T', gradeChip(x.gtGrade, true))),
      h('div', { class:'kpi-row' }, delta(x.dtScore - x.prev.dtScore, '점', { suffix:'전년 대비' }), d5 ? h('span', null, ' · ', delta(d5.d, '점', { suffix:`${d5.y}년 대비` })) : null),
      h('div', { class:'kpi-row' }, rankCell(rk), h('span', null, `/ ${fmt.n(rk.total)}개사`)),
      h('div', { class:'kpi-row' }, `평가 점수 ${fmt.sc(x.score)} = 일반항목 환산점수 ${fmt.sc(x.gen)} + 가산점 ${fmt.sc(x.bonus)}`))));

  // 5개년 추이
  const yDt = YEARS.map(y => x.hist[y] ? x.hist[y].dt : null), yAll = yearAvg(L, t2 => t2.dt);
  legend('co-trend', [{ type:'line', color: P.accent, label: x.name }, { type:'line', color: P.prev, label:'전체 평균' }, { type:'dash', label:`A 기준 ${CONFIG.gradeCut.A}` }]);
  lineYears(body('co-trend'), { series: [{ name: x.name, values: yDt, color: P.accent, main: true }, { name:'전체 평균', values: yAll, color: P.prev }], bench: { value: CONFIG.gradeCut.A, label:`A 기준 ${CONFIG.gradeCut.A}` }, pointChip: i => x.hist[YEARS[i]] ? x.hist[YEARS[i]].grade : null });
  const yRank = YEARS.map(y => { const r = ranker(L.map(o => o.hist[y] ? o.hist[y].dt : null)); return x.hist[y] ? r(x.hist[y].dt) : null; });
  setTable('co-trend', [{ label:'연도' }, { label:'D/T 종합 점수', num: true }, { label:'등급' }, { label:'그해 순위', num: true }, { label:'전체 평균', num: true }],
    YEARS.map((y, i) => [String(y), yDt[i] == null ? '평가 없음' : fmt.sc(yDt[i]), x.hist[y] ? x.hist[y].grade : '–', yRank[i] ? `${fmt.n(yRank[i].rank)} / ${fmt.n(yRank[i].total)}` : '–', fmt.sc(yAll[i])]));

  // 항목별 점수와 순위 (→ 평가항목 순위 → 세부항목)
  const areaItems = Object.fromEntries(CONFIG.areas.map(a => [a.code, ITEMS.map((c, i) => ({ c, i })).filter(o => o.c.area === a.code)]));
  body('co-rank').replaceChildren(
    expandTable([{ label:'영역 / 평가항목' }, { label:'점수', num: true }, { label:'전체 평균', num: true }, { label:'순위' }, { label:'전년 대비', num: true }, { label:'5개년' }],
      ranks.map(o => ({ key: o.a.code,
        cells: [[aname(o.a.code), o === best ? h('span', { class:'tag good' }, '최고 순위') : o === worstR ? h('span', { class:'tag bad' }, '최저 순위') : null], h('b', null, fmt.sc(o.v)), fmt.sc(base[CONFIG.areas.indexOf(o.a)]), rankCell(o.r),
          x.prevAreas[o.a.code].conv == null ? '–' : delta(o.v - x.prevAreas[o.a.code].conv), sparkline(YEARS.map(y => x.hist[y] ? x.hist[y].areas[o.a.code] : null), { name: aname(o.a.code) })],
        subs: areaItems[o.a.code].map(({ c, i }) => { const it = x.items[i], off = it.na || it.np;
          return [[c.name, off ? h('span', { class:'tag gray' }, it.na ? '미적용' : '무실적') : null], off ? '–' : fmt.sc(it.r * 100), fmt.sc(itemAvg[i]), off ? '–' : rankCell(rankItem[i](it.r)), off ? '–' : delta((it.r - it.pr) * 100), '']; }) })),
      { isOpen: k => state.detail || state.coOpen.has(k), onToggle: k => { if (state.coOpen.has(k)) state.coOpen.delete(k); else state.coOpen.add(k); renderAll(); },
        onSub: (k, j) => { const idx = areaItems[k][j].i; state.coItem = state.coItem === idx ? null : idx; renderAll(); }, selSub: (k, j) => areaItems[k][j].i === state.coItem }));
  if (state.coItem == null && state.detail) state.coItem = areaItems[worstR.a.code][0].i;
  if (state.coItem != null) {
    const ci = ITEMS[state.coItem], cit = x.items[state.coItem], off = cit.na || cit.np;
    body('co-rank').append(h('div', { class:'subpanel' },
      h('div', { style:'display:flex;justify-content:space-between;align-items:center;gap:8px' }, h('b', null, `세부항목 — ${ci.name}`), h('button', { class:'btn sm', type:'button', onclick: () => { state.coItem = null; renderAll(); } }, '닫기')),
      h('div', { class:'kpi-row' }, `배점 ${fmt.sc(ci.max)} · 평점 ${off ? '–' : fmt.sc(ci.max * cit.r)} · 환산 평점 ${off ? '–' : fmt.sc(cit.r * 100)} · 전체 평균 ${fmt.sc(itemAvg[state.coItem])}`),
      off ? h('p', { class:'note' }, '배점 계산에서 제외된 항목입니다.') : h('div', { class:'sub-list' }, subItems(x, state.coItem).map(si => h('div', { class:'sub-item' }, h('span', { class:'n' }, si.name), h('span', { class:'v' }, si.value), h('span', { class:'m' }, `${si.code} · 세부 등록 주체: ${si.owner}`))))));
  }
  foot('co-rank', h('span', { class:'note' }, '순위 = 필터 적용 범위 안에서 높은 점수 순 · 상위 20% 파랑, 하위 20% 빨강'),
    csvBtn('이 협력사 항목 내려받기', `${x.name}_항목별순위.csv`, ['구분','영역/평가항목','점수','전체 평균','순위','대상 수','전년 대비'],
      () => ranks.flatMap(o => [['영역', aname(o.a.code), fmt.sc(o.v), fmt.sc(base[CONFIG.areas.indexOf(o.a)]), o.r.rank, o.r.total, x.prevAreas[o.a.code].conv == null ? '' : fmt.sc(o.v - x.prevAreas[o.a.code].conv)],
        ...areaItems[o.a.code].map(({ c, i }) => { const it = x.items[i], off = it.na || it.np, r = off ? null : rankItem[i](it.r); return ['평가항목', c.name, off ? '' : fmt.sc(it.r * 100), fmt.sc(itemAvg[i]), r ? r.rank : '', r ? r.total : '', off ? '' : fmt.sc((it.r - it.pr) * 100)]; })])));
  setLead(`${fmt.n(L.length)}개사 · 목록 ${fmt.n(list.length)}개사 (${LIST[state.list.chip].label}) · 선택: ${x.name} ${x.grade}등급 ${fmt.sc(x.dtScore)}점 · 전체 ${fmt.n(rk.rank)}위`);
}
```
