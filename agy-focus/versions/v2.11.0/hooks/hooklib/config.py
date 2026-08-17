from __future__ import annotations

import re
from pathlib import Path


CONFIG_ROOT = Path.home() / ".gemini" / "config" / "agy-focus"
STATE_ROOT = CONFIG_ROOT / "state"
STATE_FILE = STATE_ROOT / "last_state.json"
VERSION_FILE = CONFIG_ROOT / "current" / "VERSION"

RESEARCH_TRIGGER_RE = re.compile(
    r"(최신|latest|공식|official|검색|search|출처|source|검증|verify)"
    r".*(문서|docs?|찾|확인|research|검색|source|출처|검증|verify)"
    r"|(문서|docs?|찾|확인|research|검색|source|출처|검증|verify)"
    r".*(최신|latest|공식|official|검색|search|출처|source|검증|verify)",
    re.IGNORECASE,
)
CHANGE_TRIGGER_RE = re.compile(
    r"(?:\b(?:fix|add|build|make|create|implement|update|change|edit|refactor|"
    r"remove|write)\b|고쳐|수정|추가|만들어|구현|변경|작성|리팩터|삭제)",
    re.IGNORECASE,
)
WRITE_INTENT_RE = re.compile(
    r"(?:\b(?:fix|add|build|make|create|implement|update|change|edit|refactor|remove|write)\b|"
    r"고쳐|수정해|수정할|추가해|만들어|구현해|변경해|작성해|리팩터해|삭제해)",
    re.IGNORECASE,
)
READ_ONLY_TRIGGER_RE = re.compile(
    r"(?:\b(?:read[- ]?only|review[- ]?only|audit[- ]?only|diagnos(?:e|is)|inspect|review)\b|"
    r"읽기\s*전용|검토|진단|감사|분석|확인만|수정하지\s*(?:마|말고)|변경하지\s*(?:마|말고)|"
    r"절대\s+수정하지)",
    re.IGNORECASE,
)
ARCHITECTURE_TRIGGER_RE = re.compile(
    r"(?:\b(?:fix|bug|code|feature|implementation|refactor|architecture|god object|large file|"
    r"backend|frontend|class|controller|manager|store|service|model|viewmodel|"
    r"component|repository|pipeline|handler)\b|코드|오류|기능|구현|리팩터|구조|아키텍처|"
    r"대형 파일|책임 분리|백엔드|프론트엔드|클래스|컨트롤러|매니저|스토어|"
    r"서비스|모델|컴포넌트|리포지토리|파이프라인|핸들러)",
    re.IGNORECASE,
)
DOCUMENT_TASK_RE = re.compile(
    r"(?:\b(?:readme|docs?|documentation|changelog|markdown|copy|wording)\b|"
    r"리드미|문서|마크다운|변경 기록|카피|문구)",
    re.IGNORECASE,
)
DESIGN_TRIGGER_RE = re.compile(
    r"(?:\b(?:ui|ux|css|html|react|tailwind|frontend|landing|dashboard|component|"
    r"responsive|layout|swiftui|uikit|appkit|compose|flutter)\b|디자인|화면|페이지|"
    r"버튼|레이아웃|반응형|랜딩|대시보드|컴포넌트)",
    re.IGNORECASE,
)
COPY_TRIGGER_RE = re.compile(
    r"(?:\b(?:copywriting|microcopy|headline|button label|empty state|"
    r"error message|ui copy)\b|카피|문구|헤드라인|버튼 텍스트|오류 문구|빈 상태|"
    r"설명문)",
    re.IGNORECASE,
)
GTG_TRIGGER_RE = re.compile(r"(?:^|[\s;])/gtg\b|slashCommand;gtg", re.IGNORECASE)
STATIC_PAGE_RE = re.compile(
    r"(?:\b(?:website|webpage|landing page|static page)\b|웹\s*페이지|랜딩\s*페이지|정적\s*페이지)",
    re.IGNORECASE,
)
MULTI_PAGE_TRIGGER_RE = re.compile(
    r"(?:\b(?:multi[- ]?page|multiple pages?|separate pages?|routes?|site map|information architecture)\b|"
    r"다중\s*페이지|여러\s*페이지|페이지\s*구조|라우트|사이트\s*맵|정보\s*구조)",
    re.IGNORECASE,
)
INTERACTION_TRIGGER_RE = re.compile(
    r"(?:\b(?:interactive|interaction|filter|search|drag|drop|upload|editor|player|"
    r"animation|animate|copy button|command palette)\b|상호작용|인터랙션|필터|검색|"
    r"드래그|드롭|업로드|편집기|플레이어|애니메이션|복사 버튼|명령 팔레트)",
    re.IGNORECASE,
)
DARK_THEME_TRIGGER_RE = re.compile(
    r"(?:\b(?:dark theme|dark mode|terminal theme|developer docs theme)\b|"
    r"다크\s*(?:테마|모드)|어두운\s*(?:테마|화면)|터미널\s*(?:테마|미학))",
    re.IGNORECASE,
)
CATALOG_TRIGGER_RE = re.compile(
    r"(?:\b(?:table|catalog|matrix|inventory|reference manual)\b|"
    r"표로|표를|카탈로그|매트릭스|목록표|명세표)",
    re.IGNORECASE,
)
VERIFICATION_COMMAND_RE = re.compile(
    r"(?:\b(?:pytest|ctest|xctest|build|lint|check|typecheck|verify|audit|"
    r"playwright|vitest|jest|mocha|cypress|lighthouse|axe|html-validate|"
    r"http\.server|serve|curl)\b|npm\s+(?:test|run)|pnpm\s+(?:test|run)|"
    r"yarn\s+(?:test|run)|swift\s+(?:test|build)|xcodebuild|cargo\s+(?:test|check)|"
    r"go\s+test|cmake\s+--build)",
    re.IGNORECASE,
)
VISUAL_RENDER_COMMAND_RE = re.compile(
    r"(?:verify_ui_render\.py|\b(?:playwright|cypress|lighthouse|puppeteer)\b|"
    r"(?:google\s+chrome|chromium|chrome)(?:[^\n]{0,160})(?:--headless|--screenshot)|"
    r"--screenshot(?:=|\s)|screenshot\.(?:png|jpe?g|webp)|render(?:ed)?[^\n]{0,40}\.(?:png|jpe?g|webp))",
    re.IGNORECASE,
)

URL_RE = re.compile(r"https?://[^\s)\]}>]+", re.IGNORECASE)
PLACEHOLDER_EVIDENCE_RE = re.compile(
    r"(?:https?://(?:www\.)?(?:example\.(?:com|org|net)|foo\.bar|localhost|127\.0\.0\.1)"
    r"|https?://github\.com/(?:example/|user/repo|duration/easing|foo/bar)"
    r"|(?:github\.com/)?duration/easing(?:/|\b))",
    re.IGNORECASE,
)
ANTIGRAVITY_DOC_URL_RE = re.compile(
    r"https?://(?:www\.)?antigravity\.google/docs(?:/|[?#])", re.IGNORECASE
)
GEMINI_DOC_URL_RE = re.compile(
    r"https?://ai\.google\.dev/(?:gemini-api/)?docs(?:/|[?#])", re.IGNORECASE
)
OFFICIAL_UI_SOURCE_RE = re.compile(
    r"https?://(?:developer\.apple\.com/(?:design|videos|wwdc)|"
    r"developer\.android\.com/(?:design|develop|jetpack)|developer\.chrome\.com/(?:docs|blog)|"
    r"web\.dev/articles|(?:www\.)?w3\.org/(?:WAI|TR)|research\.google|"
    r"design\.google|fluent2\.microsoft\.design|atlassian\.design|"
    r"(?:s2\.)?spectrum\.adobe\.com|carbondesignsystem\.com|"
    r"polaris(?:-react)?\.shopify\.com|chi2026\.acm\.org|arxiv\.org)(?:[/?#]|$)",
    re.IGNORECASE,
)
ONE_TIME_STATE_KEYS = (
    "uiEvidenceConversationId",
    "designContextConversationId",
    "copyContextConversationId",
    "scopeIntakeConversationId",
    "architectureContextConversationId",
)

SENSITIVE_NAME_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\..*)?|\.npmrc|\.pypirc|\.netrc|"
    r"[^/]+\.(?:pem|key)|id_rsa|id_ed25519|"
    r"(?:credentials?|secrets?|tokens?|passwords?)\.(?:json|ya?ml|toml|txt))$",
    re.IGNORECASE,
)
SKIPPED_SCOPE_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "dist",
    ".next",
    ".gradle",
    "DerivedData",
}
COMMAND_WRITE_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:apply_patch|sed\s+-[^\n]*i|perl\s+-[^\n]*pi|"
    r"tee\b|touch\b|mkdir\b|cp\b|mv\b|rm\b|truncate\b|install\b|ln\b|"
    r"git\s+(?:apply|mv|rm)\b)|(?<!\d)>(?![>&])",
    re.IGNORECASE,
)
UNSUPPORTED_OFFICIAL_CLAIM_RE = re.compile(
    r"(?:\binspect\s+hooks\b|\bdecide\s+hooks\b|\btransform\s+hooks\b|"
    r"\bpython\s+sdk\b|google\.antigravity\.hooks(?:\.policy)?|"
    r"\bprogrammatic(?:\s+logic|\s+policy)\b|after[_\s]+model[_\s]+responses?\b|"
    r"before[_\s]+tool[_\s]+call\b|after[_\s]+model[_\s]+call\b|\bask_user\b|"
    r"\bcontinue_on_error\b|`?event`?\s*[:：]|antigravity\s+plugin\s+directory|"
    r"plugin\s+directory|mcp\s+server\s+definitions|alongside\s+skills\s*,?\s*rules)",
    re.IGNORECASE,
)

INSTRUCTION_NAMES = {"agents.md", "gemini.md", "claude.md", "skill.md"}
MANIFEST_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "poetry.lock",
    "cargo.toml",
    "cargo.lock",
    "go.mod",
    "go.sum",
    "package.swift",
    "cmakelists.txt",
    "makefile",
    "project.pbxproj",
    "dockerfile",
    "gemfile",
    "podfile",
    "rakefile",
    "justfile",
    "meson.build",
    "flake.nix",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
}
SOURCE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".swift", ".c", ".cc", ".cpp",
    ".h", ".hpp", ".m", ".mm", ".rs", ".go", ".java", ".kt", ".kts",
    ".rb", ".php", ".cs", ".scala", ".sh", ".bash", ".zsh", ".fish",
    ".sql", ".html", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
}
CONFIG_SUFFIXES = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".plist",
    ".xcconfig", ".entitlements",
}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".adoc"}
DOC_NAMES = {
    "readme",
    "changelog",
    "contributing",
    "code_of_conduct",
    "security",
    "support",
    "roadmap",
    "plan",
}
