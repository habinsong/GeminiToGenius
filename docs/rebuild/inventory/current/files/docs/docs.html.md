# `docs/docs.html`

- 형식: `100644`
- 바이트: 5057
- SHA-256: `48422dfac27c7378f5fd8b28fbea90cf0fb3859373e82597e5a23c62867d1827`
- 인코딩: `utf-8`

```
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GeminiToGenius — 규칙 상세 설명서</title>
  <meta name="description" content="로컬 실행 코어와 설치·검사·복구 방법을 설명합니다.">
  <link rel="stylesheet" href="styles.css">
</head>
<body>

  <!-- 01. Apple.com Global Frosted Navigation Bar -->
  <header class="apple-global-nav">
    <div class="apple-nav-inner">
      <a href="index.html" class="apple-nav-brand">
        <span>GeminiToGenius</span>
      </a>
      <nav aria-label="메인 메뉴">
        <ul class="apple-nav-links">
          <li><a href="index.html" class="apple-nav-link">개요</a></li>
          <li><a href="index.html#principles" class="apple-nav-link">핵심 약속</a></li>
          <li><a href="index.html#process" class="apple-nav-link">일하는 과정</a></li>
          <li><a href="docs.html" class="apple-nav-link active">설명서</a></li>
          <li><a href="changelog.html" class="apple-nav-link">기록</a></li>
          <li><a href="https://github.com/habinsong/GeminiToGenius" target="_blank" rel="noopener noreferrer" class="apple-nav-link">GitHub</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <!-- 02. Main Content Canvas -->
  <main class="apple-main">
    <section class="apple-hero">
      <span class="apple-tag">v3.0.0-alpha.1 설명서</span>
      <h1 class="apple-hero-headline">설치하고, 평소처럼 요청하세요.</h1>
      <p class="apple-hero-subhead">로컬 실행과 단일 실제 오류 수정 사례를 확인한 개발 버전입니다. 종료 후 자동 재개 실패를 보완했고, 짧은 실호스트 재검증에서 재개와 등록 검사 실행을 확인했습니다.</p>
    </section>
    <section>
      <div class="apple-section-header"><h2 class="apple-section-title">설치 범위를 선택합니다.</h2></div>
      <div class="apple-spec-group">
        <div class="apple-spec-row"><div class="apple-spec-label">Antigravity 전역</div><div class="apple-spec-content"><code>bash scripts/install.sh</code><p>사용자 규칙을 보존하고 GTG 플러그인 하나를 설치합니다.</p></div></div>
        <div class="apple-spec-row"><div class="apple-spec-label">프로젝트 한 곳</div><div class="apple-spec-content"><code>bash scripts/install.sh --workspace /absolute/project/path</code><p>지정한 프로젝트의 플러그인 폴더에 설치합니다.</p></div></div>
        <div class="apple-spec-row"><div class="apple-spec-label">Gemini CLI</div><div class="apple-spec-content"><code>bash scripts/install.sh --platform gemini-cli</code><p>Gemini CLI 고유의 확장 형식과 훅을 생성합니다.</p></div></div>
      </div>
    </section>
    <section>
      <div class="apple-section-header"><h2 class="apple-section-title">검사하고 되돌릴 수 있습니다.</h2></div>
      <div class="apple-spec-group">
        <div class="apple-spec-row"><div class="apple-spec-label">설치 검사</div><div class="apple-spec-content"><code>bash scripts/install.sh doctor</code><p>원문 해시와 실제 훅 진입점 실행을 확인합니다. 실제 호스트의 모델 호출 시험은 아닙니다.</p></div></div>
        <div class="apple-spec-row"><div class="apple-spec-label">제거와 복구</div><div class="apple-spec-content"><code>bash scripts/install.sh uninstall</code><p>삭제 대신 보존 경로로 옮깁니다. 출력된 실제 경로를 <code>restore --backup</code>에 전달해 복구합니다. 프로젝트 설치와 Gemini CLI에는 설치 때와 같은 옵션을 전달합니다.</p></div></div>
        <div class="apple-spec-row"><div class="apple-spec-label">현재 검증 범위</div><div class="apple-spec-content"><p>명령 실패·시간 초과·재시작·검증 후 변경·설치 실패 복구와 여러 작업공간의 계약을 검사합니다. 실제 초기 훅과 오류 수정은 단일 사례에서 확인했습니다. Antigravity 2.12.2에서 종료 후 재개와 등록 검사 실행도 확인했으며 장기 작업·다른 모델·폭넓은 품질 평가는 남아 있습니다.</p></div></div>
      </div>
      <p><a href="rebuild/README.md">개발 계획과 전체 코드 기록</a> · <a href="../README.md">상세 사용 안내</a></p>
    </section>
  </main>

  <!-- 03. Minimal Apple Footer -->
  <footer class="apple-footer">
    <div class="apple-footer-inner">
      <div>
        <strong>GeminiToGenius</strong> — MIT 라이선스로 누구나 자유롭게 사용하실 수 있습니다. (2026 habinsong)
      </div>
      <ul class="apple-footer-links">
        <li><a href="index.html">홈</a></li>
        <li><a href="docs.html">상세 설명서</a></li>
        <li><a href="changelog.html">업데이트 기록</a></li>
        <li><a href="https://github.com/habinsong/GeminiToGenius" target="_blank" rel="noopener noreferrer">GitHub</a></li>
      </ul>
    </div>
  </footer>

  <script src="main.js"></script>
</body>
</html>
```
