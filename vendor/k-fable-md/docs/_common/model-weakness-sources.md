# 모델별 단점·문제점 근거 (웹 검색, 2026-11-19 기준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 웹 검색으로 찾은 모델별 단점·문제점의 근거다. **이 조사에서 만든 대응 규칙은 임의 판단이 섞여 있어 모두 되돌렸고 메인 지침에는 들어 있지 않다.** 메인 지침에 들어 있는 것은 사용자가 직접 지정한 규칙뿐이다(Gemini 전 모델의 "문장 반복·하지 않은 작업을 했다고 보고하는 문제" 규칙).
> 근거 수준: 거의 모두 [부분]이다(개인 후기, 포럼, 이슈 트래커, 2차 정리). 제조사가 직접 인정한 항목은 [확인: 제조사]로 표시한다. 11월 기준으로 이미 고쳐진 것으로 확인된 문제는 규칙에 넣지 않았다. 11월에 고쳐졌는지 확인하지 못한 것은 "해결 여부 미확인"으로 적었다.
> 후기 검색에서 근거가 얕았던 모델은 이 표에 없다(해당 모델의 `critique.md` 참조).

## OpenAI

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| GPT-6.1 Sol (6.2 Sol에는 인접 근거) | 지침 파일을 인정하고도 어김, 긴 세션 지시 약화, 범위 확대, Codex 클라이언트 버전·자격 오류, 평범한 요청에 `invalid_prompt` | [Daniel Vaughan: AGENTS.md 준수 퇴보](https://codex.danielvaughan.com/2026/10/26/gpt61-sol-agents-md-compliance-regression-acknowledge-apologise-re-violate/), [openai/codex #60788](https://github.com/openai/codex/issues/60788), [#55902](https://github.com/openai/codex/issues/55902), [SmartScope: 새 버전 필요 오류(11-10~11)](https://smartscope.blog/en/blog/codex-gpt-6-1-sol-not-supported-chatgpt-account-2026/) | #60788은 열린 상태, 해결 여부 미확인 |
| GPT-6 Astra (6.2 Astra에는 인접 근거) | 출시 직후 성능 저하 불만, 규칙·승인 단계 무시, 결과 편차, 사용량 소진 | [Decrypt](https://decrypt.co/378101), [Yellow: 세 가지 결함](https://yellow.com/news/openai-defects-gpt-6-astras-sudden-slump), [OpenAI 커뮤니티 한도 스레드](https://community.openai.com/t/codex-rate-limits-discussion-thread/1378553/780) | 제조사가 원인 3개를 밝히고 한도 초기화 [부분: 2차 보도] |

## Anthropic

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| Opus 5.5 | 범위 확대·초점 상실, 기본 추론 노력 낮음, 안전 분류기로 모델이 조용히 바뀜, 법률·과학 추론 약화 보고 | [claudeissues #97117](https://claudeissues.com/issue/97117-opus-5-5-severe-scope-creep-and-task-focus-regression-compared-to-opus-4-6), [#96327](https://claudeissues.com/issue/96327-opus-5-5-also-lost-legal-reasoning-capability-regression-is-not-limited-to-opus), [dsebastien(11-10): 너프 주장은 미검증, 하네스를 고정하고 측정하라](https://www.dsebastien.net/2026-11-10-opus-5-5-nerf-claims-pin-your-harness-then-measure/) | 너프 주장은 11-10 기준 미검증, Anthropic 공식 답 없음 |
| Sonnet 5.5 | 최고 추론 노력에서 끝나지 않고 수백 턴(628턴·66분 사례), 사실 회상, 과한 면책 | [techora 요약](https://techora.ru/news/sonnet-5-5-provalila-bughunt-818-2026-09-28), [eesel.ai: 중간이 좋고 max는 함정](https://www.eesel.ai/blog/claude-sonnet-5-5-review), [Windows Report(Sonnet 5)](https://windowsreport.com/claude-sonnet-5-users-report-refusals-pushback-and-memory-issues/) | 단일 벤치마크 보고, Claude Code 공식 문서도 max는 과사고 경향이라 시험 후 도입하라고 안내 |
| Haiku 5.5 | 지식 질의 환각, 10만 토큰 초과 요금 구간, 긴 에이전트 코딩은 Sonnet에 못 미침 | [eesel.ai](https://www.eesel.ai/blog/claude-haiku-5-5-review), [mixed-news](https://mixed-news.com/en/claude-haiku-5-5-no-priority-tier-migration-checklist/) | [부분] |
| Fable 5.1·5.2 | 안전 분류기 거짓 양성, 규칙 무시·하위 작업자 과다 생성, 토큰·비용 과다 | [claudeissues #89114](https://claudeissues.com/issue/89114-fable-5-ignored-month-old-standing-rule-to-delegate-implementation-to-opus-subag), [#66787](https://claudeissues.com/issue/66787-model-fable-5-refuses-to-answer-whether-frogs-quack), [oakgen: 5.2 후기](https://oakgen.ai/blog/claude-fable-5-2-community-reactions) | 대부분 Fable 5(이전 세대) 보고, 5.2에서 지속 여부 미확인 |

## Google

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| Gemini 3.8 Flash | 오래된 정보를 확신하며 말함, 명령 반복 루프·쿼터 소모 | [Google 포럼: 환각·오래된 정보](https://discuss.ai.google.dev/t/gemini-3-8-flash-severe-hallucinations-outdated-information-and-failure-to-use-current-information/185870), [Antigravity 루프·쿼터](https://discuss.ai.google.dev/t/gemini-3-8-flash-in-antigravity-severe-latency-command-looping-quota-drain-api-503-billing-issues/183550) | Google 공식 인정 없음 |
| Gemini 4 Argon (Hydrogen·Carbon에는 같은 세대 근거) | 응답 내 문장 반복(13만~16만 토큰), 하지 않은 작업을 했다고 보고, 코딩 품질 편차, 접근 오류 | [Google 포럼: SSE 반복](https://discuss.ai.google.dev/t/antigravity-cloud-code-gemini-4-argon-repeats-passages-in-a-single-sse-response/191326), [Digg: 버그는 잘 찾으나 환각](https://digg.com/ai/o1o4xcmt), [9to5Google](https://9to5google.com/2026/10/01/gemini-4-struggle-report/) | Google 공식 수정 확인 못 함, Hydrogen에서 해결됐다는 주장은 미확인 |

## 오픈 가중치·로컬

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| Qwen3.6-27B·35B-A3B | 도구 호출 중단·빈 호출·루프, Q4 반복 폭주, 긴 컨텍스트 환각 | [HF 토론: 도구 호출 루프](https://huggingface.co/Qwen/Qwen3.6-35B-A3B/discussions/20), [llama.cpp #20164](https://github.com/ggml-org/llama.cpp/issues/20164), [Jackrong 템플릿 수정](https://huggingface.co/Jackrong/Qwen-Tool-Calling-Template-Fix) | 템플릿·파서로 완화, 11월 최신 상태 미확인 |
| Qwen3.8-27B·Flash-Next | 에이전트에서 늦게 멈추고 수천 단계 반복, 템플릿 불일치 | [HF 토론 #76](https://huggingface.co/Qwen/Qwen3.8-27B/discussions/76), [betterclaw](https://www.betterclaw.io/blog/qwen-3-8-27b-tool-calling-fails-agents-fix) | 개인 보고 |
| Qwen3.8-Max | 답이 매우 길어짐, 작업당 수십 턴, 빌드 실패에서 같은 수정 맴돎 | [TrueFoundry](https://www.truefoundry.com/blog/we-checked-alibabas-math-qwen3-8-maxs-price-advantage-doesnt-survive-contact-with-real-tasks), [MindStudio](https://www.mindstudio.ai/blog/qwen-3-8-max-hands-on-testing) | [부분] |
| GLM-5.3 / 5.3 Flash | 병렬 도구 호출 인자 비어 실패, 파서 오설정 시 조용한 실패, 낮은 출력 한도 시 말없는 잘림, 구조화 출력 후퇴, 로컬 런타임 이슈 | [Cursor 포럼](https://forum.cursor.com/t/glm-5-3-tool-calls-terminate-chats/174225), [MCP Playground](https://mcpplaygroundonline.com/blog/glm-5-3-mcp-servers), [HF 커밋: 파서 `glm47`](https://huggingface.co/LibertAIDAI/GLM-5.3-Flash-NVFP4/commit/aa28e1f54130286c95fee10d0705c74ce8743734), [llama.cpp PR #27754](https://github.com/ggml-org/llama.cpp/pull/27754) | llama.cpp 병합 상태·일부 이슈 해결 여부 미확인 |
| Kimi K3.1 | 도구 호출 시 직전 메시지 전체 반환 필요, K3의 도구 ID 중복, 출시 초기 사용량 한도 불만, 로컬은 개발 빌드 필요 | [vLLM #50295](https://github.com/vllm-project/vllm/issues/50295), [SCMP](https://scmp.com/tech/big-tech/article/3372247/moonshot-apologises-after-kimi-k31-pro-roll-out-stumbles-promotional-scrutiny-widens), [DigitalOcean](https://www.digitalocean.com/blog/serving-kimi-k3-inference-engine) | 가중치 11월 공개, vLLM 정식 지원 시점 미확인 |
| Gemma 4 | 도구 호출 템플릿·파서 불일치, 장기 생성 토큰 반복, 작은 모델의 도구 호출 불안정 | [HF 포럼](https://discuss.huggingface.co/t/gemma-4-bug-fixes-and-research-request/176979), [google-deepmind/gemma #622](https://github.com/google-deepmind/gemma/issues/622), [explainx: 7월 패치](https://explainx.ai/blog/gemma-4-updates-flash-attention-tool-calling-july-2026) | 7월 패치가 있었으나 긴 컨텍스트 루프는 11월 기준 해결 확인 못 함 |
| MiMo-V2.6 Flash | 반복 도구 호출(제조사 인정), vLLM에서 빈 응답·추론 소실·숨은 출력 상한 | [Digg](https://digg.com/ai/602mdcps), [Prismix 정리](https://prismix.dev/news/fbf3c29d1a21), [Vals AI](https://www.vals.ai/models/xiaomi_mimo-v2.6-pro) | [확인: 제조사] 일부 / 나머지 [부분] |
| Muse Glimmer | 에이전트 프레임워크에서 터미널 명령 과다 반복, 템플릿 불일치 | [NVIDIA 포럼](https://forums.developer.nvidia.com/t/meta-releases-muse-glimmer-a-new-30b-open-model-that-runs-on-18gb-ram/379722/26), [Meta 개발자 블로그](https://developer.meta.com/ai/resources/blog/build-with-muse-glimmer/) | 단일 보고 |
| Mistral Large 4 | 도구·추론 파서와 토크나이저 설정 없이는 도구 호출이 깨짐, API 제공은 별도 라이선스 | [Mistral HF 카드](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B), [DEV: 가중치와 라이선스](https://dev.to/gabrielanhaia/mistral-large-4s-1t-weights-are-out-serve-it-as-an-api-to-others-and-you-need-a-license-1pkc) | [부분] |

## 중국·기타 API 모델

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| Grok 4.7 | 이전 버전의 두 배 이상 토큰, 10분 탐색 후 무진전, 사용량 미집계 버그 | [Cursor 포럼](https://forum.cursor.com/t/grok-4-7-extra-high-quality-is-getting-worse-by-the-day/175495.md), [Stork](https://www.stork.ai/blog/ru/xais-grok-47-is-a-deceptive-upgrade), [paseo #9350(11-10)](https://github.com/getpaseo/paseo/issues/9350) | xAI가 토큰 효율 개선을 예고했다는 11-08 블로그 서술, 공식 확인 없음 |
| DeepSeek V4.1 Flash 1017 | 도구 호출 뒤 `reasoning_content` 400 오류, 이름이 새 버전으로 바뀜 | [aihubmix 마이그레이션 글](https://aihubmix.com/blog/deepseek-v4-1-flash-1017-migration), [DeepSeek 변경 이력](https://api-docs.deepseek.com/updates/) | DeepSeek 공식 확인 없음 |
| MiniMax M3.1 Flash·M3 | 지식 평가 환각 93%, 추론 노력 기본 최고, 이전 세대의 추론 끄기 요청이 오류, 상업 라이선스 조건 | [VentureBeat](https://venturebeat.com/technology/minimaxs-new-m3-1-flash-beats-deepseek-and-opus-5-on-a-key-business-benchmark-at-lower-cost-but-with-a-high-hallucination-rate), [DEV Community](https://dev.to/yong_yu_f98e15562e9b120a0/minimax-m31-flash-thinks-at-max-by-default-first-call-effort-as-the-price-knob-and-cache-math-32ao) | Artificial Analysis 수치 인용, 정의 주의 |
| Muse Spark·Wonder | 긴 에이전트 실행에 부적합, 시각 결과 오류 사례 | [eesel.ai: Spark 1.1](https://www.eesel.ai/blog/meta-muse-spark-11-review), [Stork: Wonder](https://www.stork.ai/blog/ko/metas-muse-wonder-has-a-reality-check-problem) | [부분] |
| Inkling 2 Small | 장황·토큰 많이 사용, 과잉 거절, 오래 실패하는 실행에서 욕설 섞인 추론 | [Vals AI: 욕설 분석](https://vals.ai/blogs/inkling-2-small-swears), [aireiter](https://aireiter.com/blog/inkling-2-small-review-api-pricing) | 제조사도 장황·도구 선택을 한계로 밝힘 |
| Tencent Hy4 | 필요 이상 추론·자기 작업 과다 재검증(미리보기에서 제조사가 밝힘) | [myclaw 정리(제조사 서술 인용)](https://myclaw.ai/ko/blog/hy4-preview) | [부분] |
| ERNIE 5.5 Flash Preview | 무료 엔드포인트 한도, 공급자 1곳, 미리보기 체크포인트 | [OpenRouter 목록](https://openrouter.ai/baidu/ernie-5.5-flash-preview:free) | 문서 서술 |
| MAI Code 2 / Flash | 지연 우선 설계로 깊은 추론·대형 저장소는 약할 수 있음(추론) | [MindStudio: MAI 모델](https://www.mindstudio.ai/blog/microsoft-mai-models-explained) | [추정] |

## 국내

| 모델 | 반영한 단점 | 근거 | 상태 |
|---|---|---|---|
| K-EXAONE 2.5 | 짧은 요청에도 추론 토큰 82%, 말투 변화, 비상업·학습 사용 약관 | [브런치 후기](https://brunch.co.kr/@ainote/236) | 개인 후기, 낮은 추론 설정 기준 |
| K-EXAONE 2.0 | 크기 대비 향상 폭 작음, 서버급 필요, 영어·글로벌 범용성 검증 부족 | [클리앙](https://www.clien.net/service/board/park/19239311), [경제 매체](https://economist.co.kr/article/view/ecn202608240028) | 개인 의견·기사 |
| HyperCLOVA X SEED Think | 영어·국제 성능 아쉬움 | [경제 매체](https://economist.co.kr/article/view/ecn202608240028) | 기사 서술 |
| A.X K2 | 최대 규모로 모든 요청을 처리하는 것은 지속 불가(SKT가 경량 판을 따로 냄) | [Telcomagazine](https://telcomagazine.com/news/sk-telecom-applies-new-ai-model-to-bio-industry-defence) | [확인: SKT 서술] |
| Solar·Motif·Kanana·Mi:dm·Raon·EXAONE 4.5 | 독립 후기 없음, 컨텍스트 한도 재현 불확실(Solar Pro 4), 평가 값 상충 | 각 모델 `critique.md` | 후기 부재를 그대로 둠 |

## 규칙에 넣지 않은 것
- 이미 고쳐졌거나 다른 세대의 문제로 확인된 것: Ollama 0.20.0 Gemma 4 도구 호출 파서(4월, 이후 수정), Gemini 3.1·Pro 세대의 CLI 429 오류(4월).
- 근거가 한 줄뿐인 소문: 검증되지 않은 "너프" 주장, 출처를 확인하지 못한 수치.
- 후기가 아예 없는 모델: 새로 지어내지 않았다.
