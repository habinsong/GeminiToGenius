# 규칙 목록 (정리본)

`ai-smell rules --format md`가 만든다. 직접 고치지 말고 `ai_smell/rules/`를 고친 뒤 다시 만든다.

| id | 언어 | 범주 | 등급 | 가중치 | 교정 | 설명 |
|---|---|---|---|---|---|---|
| `en.residue.opener` | en | 챗봇 잔재 | A | 1.0 | standard | Paragraph opens with a chatbot acknowledgement. |
| `en.residue.here-is-revised` | en | 챗봇 잔재 | A | 1.0 | standard | Meta sentence introducing the edited text. |
| `en.residue.hope-helps` | en | 챗봇 잔재 | A | 1.0 | standard | Chatbot sign-off. |
| `en.residue.let-me-know` | en | 챗봇 잔재 | A | 1.0 | standard | Offer of further help at the end. |
| `en.residue.happy-to-help` | en | 챗봇 잔재 | A | 1.0 | standard | Eager-to-help line. |
| `en.residue.apology` | en | 챗봇 잔재 | A | 1.0 | standard | Stock apology. |
| `en.residue.as-an-ai` | en | 챗봇 잔재 | A | 1.0 | standard | Model self-reference as a preamble. |
| `en.residue.no-opinions` | en | 챗봇 잔재 | A | 1.0 | - | Model limitation disclaimer. |
| `en.residue.cutoff` | en | 챗봇 잔재 | A | 1.0 | - | Knowledge-cutoff disclaimer. |
| `en.residue.generated-note` | en | 챗봇 잔재 | A | 1.0 | standard | Self-label line. |
| `en.sycophancy.praise` | en | 아첨·공치사 | A | 0.6 | standard | Praises the question before answering. |
| `en.sycophancy.right` | en | 아첨·공치사 | A | 0.6 | standard | Agreement opener that agrees before checking. |
| `en.placeholder.bracket` | en | 빈 자리표시자 | A | 0.8 | - | Template slot left unfilled. |
| `any.markup.utm` | any | 누출된 마크업 | A | 1.0 | safe | Chat tool tag in a URL. |
| `en.residue.signpost-polish` | en | 챗봇 잔재 | B | 1.0 | standard | Label line for the edited text. |
| `en.puffery.testament` | en | 의미 부풀리기 | B | 1.0 | - | Inflates a small fact into a symbol. |
| `en.puffery.vital-role` | en | 의미 부풀리기 | B | 1.0 | - | Importance asserted instead of shown. |
| `en.puffery.underscores` | en | 의미 부풀리기 | B | 1.0 | - | Sentence announces its own significance. |
| `en.puffery.tapestry` | en | 의미 부풀리기 | B | 1.0 | standard | Stock metaphor. |
| `en.puffery.todays-world` | en | 의미 부풀리기 | B | 1.0 | standard | Generic scene-setting opener. |
| `en.puffery.evolving-landscape` | en | 의미 부풀리기 | B | 1.0 | - | Stock phrase for change. |
| `en.puffery.navigate` | en | 의미 부풀리기 | B | 1.0 | standard | Navigation metaphor. |
| `en.puffery.beacon` | en | 의미 부풀리기 | C | 1.0 | - | Monument metaphor. |
| `en.puffery.paving` | en | 의미 부풀리기 | B | 1.0 | - | Stock phrase for 'enables'. |
| `en.puffery.unlock` | en | 의미 부풀리기 | B | 1.0 | standard | Stock phrase. |
| `en.puffery.game-changer` | en | 의미 부풀리기 | B | 1.0 | standard | Hype word. |
| `en.puffery.future-bright` | en | 의미 부풀리기 | B | 1.0 | - | Empty forward-looking close. |
| `en.puffery.only-time` | en | 의미 부풀리기 | C | 1.0 | - | Empty forward-looking close. |
| `en.puffery.lasting` | en | 의미 부풀리기 | C | 1.0 | - | Legacy cliche. |
| `en.puffery.travel` | en | 의미 부풀리기 | C | 1.0 | - | Brochure language. |
| `en.puffery.unwavering` | en | 의미 부풀리기 | B | 1.0 | - | Intensified abstraction. |
| `en.puffery.transformative` | en | 의미 부풀리기 | B | 1.0 | - | Hype phrase. |
| `en.puffery.new-era` | en | 의미 부풀리기 | B | 1.0 | - | Importance inflation. |
| `en.puffery.metaphor-of` | en | 의미 부풀리기 | C | 1.0 | - | Stock metaphor. |
| `en.puffery.realm` | en | 의미 부풀리기 | C | 1.0 | - | Abstract container; 'in' is enough. |
| `en.puffery.fragment-closer` | en | 의미 부풀리기 | B | 1.0 | - | Dramatic one-line closer. |
| `en.puffery.the-real` | en | 의미 부풀리기 | C | 1.0 | - | Staged reveal. |
| `en.puffery.honest-answer` | en | 의미 부풀리기 | C | 1.0 | - | Anecdotal tic reported for recent assistants; weak evidence. |
| `en.attribution.vague` | en | 출처 없는 권위 | B | 1.0 | - | Authority without a named source. |
| `en.signpost.lets-pure` | en | 예고·안내 | B | 0.8 | standard | Content-free announcement. |
| `en.signpost.lets` | en | 예고·안내 | B | 0.6 | - | Announces what will be done instead of doing it. |
| `en.signpost.in-this` | en | 예고·안내 | C | 0.8 | - | Table-of-contents sentence. |
| `en.signpost.stock` | en | 예고·안내 | C | 0.8 | - | Hook phrase. |
| `en.signpost.heres-the-thing` | en | 예고·안내 | B | 0.8 | strong | Staged run-up. |
| `en.signpost.the-x-question` | en | 예고·안내 | B | 0.8 | - | Self-posed question answered at once. |
| `en.signpost.question-opener` | en | 예고·안내 | C | 0.8 | - | Hook opening. |
| `en.signpost.whether` | en | 예고·안내 | B | 0.8 | - | 'Whether you're A or B' audience sweep. |
| `en.puffery.adds-depth` | en | 의미 부풀리기 | B | 1.0 | standard | Stock depth/nuance inflation. |
| `en.puffery.signal` | en | 의미 부풀리기 | B | 1.0 | standard | Stock signalling rhetoric. |
| `en.puffery.abstract-index` | en | 의미 부풀리기 | B | 1.0 | standard | Abstract metric jargon in prose. |
| `en.puffery.density` | en | 의미 부풀리기 | B | 1.0 | standard | Pretentious density phrasing. |
| `en.puffery.paradigm-shift` | en | 의미 부풀리기 | B | 1.0 | standard | Cliché buzzword for major change. |
| `en.structure.neg-parallel` | en | 구조 습관 | A | 1.2 | strong | Negative parallelism: knocks down a view nobody held, then states the point. |
| `en.structure.neg-parallel-noun` | en | 구조 습관 | A | 1.2 | - | Negative parallelism with a noun subject. |
| `en.structure.isnt-x-but-y` | en | 구조 습관 | B | 0.8 | - | 'isn't the X but the Y' contrast. |
| `en.structure.on-one-hand` | en | 구조 습관 | C | 0.5 | - | Balanced both-sides frame. |
| `en.structure.neg-parallel-about` | en | 구조 습관 | A | 1.2 | - | Negative parallelism ('isn't about X, it's about Y'). |
| `en.structure.not-only` | en | 구조 습관 | B | 0.25 | - | 'Not only X but also Y' frame (common in human prose; weak). |
| `en.structure.more-than-just` | en | 구조 습관 | B | 1.2 | - | Negative-parallel variant. |
| `en.structure.less-more` | en | 구조 습관 | B | 1.2 | - | Negative-parallel variant ('less about X, more about Y'). |
| `en.structure.no-no-just` | en | 구조 습관 | B | 1.2 | - | 'No X. No Y. Just Z.' triple. |
| `en.structure.not-a-but-a` | en | 구조 습관 | B | 1.2 | - | 'Not a X, but a Y' frame. |
| `en.structure.participial-tail` | en | 구조 습관 | B | 1.2 | strong | Tail clause that announces significance ('..., highlighting its importance'). |
| `en.structure.copula` | en | 구조 습관 | B | 1.2 | standard | Fancy verb where 'is' works. |
| `en.structure.boasts` | en | 구조 습관 | B | 1.2 | strong | 'Boasts' for 'has'. |
| `en.structure.considered` | en | 구조 습관 | C | 1.2 | - | Vague framing. |
| `en.structure.summary-open` | en | 구조 습관 | B | 0.6 | - | Paragraph restates what was just said. |
| `en.structure.summary-heading` | en | 구조 습관 | C | 0.4 | - | Template heading. |
| `en.structure.false-concession` | en | 구조 습관 | C | 1.2 | - | 'While X has limits, it is still great' frame. |
| `en.structure.false-range` | en | 구조 습관 | C | 1.2 | - | Range with no real scale. |
| `en.structure.staged-honest` | en | 구조 습관 | C | 1.2 | - | Staged candor. |
| `en.structure.paired-with` | en | 구조 습관 | B | 1.2 | standard | Overused coupling phrase. |
| `en.hedging.note-that` | en | 군더더기·유보 | B | 0.7 | standard | Throat-clearing before the actual statement. |
| `en.hedging.potentially` | en | 군더더기·유보 | B | 0.7 | standard | Stacked hedge. |
| `en.hedging.stock-lead` | en | 군더더기·유보 | C | 0.7 | strong | Filler lead-in. |
| `en.hedging.adverb-lead` | en | 군더더기·유보 | C | 0.5 | strong | Sentence adverb that comments on itself. |
| `en.hedging.that-said` | en | 군더더기·유보 | C | 0.4 | - | Stock concession opener. |
| `en.hedging.worth-ing` | en | 군더더기·유보 | B | 0.5 | - | Throat-clearing that points at the next point. |
| `en.hedging.when-it-comes` | en | 군더더기·유보 | C | 0.4 | - | Wordy topic marker; 'for' or 'with' is usually enough. |
| `en.hedging.arguably` | en | 군더더기·유보 | C | 0.4 | - | Weasel hedge. |
| `en.hedging.wordy` | en | 군더더기·유보 | C | 0.0 | standard | Wordier than the plain phrase (conciseness only; humans use these more often, so it is not scored). |
| `en.vocab.notably-lead` | en | 과다 어휘 | A | 0.8 | strong | Sentence adverb that comments on itself. |
| `en.vocab.delve` | en | 과다 어휘 | A | 0.8 | - | Peak 'LLM word' in academic prose. |
| `en.vocab.delve-into` | en | 과다 어휘 | A | 0.8 | standard | Peak 'LLM word' in academic prose. |
| `en.vocab.tapestry` | en | 과다 어휘 | A | 0.8 | - | Stock metaphor. |
| `en.vocab.showcase` | en | 과다 어휘 | A | 0.8 | - | Overused verb ('show'). |
| `en.vocab.showcase-fix` | en | 과다 어휘 | A | 0.8 | standard | Overused verb ('show'). |
| `en.vocab.underscore` | en | 과다 어휘 | A | 0.8 | - | Overused verb ('show', 'stress'). |
| `en.vocab.intricate` | en | 과다 어휘 | A | 0.8 | - | Overused adjective. |
| `en.vocab.pivotal` | en | 과다 어휘 | A | 0.8 | strong | Overused adjective ('key'). |
| `en.vocab.meticulous` | en | 과다 어휘 | A | 0.8 | - | Overused adjective. |
| `en.vocab.commendable` | en | 과다 어휘 | A | 0.8 | - | Overused adjective. |
| `en.vocab.notably` | en | 과다 어휘 | A | 0.5 | - | Overused sentence adverb. |
| `en.vocab.multifaceted` | en | 과다 어휘 | A | 0.8 | - | Overused adjective. |
| `en.vocab.crucial` | en | 과다 어휘 | B | 0.5 | - | Overused intensifier. |
| `en.vocab.comprehensive` | en | 과다 어휘 | B | 0.5 | - | Overused adjective. |
| `en.vocab.enhance` | en | 과다 어휘 | B | 0.5 | - | Overused verb. |
| `en.vocab.foster` | en | 과다 어휘 | B | 0.8 | - | Overused verb. |
| `en.vocab.garner` | en | 과다 어휘 | B | 0.8 | - | Overused verb ('get', 'win'). |
| `en.vocab.bolster` | en | 과다 어휘 | B | 0.8 | - | Overused verb ('strengthen'). |
| `en.vocab.elevate` | en | 과다 어휘 | B | 0.8 | - | Overused verb. |
| `en.vocab.streamline` | en | 과다 어휘 | B | 0.8 | - | Overused verb. |
| `en.vocab.revolutionize` | en | 과다 어휘 | B | 0.8 | - | Hype verb. |
| `en.vocab.leverage` | en | 과다 어휘 | B | 0.8 | - | Business jargon for 'use'. |
| `en.vocab.leverage-fix` | en | 과다 어휘 | B | 0.8 | standard | Business jargon for 'use'. |
| `en.vocab.utilize` | en | 과다 어휘 | C | 0.4 | standard | 'Use' is enough. |
| `en.vocab.commence` | en | 과다 어휘 | C | 0.4 | standard | 'Start' is enough. |
| `en.vocab.facilitate` | en | 과다 어휘 | B | 0.5 | - | Abstract verb. |
| `en.vocab.empower` | en | 과다 어휘 | B | 0.8 | - | Hype verb. |
| `en.vocab.unleash` | en | 과다 어휘 | B | 0.8 | - | Hype verb. |
| `en.vocab.embark` | en | 과다 어휘 | B | 0.8 | - | Journey metaphor. |
| `en.vocab.holistic` | en | 과다 어휘 | B | 0.8 | - | Abstract adjective. |
| `en.vocab.synergy` | en | 과다 어휘 | B | 0.8 | - | Business jargon. |
| `en.vocab.paradigm` | en | 과다 어휘 | C | 0.8 | - | Abstract noun. |
| `en.vocab.myriad` | en | 과다 어휘 | B | 0.8 | - | Grand quantity word ('many'). |
| `en.vocab.nuanced` | en | 과다 어휘 | C | 0.8 | - | Vague praise. |
| `en.vocab.robust` | en | 과다 어휘 | C | 0.8 | - | Vague praise. |
| `en.vocab.seamless` | en | 과다 어휘 | C | 0.8 | - | Vague praise. |
| `en.vocab.vibrant` | en | 과다 어휘 | C | 0.8 | - | Vague praise. |
| `en.vocab.groundbreaking` | en | 과다 어휘 | B | 0.8 | - | Hype adjective. |
| `en.vocab.invaluable` | en | 과다 어휘 | B | 0.8 | - | Superlative with no number behind it. |
| `en.vocab.interplay` | en | 과다 어휘 | B | 0.8 | - | Abstract noun. |
| `en.vocab.ecosystem` | en | 과다 어휘 | C | 0.5 | - | Abstract container noun. |
| `en.vocab.dynamic` | en | 과다 어휘 | C | 0.4 | - | Vague intensifier. |
| `en.vocab.era-2026` | en | 과다 어휘 | C | 0.5 | - | Reported as a recent assistant tic (anecdotal). |
| `en.vocab.gauge` | en | 과다 어휘 | B | 0.8 | standard | Abstract measuring metaphor ('gauge the impact'). |
| `en.vocab.propagate` | en | 과다 어휘 | B | 0.8 | standard | Pretentious spreading verb in prose. |
| `en.vocab.seamless-action` | en | 과다 어휘 | B | 0.8 | standard | Overused 'seamless' buzzword with verbs. |
| `en.vocab.automatically` | en | 과다 어휘 | B | 0.8 | standard | Unnecessary 'automatically' modifier. |
| `en.vocab.hardcode` | en | 과다 어휘 | B | 0.8 | standard | Slang verb for embedding or baking in. |
| `en.puffery.authority` | en | 의미 부풀리기 | B | 0.7 | - | Asserts depth or stakes instead of showing them. |
| `en.puffery.aphorism` | en | 의미 부풀리기 | C | 0.4 | - | Aphorism formula ('X is the language of Y'). |
| `en.puffery.closer-line` | en | 의미 부풀리기 | B | 0.8 | - | One-line closer that repeats the point. |
| `en.puffery.performed-insight` | en | 의미 부풀리기 | C | 0.5 | - | Announces profundity instead of delivering it. |
| `en.signpost.candor` | en | 예고·안내 | C | 0.45 | - | Narrates its own candor instead of disclosing. |
| `en.puffery.lingering` | en | 의미 부풀리기 | C | 0.5 | - | Unfalsifiable claim about the writer's own lingering attention. |
| `en.puffery.reaction` | en | 의미 부풀리기 | C | 0.25 | - | Stock reaction frame. Keep a real reaction; cut the empty frame. |
| `en.signpost.endorse` | en | 예고·안내 | C | 0.4 | - | Generic endorsement closer. |
| `en.signpost.no-one` | en | 예고·안내 | C | 0.4 | - | Answers an objection nobody raised. |
| `en.puffery.novelty` | en | 의미 부풀리기 | B | 0.6 | - | Claims scarcity of knowledge where none exists. |
| `en.puffery.self-label` | en | 의미 부풀리기 | C | 0.5 | - | Labels its own item as clever or surprising. |
| `en.signpost.reasoning` | en | 예고·안내 | B | 0.6 | - | Reasoning scaffold left in the prose. |
| `en.signpost.numbered` | en | 예고·안내 | C | 0.3 | - | Numbered list framing chosen for structure, not for the count of items. |
| `en.hedging.parenthetical` | en | 군더더기·유보 | C | 0.4 | - | Parenthetical aside that sounds nuanced without committing. |
| `en.signpost.fake-casual` | en | 예고·안내 | C | 0.3 | - | Props that stand in for a casual voice. |
| `en.puffery.launch` | en | 의미 부풀리기 | B | 0.6 | - | Launch-copy introduction. |
| `en.vocab.era-gpt6` | en | 과다 어휘 | C | 0.3 | - | Words reported for GPT-6-era output (Wikipedia, 2026); only counted in a cluster. |
| `en.opaque.the-noun` | en | 해독 부담 | C | 0.3 | - | A sentence opens with 'The <label>' for something the reader was never told about. |
| `en.opaque.file-ref` | en | 해독 부담 | C | 0.3 | - | Points at an internal notes file the reader may not have. |
| `en.opaque.arrow` | en | 해독 부담 | C | 0.25 | - | An arrow stands in for a verb or a causal link in running prose. |
| `en.opaque.inanimate-verb` | en | 해독 부담 | C | 0.4 | - | A thing does what only a person does ('the goal bites', 'modules sit on modules'). |
| `en.opaque.telegraphic` | en | 해독 부담 | C | 0.4 | - | A verbless run of fragments joined by semicolons (label-style shorthand). |
| `en.opaque.abstract-chain` | en | 해독 부담 | C | 0.3 | - | Three abstract nouns packed into one stretch of a sentence. |
| `en.opaque.vague-move` | en | 해독 부담 | C | 0.25 | - | 'The right move' names a choice without saying what it is. |
| `en.vocab.load-bearing` | en | 과다 어휘 | B | 0.6 | - | 'Load-bearing' as a general word for 'important' (reported as a Claude-family tic across several independent counts). |
| `en.vocab.claude-stock` | en | 과다 어휘 | C | 0.35 | - | Stock engineering metaphors that recent assistants reach for; each is fine alone and repeats across a text. |
| `en.signpost.pushback` | en | 예고·안내 | C | 0.5 | - | Combat framing for an ordinary statement. |
| `en.signpost.candor-plain` | en | 예고·안내 | C | 0.5 | - | Labels the next claim as plain or honest before making it. |
| `en.puffery.is-the-lever` | en | 의미 부풀리기 | C | 0.45 | - | Aphorism that names a single lever ('X is the unlock'). |
| `en.puffery.self-rank` | en | 의미 부풀리기 | C | 0.35 | - | Ranks its own claim instead of letting the reader judge. |
| `en.puffery.matters-because` | en | 의미 부풀리기 | C | 0.4 | - | Announces significance before giving the reason. |
| `ko.residue.opener` | ko | 챗봇 잔재 | A | 1.0 | standard | 챗봇식 수락 서두. |
| `ko.residue.hope-helps` | ko | 챗봇 잔재 | A | 1.0 | standard | 챗봇식 맺음 인사. |
| `ko.residue.ask-more` | ko | 챗봇 잔재 | A | 1.0 | standard | 더 도울 일을 묻는 맺음. |
| `ko.residue.anytime` | ko | 챗봇 잔재 | A | 1.0 | standard | '언제든 말씀하세요' 맺음. |
| `ko.residue.lead-in` | ko | 챗봇 잔재 | B | 1.0 | standard | 결과물 앞의 안내 문장. |
| `ko.residue.revised-label` | ko | 챗봇 잔재 | A | 1.0 | standard | 결과물 앞의 이름표 줄. |
| `ko.residue.as-ai` | ko | 챗봇 잔재 | A | 1.0 | - | 모델 자기소개. |
| `ko.residue.confusion` | ko | 챗봇 잔재 | A | 1.0 | standard | 판에 박힌 사과. |
| `ko.sycophancy.praise` | ko | 아첨·공치사 | A | 0.6 | standard | 질문을 칭찬하며 시작한다. |
| `ko.sycophancy.right` | ko | 아첨·공치사 | B | 0.6 | - | 확인하기 전에 먼저 동의한다. |
| `ko.sycophancy.apology-thanks` | ko | 아첨·공치사 | B | 0.3 | - | 사과와 감사가 한 글에 여러 번 겹친다. |
| `ko.placeholder.bracket` | ko | 빈 자리표시자 | A | 0.8 | - | 채우지 않은 자리표시자. |
| `ko.puffery.implication` | ko | 의미 부풀리기 | B | 1.0 | - | '시사하는 바가 크다': 무엇을 시사하는지 말하지 않는다. |
| `ko.puffery.noteworthy` | ko | 의미 부풀리기 | B | 1.0 | - | '주목할 만하다': 왜 주목할지 말하지 않는다. |
| `ko.puffery.key-role` | ko | 의미 부풀리기 | B | 1.0 | - | 중요하다고만 하고 무엇을 하는지 말하지 않는다. |
| `ko.puffery.cannot-stress` | ko | 의미 부풀리기 | B | 1.0 | - | 관용적 강조. |
| `ko.puffery.new-horizon` | ko | 의미 부풀리기 | B | 1.0 | - | 의미를 부풀리는 틀. |
| `ko.puffery.grand-background` | ko | 의미 부풀리기 | B | 1.0 | - | 서두의 거대한 배경. |
| `ko.puffery.importance-rises` | ko | 의미 부풀리기 | B | 1.0 | - | 중요성이 커진다는 말만 있다. |
| `ko.puffery.various` | ko | 의미 부풀리기 | C | 0.3 | - | '다양한 ~' 묶음. |
| `ko.puffery.overall` | ko | 의미 부풀리기 | C | 0.4 | - | 포괄 표현. |
| `ko.puffery.this-means` | ko | 의미 부풀리기 | C | 0.3 | - | '이는 ~를 의미한다' 해설. |
| `ko.puffery.future-close` | ko | 의미 부풀리기 | C | 1.0 | - | 빈 전망 맺음. |
| `ko.puffery.meaning` | ko | 의미 부풀리기 | B | 0.6 | - | 의미가 크다고만 하고 내용이 없다. |
| `ko.puffery.precious` | ko | 의미 부풀리기 | C | 0.3 | - | 정형 수식. |
| `ko.puffery.honestly` | ko | 의미 부풀리기 | C | 0.4 | - | 연출된 솔직함. |
| `ko.puffery.one-step` | ko | 의미 부풀리기 | C | 1.0 | - | 상투 연결. |
| `ko.puffery.deohada` | ko | 의미 부풀리기 | B | 0.7 | standard | '~를 더하다': 깊이·가치·매력 등 추상 명사에 '더하다'를 붙이는 상투구. |
| `ko.puffery.jisu` | ko | 의미 부풀리기 | B | 0.6 | standard | '~지수': 추상적 대상에 '지수(index)'를 붙여 객관성을 가장하는 표현. |
| `ko.puffery.mildo` | ko | 의미 부풀리기 | B | 0.6 | standard | '밀도': 깊이나 짜임새를 '밀도(density)'로 은유하는 상투적 표현. |
| `ko.signpost.announce` | ko | 예고·안내 | B | 0.8 | strong | 하겠다는 예고. 하지 않고 말만 한다. |
| `ko.signpost.lets` | ko | 예고·안내 | B | 0.8 | strong | 권유형 예고. |
| `ko.signpost.qa` | ko | 예고·안내 | C | 0.8 | - | 스스로 묻고 바로 답하는 틀. |
| `ko.structure.neg-simple` | ko | 구조 습관 | B | 1.2 | strong | '단순한 A가 아니라 B': 없던 오해를 세우고 부정한다. |
| `ko.structure.neg-general` | ko | 구조 습관 | B | 0.9 | - | 'A가 아니라 B' 대구. |
| `ko.structure.neg-chain` | ko | 구조 습관 | B | 1.2 | - | 부정을 연달아 쌓고 결론을 낸다. |
| `ko.structure.disclaimer-pair` | ko | 구조 습관 | B | 0.5 | - | 한 문장 안에 부정을 둘 맞세워 쌓는다('~을 보장하지 않고, ~을 뜻하지도 않는다'). 면책 문구가 대구로 짜인다. |
| `ko.structure.ji-pair` | ko | 구조 습관 | C | 0.35 | - | 한 문장에 '~는지'가 겹친다('자연스러운지 맞는지'). 같은 어미가 되풀이돼 기계적으로 읽힌다. |
| `ko.structure.bare-either` | ko | 구조 습관 | C | 0.35 | - | 주어 없이 '낮든 높든'으로 시작한다. 무엇이 낮고 높은지 말하지 않는 상관 표현이다. |
| `ko.structure.negation-pile` | ko | 구조 습관 | C | 0.3 | - | '~하지 않는다', '~이 아니다'로 끝나는 말이 한 글에 되풀이된다. 이 글이 무엇인지 말하지 않고 아닌 것만 쌓는다. |
| `ko.structure.not-only` | ko | 구조 습관 | C | 0.3 | - | '~뿐만 아니라' 병렬. |
| `ko.structure.beyond` | ko | 구조 습관 | B | 0.8 | - | '~를 넘어 ~로' 확장 틀. |
| `ko.structure.on-one-hand` | ko | 구조 습관 | C | 0.5 | - | 양면을 나란히 세우는 틀. |
| `ko.structure.rather` | ko | 구조 습관 | C | 0.5 | - | 대구의 변종. |
| `ko.structure.postposed` | ko | 구조 습관 | C | 0.4 | - | 서술어 뒤에 부사를 붙이는 도치('했다, 조용히.'). |
| `ko.structure.cleft` | ko | 구조 습관 | C | 0.5 | - | 강조 도입. 한 글에 한 번 이하. |
| `ko.structure.enumerate` | ko | 구조 습관 | C | 0.5 | - | '첫째, 둘째' 기계 나열. |
| `ko.structure.summary-open` | ko | 구조 습관 | B | 0.6 | - | 앞 내용을 되풀이하는 맺음 문단. |
| `ko.hedging.rago` | ko | 군더더기·유보 | B | 0.6 | strong | '~라고 할 수 있다' 유보. |
| `ko.hedging.dago` | ko | 군더더기·유보 | B | 0.6 | strong | '~다고 할 수 있다' 유보. |
| `ko.hedging.should` | ko | 군더더기·유보 | B | 0.6 | - | 당위 서술 반복. |
| `ko.hedging.importance-sentence` | ko | 군더더기·유보 | C | 0.5 | - | '~하는 것이 중요하다' 결론. |
| `ko.hedging.can-do` | ko | 군더더기·유보 | C | 0.4 | standard | '~하는 것이 가능하다'는 '~할 수 있다'로 충분하다. |
| `ko.hedging.nominal-verb` | ko | 군더더기·유보 | C | 0.4 | standard | 명사 + 만능 동사. 동사 하나로 줄인다. |
| `ko.trans.daehan` | ko | 번역투 | C | 0.25 | - | '~에 대해/대한' 번역투. |
| `ko.trans.isseo` | ko | 번역투 | C | 0.4 | - | '~에 있어서' 번역투. |
| `ko.trans.euihae` | ko | 번역투 | C | 0.3 | - | '~에 의해' 번역투. |
| `ko.trans.inhae` | ko | 번역투 | C | 0.3 | - | '~로 인해' 번역투. |
| `ko.trans.tonghae` | ko | 참고(점수 제외) | C | 0.0 | - | '~를 통해'. 사람 글에서 오히려 더 많이 나와 점수에 넣지 않는다. |
| `ko.trans.geosida` | ko | 참고(점수 제외) | C | 0.0 | - | '~것이다'. 사람 글에서 오히려 더 많이 나와 점수에 넣지 않는다. |
| `ko.trans.double-passive-doe` | ko | 번역투 | C | 0.4 | standard | '되어지다'. 비문으로 단정하지는 않지만 '되다'가 읽기 쉽다. |
| `ko.trans.double-passive` | ko | 번역투 | C | 0.4 | standard | '-어지다'가 겹친 피동. 비문으로 단정하지는 않지만 단순형이 읽기 쉽다. |
| `ko.trans.such-as` | ko | 번역투 | C | 0.25 | - | '~와 같은' (such as) 번역투. |
| `ko.trans.in-order` | ko | 번역투 | C | 0.3 | - | '~하기 위해서는', '~하는 데 있어' 번역투. |
| `ko.trans.demonstrative` | ko | 참고(점수 제외) | C | 0.0 | - | '이러한' 지시어 반복. 참고용이다. |
| `ko.trans.gajigo` | ko | 번역투 | C | 0.3 | - | '가지고 있다' 번역투. |
| `ko.trans.one-of` | ko | 번역투 | C | 0.3 | - | '~중 하나' 번역투. |
| `ko.trans.case` | ko | 번역투 | C | 0.2 | - | '~의 경우' 반복. |
| `ko.trans.jeok` | ko | 번역투 | C | 0.12 | - | '~적' 체인. |
| `ko.trans.jaeda` | ko | 번역투 | B | 0.7 | standard | '재다': 물리적 길이가 아닌 추상적 격차·비용·오류율·수치를 '재다'로 표현한 번역투. |
| `ko.trans.jaeboda` | ko | 번역투 | B | 0.6 | - | '재 보다'. 값을 매기거나 비교한 일을 '재 본다'로 말하는 번역투. '재 보니', '재 보지 않았다' 모두 같다. |
| `ko.trans.jeonpa` | ko | 번역투 | B | 0.6 | standard | '전파하다/전파되다': 확산·전달·공유를 기계적으로 '전파(propagate/disseminate)'로 쓴 번역투. |
| `ko.trans.jadong` | ko | 번역투 | B | 0.5 | standard | '자동으로': '스스로'나 '알아서'로 충분한 자리에 'automatically'를 직역한 표현. |
| `ko.vocab.sino-b` | ko | 과다 어휘 | B | 0.5 | - | 한자어 학술 동사. 2018→2026년 논문 초록에서 급증한 계열(arXiv 2609.07447). |
| `ko.vocab.sino-c` | ko | 과다 어휘 | C | 0.4 | - | 한자어 동사 묶음. |
| `ko.vocab.eval-b` | ko | 과다 어휘 | B | 0.7 | - | 평가 형용사. 숫자와 비교 대상 없이 칭찬만 한다. |
| `ko.vocab.eval-c` | ko | 과다 어휘 | C | 0.4 | - | 평가 형용사. |
| `ko.vocab.jjak` | ko | 과다 어휘 | B | 0.7 | standard | '짝'/'짝짓다': 둘의 대응이나 연계를 인위적으로 '짝'으로 표현한 번역투. |
| `ko.vocab.ssang` | ko | 과다 어휘 | B | 0.6 | standard | '쌍을 이루다': 둘의 병렬·대응을 상투적으로 표현한 어구. |
| `ko.vocab.sinho` | ko | 과다 어휘 | B | 0.6 | standard | '신호': 징후·단서·특징을 '신호(signal)'로 직역한 번역투. |
| `ko.vocab.bakda` | ko | 과다 어휘 | B | 0.6 | standard | '박다/박아 넣다': 거칠거나 비격식적인 삽입·하드코딩 표현 상투구. |
| `ko.figure.lens` | ko | 과다 어휘 | C | 0.4 | - | '렌즈'로 관점을 가리킨다. |
| `ko.figure.axis` | ko | 과다 어휘 | C | 0.35 | - | '축'으로 갈래를 셈한다. |
| `ko.figure.layer` | ko | 과다 어휘 | C | 0.35 | - | '겹', '층위'로 의미를 쌓아 놓는다. |
| `ko.figure.weight` | ko | 과다 어휘 | C | 0.4 | - | '~의 무게'로 중요함이나 부담을 가리킨다. |
| `ko.figure.temperature` | ko | 과다 어휘 | C | 0.35 | - | '온도'로 분위기를 가리킨다. |
| `ko.figure.landscape` | ko | 과다 어휘 | C | 0.35 | - | '풍경', '지형'으로 상황 전체를 가리킨다. |
| `ko.figure.guide` | ko | 과다 어휘 | C | 0.4 | - | 길잡이 도구에 빗댄다. |
| `ko.figure.journey` | ko | 과다 어휘 | C | 0.35 | - | '여정', '궤적'으로 과정을 가리킨다. |
| `ko.figure.pillar` | ko | 과다 어휘 | C | 0.4 | - | 구조물에 빗댄 말. |
| `ko.figure.weave` | ko | 과다 어휘 | B | 0.6 | - | 직물에 빗댄 말. |
| `ko.figure.joint` | ko | 과다 어휘 | C | 0.35 | - | 이음매, 천장, 모서리 같은 건축 용어로 추상을 가리킨다. |
| `ko.figure.resonance` | ko | 과다 어휘 | B | 0.5 | - | 공명, 숨결, 여백을 글 바깥의 감각에 빗대어 쓴다. |
| `ko.figure.hold` | ko | 과다 어휘 | C | 0.3 | - | 쥐다, 붙들다, 떠받치다, 얹다를 추상에 쓴다. |
| `ko.figure.draw` | ko | 과다 어휘 | B | 0.55 | - | 시적인 동사를 설명문에 쓴다. |
| `ko.figure.grammar-of` | ko | 과다 어휘 | C | 0.35 | - | 문법, 역학, 서사로 흐름을 추상화한다. |
| `ko.figure.unlock` | ko | 과다 어휘 | B | 0.55 | - | 잠금 해제, 살아 숨 쉬는, 온기 같은 말을 데이터나 능력에 붙인다. |
| `ko.figure.felt-fact` | ko | 과다 어휘 | C | 0.4 | - | 수치나 분석에 체감 형용사를 붙인다. |
| `ko.figure.hedge-verb` | ko | 과다 어휘 | C | 0.35 | - | 탐구하다, 형성하다 같은 거창한 동사. |
| `ko.collocate.build` | ko | 과다 어휘 | B | 0.45 | - | '구축'은 시설이나 체계에 어울리는 말이다. |
| `ko.collocate.generate` | ko | 과다 어휘 | B | 0.45 | - | '생성'은 데이터나 산출물에 어울리는 말이다. |
| `ko.collocate.deliver` | ko | 과다 어휘 | C | 0.35 | - | '가치를 전달', '성공을 달성'처럼 겹말에 가까운 서술. |
| `ko.collocate.formal-verb` | ko | 과다 어휘 | B | 0.55 | - | 마음 상태에 정책 문서의 동사를 붙였다. |
| `ko.collocate.enjoy` | ko | 과다 어휘 | C | 0.4 | - | '향유', '영위'는 문어체에서 겉도는 말이다. |
| `ko.collocate.perform` | ko | 과다 어휘 | C | 0.35 | - | 일상 행동에 '수행', '진행'을 붙였다. |
| `ko.collocate.informed` | ko | 과다 어휘 | C | 0.45 | - | '정보에 입각한', '강력한 증거'처럼 영어 구절을 옮긴 짝. |
| `ko.collocate.nuance` | ko | 과다 어휘 | C | 0.4 | - | '뉘앙스 있는', '사려 깊은 고려'처럼 좋은 말만 붙인 짝. |
| `ko.collocate.success` | ko | 과다 어휘 | C | 0.4 | - | '성공적으로 ~하다', '영향을 만들다'는 번역투 짝이다. |
| `ko.frame.in-progress` | ko | 번역투 | C | 0.2 | - | '~되고 있다' 진행 피동이 잦다. |
| `ko.frame.evident` | ko | 의미 부풀리기 | C | 0.35 | - | 스스로 분명하다고 단언하며 근거를 대지 않는다. |
| `ko.frame.foundation` | ko | 의미 부풀리기 | B | 0.5 | - | '발판을 마련한다'는 무엇이 달라지는지 말하지 않는다. |
| `ko.frame.no-longer` | ko | 구조 습관 | C | 0.3 | - | '더 이상 ~이 아니다' 도입 틀. |
| `ko.frame.either-or` | ko | 구조 습관 | B | 0.5 | - | 'A인가, B인가' 대구 질문. |
| `ko.frame.time-to` | ko | 의미 부풀리기 | B | 0.5 | - | '~할 때입니다' 맺음. |
| `ko.frame.from-to` | ko | 구조 습관 | C | 0.3 | - | 'X에서 Y로 전환'처럼 변화를 틀로 선언한다. |
| `ko.frame.leads-to` | ko | 구조 습관 | C | 0.4 | - | '결국 ~로 이어진다' 결산 틀. |
| `ko.frame.reason-close` | ko | 구조 습관 | C | 0.3 | - | '~하는 이유다' 결말. |
| `ko.frame.horizon` | ko | 의미 부풀리기 | C | 0.2 | - | 막연한 시간 지평. |
| `ko.frame.open-problem` | ko | 의미 부풀리기 | B | 0.45 | - | 내용 없이 남은 과제만 선언한다. |
| `ko.frame.musing` | ko | 의미 부풀리기 | C | 0.2 | - | 성찰을 알리는 부사. |
| `ko.frame.personified` | ko | 의미 부풀리기 | C | 0.35 | - | 무생물이 말하고 보여 주는 주어. |
| `ko.frame.nobody-says` | ko | 출처 없는 권위 | C | 0.4 | - | 누가 그렇게 보는지 밝히지 않은 평가. |
| `ko.frame.hedged-outlook` | ko | 군더더기·유보 | C | 0.25 | - | 완곡한 추정 맺음. |
| `ko.frame.formal-noun` | ko | 군더더기·유보 | C | 0.2 | - | '~라는 것', '~라는 점' 명사화. |
| `ko.frame.degree-adverb` | ko | 군더더기·유보 | C | 0.15 | - | 정도부사가 겹친다. |
| `ko.frame.policy-verb` | ko | 과다 어휘 | C | 0.4 | - | 정책 문서식 동사를 이어 붙인다. |
| `ko.frame.deictic-lead` | ko | 접속어 남발 | C | 0.25 | - | 문장을 '이는'으로 여는 습관. |
| `ko.frame.numbered-inline` | ko | 서식 신호 | C | 0.3 | - | 한 문단 안의 '1) 2) 3)' 나열. |
| `ko.frame.subtitle-heading` | ko | 서식 신호 | C | 0.25 | - | '주제: 부제' 형태의 제목. |
| `ko.frame.quote-emphasis` | ko | 서식 신호 | C | 0.2 | - | 짧은 낱말을 따옴표로 강조한다. |
| `ko.over.self-intro` | ko | 의미 부풀리기 | B | 0.4 | - | 문서가 자기 자신을 소개하는 문장으로 시작한다. |
| `ko.over.purpose-narration` | ko | 의미 부풀리기 | B | 0.5 | - | 왜 그렇게 만들었는지 변명하듯 적는다('~하려고 붙였습니다'). |
| `ko.over.because-tail` | ko | 의미 부풀리기 | C | 0.35 | - | '~때문입니다', '까닭은'으로 이유를 덧붙인다. |
| `ko.over.gloss` | ko | 의미 부풀리기 | C | 0.35 | - | 뜻이 뻔한 말을 '~를 의미합니다', '~에 해당합니다'로 풀어 쓴다. |
| `ko.over.recorded` | ko | 의미 부풀리기 | C | 0.4 | - | '~정리해 두었습니다'. 문서가 자기가 한 일을 보고한다. |
| `ko.over.paren-stack` | ko | 의미 부풀리기 | C | 0.3 | - | 한 문장에 괄호 설명이 둘 이상 겹친다. |
| `ko.over.long-list` | ko | 의미 부풀리기 | C | 0.3 | - | 한 문장에 항목을 네 개 이상 나열한다. |
| `ko.tic.value-figurative` | ko | 과다 어휘 | B | 0.5 | - | 수치가 아닌 것에 '값'을 붙인다(값어치, 의미의 값). |
| `ko.tic.value-bare` | ko | 과다 어휘 | C | 0.25 | - | '값'이 한 글에 자주 나온다. 변수나 측정값이 아니면 다른 낱말로 바꿀 수 있다. |
| `ko.tic.judge` | ko | 과다 어휘 | C | 0.25 | - | '판단'이 한 글에 자주 나온다. |
| `ko.tic.criterion-becomes` | ko | 과다 어휘 | B | 0.4 | - | '기준이 된다', '기준으로 삼는다': 무엇을 기준으로 어떻게 정하는지 말하지 않는다. |
| `ko.tic.criterion-bare` | ko | 과다 어휘 | C | 0.2 | - | '기준'이 한 글에 자주 나온다. |
| `ko.tic.test-heavy` | ko | 과다 어휘 | C | 0.2 | - | '시험'이 한 글에 자주 나온다. |
| `ko.tic.test-bench` | ko | 과다 어휘 | B | 0.5 | - | '시험대'. 무엇을 어떻게 겪는지 말하지 않는다. |
| `ko.tic.pivotal` | ko | 과다 어휘 | B | 0.5 | - | '관건'. 무엇이 걸렸는지 구체적으로 쓰지 않는다. |
| `ko.tic.trail` | ko | 과다 어휘 | C | 0.4 | - | '따라붙다'. 딸린다, 붙는다는 말을 추상적으로 쓴다. |
| `ko.tic.defer` | ko | 과다 어휘 | C | 0.3 | - | '미뤘다'. 일정이 아닌 판단이나 문제를 미룬다고 쓴다. |
| `ko.tic.crossover` | ko | 과다 어휘 | C | 0.3 | - | '넘어오다/넘어가다'를 화제나 단계 전환에 쓴다. |
| `ko.tic.continues` | ko | 과다 어휘 | C | 0.25 | - | '이어지다'가 인과와 연결을 두루 가린다. |
| `ko.tic.draw-line` | ko | 과다 어휘 | B | 0.45 | - | '선을 긋다'. 무엇을 하지 않겠다는 뜻인지 풀어 쓰지 않는다. |
| `ko.tic.touch-up` | ko | 과다 어휘 | B | 0.45 | - | '손보다'. 무엇을 어떻게 바꾸는지 말하지 않고 손만 댄다는 말을 쓴다('손볼 곳이 없다'). |
| `ko.tic.distinct` | ko | 과다 어휘 | C | 0.35 | - | '뚜렷하게', '뚜렷한'. 얼마나인지 수치 없이 정도만 꾸민다('뚜렷하게 확인됐다'). |
| `ko.tic.weak-verdict` | ko | 과다 어휘 | C | 0.4 | - | '~은 약했으며'. 무엇이 얼마나 약한지 말하지 않고 강약만 붙인다. |
| `ko.tic.density` | ko | 과다 어휘 | B | 0.5 | - | 단위 없는 '밀도'. 무게나 길이 같은 단위가 붙지 않으면 비율이나 건수로 말할 것을 추상어로 쓴 것이다. |
| `ko.tic.text-amount` | ko | 과다 어휘 | C | 0.4 | - | '글 분량'. 글자, 어절, 문장 중 무엇을 센 것인지 말하지 않는다. |
| `ko.tic.weigh-up` | ko | 과다 어휘 | B | 0.4 | - | '따지다'. 승부나 시비를 가릴 때가 아니면 '확인한다', '묻는다'를 뜻 없이 대신한다('내용이 사실인지는 따지지 않는다'). |
| `ko.tic.between` | ko | 과다 어휘 | C | 0.3 | - | '사이'가 한 글에 되풀이된다. '그 사이였다'처럼 위치를 말하지 않고 중간쯤이라는 뜻만 흐린다. |
| `ko.tic.degree-of` | ko | 과다 어휘 | C | 0.35 | - | '구분 정도', '차이 정도'. 얼마나인지 수치 없이 '정도'라는 추상어로 감싼다. |
| `ko.tic.whether` | ko | 과다 어휘 | C | 0.35 | - | '사실 여부', '확인 여부'. 무엇을 확인하는지 말하지 않고 '여부'로 뭉뚱그린다. |
| `ko.tic.not-look` | ko | 과다 어휘 | B | 0.45 | - | 띄어 쓴 '보지 않다'. 사람은 '보지'가 다른 뜻으로 읽히는 것을 피해 '보지않다'로 붙여 쓰거나 '확인하지 않는다'로 쓴다. |
| `ko.tic.freq-phrase` | ko | 과다 어휘 | B | 0.4 | - | '출현 빈도'. '나온 횟수', '비율'이면 될 말을 한자어로 굳힌다. |
| `ko.tic.computed-score` | ko | 과다 어휘 | B | 0.4 | - | '산출'. 계산하거나 구한다는 말을 보고서 어휘로 바꿔 쓴다('산출 점수'). |
| `ko.tic.style-pattern` | ko | 과다 어휘 | B | 0.4 | - | '문체 패턴'. 무슨 표현을 말하는지 흐린다. |
| `ko.tic.detail-adj` | ko | 과다 어휘 | C | 0.35 | - | '세부적인'. '자세한'으로 충분한 자리에 한자어 관형어를 쓴다('세부적인 한계'). |
| `ko.format.middle-dot` | ko | 서식 신호 | C | 0.3 | - | 가운데 점(·)으로 낱말을 나열한다('코드·URL·표'). 읽는 사람이 쉼표나 '와'로 쓰는 자리에 점을 쓴다. |
| `ko.tic.reveal` | ko | 과다 어휘 | C | 0.35 | - | '드러내다/드러나다'. 보인다, 밝힌다는 말을 추상적으로 쓴다('드러내지 않는다'). |
| `ko.tic.signal-bare` | ko | 과다 어휘 | C | 0.3 | - | '신호'가 한 글에 되풀이된다. 특징, 단서, 표현을 가리키는 말로 번번이 쓴다. |
| `ko.tic.compare-with` | ko | 과다 어휘 | B | 0.4 | - | '견주다'. 비교한다는 말을 고풍스럽게 바꿔 쓴다. |
| `ko.tic.purpose` | ko | 과다 어휘 | C | 0.35 | - | '~하는 용도다'. 무엇을 위한 것인지 풀지 않고 '용도'로 묶는다. |
| `ko.tic.skip` | ko | 과다 어휘 | B | 0.4 | - | '건너뛰다'. 제외하거나 생략한다는 말을 반복해서 쓴다. |
| `ko.tic.reproduce` | ko | 과다 어휘 | C | 0.35 | - | '재현'. 다시 나왔다는 말을 보고서 어휘로 바꿔 쓴다('재현됐다'). |
| `ko.tic.ask-back` | ko | 과다 어휘 | C | 0.35 | - | '되묻다'. 묻는다는 말에 '되'를 붙여 대화하는 시늉을 낸다. |
| `ko.tic.put-in-criteria` | ko | 과다 어휘 | B | 0.4 | - | '기준에 넣다'. 무엇을 따지는지 말하지 않고 기준이라는 틀에 담는다. |
| `ko.tic.put-keep` | ko | 과다 어휘 | C | 0.3 | - | '두다'. 남긴다, 정한다, 놓는다는 뜻을 가리지 않고 폭넓게 쓴다. |
| `ko.tic.fit-to` | ko | 과다 어휘 | C | 0.35 | - | '맞추다'. 정한다, 고친다, 따른다, 일치시킨다는 뜻을 가리지 않고 폭넓게 쓴다('맞추지 않는다'). |
| `ko.tic.score-bare` | ko | 과다 어휘 | C | 0.3 | - | '점수'. 표준국어대사전은 '성적을 나타내는 숫자'로 풀이한다. 성적이 아닌 글에서 수치를 '점수'로 부른다. |
| `ko.tic.local` | ko | 과다 어휘 | B | 0.4 | - | '국소'. 의학 용어가 아닌 글에서 '일부', '해당 부분'이라는 말을 한자어로 바꿔 쓴다('국소 수정'). |
| `ko.tic.count-verb` | ko | 과다 어휘 | B | 0.4 | - | '세다'. 나이나 숫자를 헤아리는 때가 아니면 확인한다, 구한다, 반영한다는 말을 '센다'로 뭉뚱그린다('세지 않는다', '세고 있다'). |
| `ko.tic.habit-speech` | ko | 과다 어휘 | B | 0.4 | - | '입버릇'. 되풀이되는 표현을 가리키는 말인데 무엇이 되풀이되는지 쓰지 않는다. |
| `ko.tic.sentence-frame` | ko | 과다 어휘 | B | 0.4 | - | '문장틀'. 문장 구조를 가리키는 추상어로, 어떤 구조인지 쓰지 않는다. |
| `ko.tic.dash-word` | ko | 과다 어휘 | B | 0.4 | - | '줄표'. 모델이 문장부호 '—'를 가리킬 때 쓰는 말이다. |
| `ko.tic.neutral` | ko | 과다 어휘 | B | 0.4 | - | '중립'. 정치나 가치가 아닌 곳에서 '모델 중립'처럼 어울리지 않는 자리에 쓴다. |
| `ko.tic.lean-on` | ko | 과다 어휘 | B | 0.4 | - | '기대다'. 사물이나 사람에게 몸을 기댈 때만 자연스럽다. 규칙이나 수치에 '기댄다'고 쓰면 의존한다는 뜻을 흐린다. |
| `ko.tic.approx` | ko | 과다 어휘 | B | 0.4 | - | 숫자 없는 '근삿값', '근사값'. 어느 수에 얼마나 가까운지 말하지 않고 '근사'라는 말만 쓴다. |
| `ko.tic.measured-value` | ko | 과다 어휘 | B | 0.4 | - | 숫자 없는 '측정한 값', '측정값'. 무엇을 얼마로 쟀는지 말하지 않고 측정했다는 사실만 쓴다. |
| `ko.tic.heavy-light` | ko | 과다 어휘 | B | 0.4 | - | '무겁다', '가볍다'. 무게나 사물, 사람이 나오지 않는 문장에서 분량, 부담, 어조를 무게에 빗댄다. |
| `ko.tic.measure-any` | ko | 과다 어휘 | B | 0.5 | - | '재다/잰다'. 길이를 잴 때가 아니면 확인한다, 비교한다, 구한다는 말을 '잰다'로 바꿔 쓴다('재지 않았다'). |
| `ko.tic.limit-open` | ko | 과다 어휘 | B | 0.5 | - | 서술 없이 '한계'로 시작한다. 무엇이 어디까지 안 되는지 말하기 전에 '한계'라는 이름표부터 붙인다. |
| `ko.tic.limit-bare` | ko | 과다 어휘 | C | 0.3 | - | '한계'가 한 글에 되풀이된다. |
| `ko.tic.work-done` | ko | 과다 어휘 | B | 0.4 | - | '하는 일', '하지 않는 일'. 무엇을 하는지 쓰지 않고 '일'로 뭉뚱그려 구분한다. |
| `ko.tic.not-do` | ko | 과다 어휘 | C | 0.35 | - | '~하지 않는다'. 하지 않는 일을 나열해 글을 끝맺는다. |
| `ko.tic.index-bare` | ko | 과다 어휘 | B | 0.5 | - | '지수'. 표준국어대사전의 '지수'는 거듭제곱의 횟수를 뜻하는 수학 용어이고, 경제에서는 기준 시점을 100으로 놓고 비교한 수치를 가리킨다. 기준값이나 수식 없이 '지수'라고 부르면 뜻이 흐려진다. |
| `ko.tic.who-text` | ko | 과다 어휘 | B | 0.45 | - | '사람 글', 'AI 글'. 누가 쓴 글인지 서술하지 않고 '글' 앞에 주체만 붙인다. |
| `ko.tic.structure-habit` | ko | 과다 어휘 | B | 0.4 | - | '구조 습관'. 문장이나 글이 어떤 틀로 짜였는지 쓰지 않고 '습관'이라는 이름표를 붙인다. |
| `ko.tic.false-detect` | ko | 과다 어휘 | B | 0.45 | - | '오탐', '미탐'. 줄여 쓴 말로, 풀어 쓰면 '오탐지', '미탐지'이다. |
| `ko.tic.seem` | ko | 과다 어휘 | B | 0.4 | - | '보인다', '안 보인다', '잘 안 보인다'. 눈이나 카메라로 보는 일이 아닌데 '드러난다', '나타난다', '잡힌다'는 뜻으로 쓴다. |
| `ko.tic.come-out` | ko | 과다 어휘 | B | 0.4 | - | '나왔다', '나오지 않았다', '나오려고 한다'. 문이나 출입구로 드나드는 일이 아닌데 '생겼다', '드러났다', '걸렸다'는 뜻으로 쓴다. |
| `ko.tic.prior-bare` | ko | 과다 어휘 | B | 0.4 | - | '전 수치'. 이전이라는 뜻으로 쓴 말인데 사람이 읽으면 '모든 수치'로 읽힌다. |
| `ko.tic.piece` | ko | 과다 어휘 | B | 0.4 | - | '조각'. 케이크, 피자, 부품처럼 실제로 쪼개진 물건이 아닌데 글의 일부나 표본을 '조각'이라고 부른다. |
| `ko.tic.listen` | ko | 과다 어휘 | B | 0.4 | - | '듣는다', '듣지 않는다'. 귀로 소리를 듣는 일이 아닌데 따른다, 받아들인다, 묻는다는 뜻으로 쓴다. |
| `ko.tic.pair-up` | ko | 과다 어휘 | B | 0.45 | - | '짝짓다', '짝지어', '짝을 이루어'. 대응시킨다는 말을 짝 맞추기에 빗댄다. |
| `ko.tic.holdout` | ko | 과다 어휘 | B | 0.45 | - | '홀드아웃'. 영어 'hold-out'을 소리 나는 대로 옮긴 말이다. 사람이 쓴 글에서는 '검증 자료'처럼 풀어 쓴다. |
| `ko.tic.leave` | ko | 과다 어휘 | B | 0.4 | - | '남긴다', '남기지 않는다'. 일부러 조금 두거나 무언가를 두고 오는 일이 아닌데 유지한다, 보존한다, 적는다는 뜻으로 쓴다. |
| `ko.tic.point-at` | ko | 과다 어휘 | B | 0.4 | - | '짚다', '짚은'. 무언가를 만지거나 짚는 일이 아닌데 지적한다, 밝힌다는 뜻으로 쓴다. |
| `ko.tic.fathom` | ko | 과다 어휘 | B | 0.4 | - | '헤아린다'. 사람의 마음을 짐작하는 문장이 아닌데 센다, 계산한다, 반영한다는 뜻으로 쓴다. |
| `ko.tic.open-data` | ko | 과다 어휘 | C | 0.35 | - | '공개 자료'. 사람은 보통 '공개된 자료'라고 풀어 쓴다. |
| `ko.tic.replace-with` | ko | 과다 어휘 | B | 0.45 | - | '갈음하다'. 사람은 일상 글에서 거의 쓰지 않는 말로, '대신한다'를 격식 있어 보이게 바꾼 것이다. |
| `ko.tic.link-word` | ko | 과다 어휘 | B | 0.4 | - | '이음말'. 사람은 거의 쓰지 않는 말로, 문장을 잇는 말을 가리킬 때 '이어지는 말'이라고 한다. |
| `ko.tic.gap-arises` | ko | 과다 어휘 | B | 0.4 | - | '차이가 난다'. 사람은 '차이가 발생한다', '차이가 확인된다'처럼 쓰고, '난다'로 줄여 쓰지 않는다. |
| `ko.tic.reach` | ko | 과다 어휘 | B | 0.4 | - | '닿다', '안 닿는 값', '닿은 값'. '닿다'는 부딪히다에 가까운 말인데, 도달한다, 이른다는 뜻으로 폭넓게 쓴다. |
| `ko.tic.personify` | ko | 과다 어휘 | B | 0.4 | - | 추상 명사를 사람처럼 쓴다('시간이 말했다'). 소설 윤문에서는 의인화한 추상 주어를 쓰지 않는다. |
| `ko.tic.realize` | ko | 과다 어휘 | B | 0.45 | - | '그는 비로소 깨달았다'. 깨달음을 선언하는 문장으로 장면을 닫는다. |
| `ko.tic.object-honorific` | ko | 과다 어휘 | B | 0.4 | - | 사물에 '-시-'를 붙이는 과잉 높임('커피 나오셨습니다'). |
| `ko.tic.win-lose` | ko | 과다 어휘 | C | 0.35 | - | 비교를 승부로 쓴다('이겼다', '밀렸다'). |
| `ko.tic.stand` | ko | 과다 어휘 | B | 0.35 | - | '~에 선다/섭니다'. 위치나 입장을 몸의 자세에 빗대 말한다. |
| `ko.tic.exceed` | ko | 과다 어휘 | C | 0.35 | - | '웃돌다'. 얼마나 넘는지 숫자 없이 방향만 말한다. |
| `ko.tic.put-forward` | ko | 과다 어휘 | C | 0.35 | - | '내세우다'. 주장하는지 강조하는지 알 수 없다. |
| `ko.tic.claim` | ko | 과다 어휘 | C | 0.25 | - | '주장'이 한 글에 자주 나온다. 누가 무엇을 근거로 말하는지가 흐려진다. |
| `ko.tic.demand` | ko | 과다 어휘 | C | 0.25 | - | '요구'가 한 글에 자주 나온다. |
| `ko.tic.widen` | ko | 과다 어휘 | C | 0.3 | - | '넓히다'. 무엇이 얼마나 커지는지 말하지 않는다. |
| `ko.tic.apply` | ko | 과다 어휘 | C | 0.25 | - | '적용'이 한 글에 자주 나온다. |
| `ko.tic.dress-up` | ko | 과다 어휘 | C | 0.35 | - | '꾸미다'. 설명이나 보고를 그럴듯하게 만든다는 말로 쓴다. |
| `ko.tic.back-up` | ko | 과다 어휘 | C | 0.3 | - | '뒷받침'. 무엇이 어떤 근거로 받치는지 말하지 않는다. |
| `ko.tic.adapt` | ko | 과다 어휘 | C | 0.25 | - | '적응'이 한 글에 자주 나온다. |
| `ko.tic.corpus` | ko | 과다 어휘 | C | 0.3 | - | '말뭉치'. 학술 용어를 설명 없이 쓴다. |
| `ko.tic.shape` | ko | 과다 어휘 | B | 0.4 | - | '~모양입니다'. 형태를 말하는 것인지 추측을 말하는 것인지 흐리게 둔다. |
| `ko.tic.unrelated` | ko | 과다 어휘 | B | 0.4 | - | '~와는 상관이 없습니다'. 아무도 묻지 않은 오해를 먼저 지운다. |
| `ko.tic.whole` | ko | 과다 어휘 | C | 0.25 | - | '전체'가 한 글에 자주 나온다. |
| `ko.tic.contract-word` | ko | 과다 어휘 | B | 0.4 | - | '응답 계약' 같은 조어. 읽는 사람이 처음 보는 용어를 설명 없이 쓴다. |
| `ko.tic.same-as` | ko | 과다 어휘 | C | 0.3 | - | '같은 순서로', '같은 구성'. 무엇이 같은지 앞뒤에서 밝히지 않는다. |
| `ko.term.release` | ko | 과다 어휘 | A | 0.5 | safe | '릴리스'가 아니라 '릴리즈'로 쓴다. |
| `ko.term.harness` | ko | 과다 어휘 | A | 0.5 | safe | '하네즈', '하니스'가 아니라 '하네스'로 쓴다. 모델이 자주 내는 표기다. |
| `ko.term.synthesizer` | ko | 과다 어휘 | A | 0.5 | safe | '신시사이저'. 모델이 자주 내는 표기이고 사람들은 '신디사이저'로 쓴다. 표기 규범과는 별개로 쓰는 빈도 기준이다. |
| `ko.tic.among` | ko | 과다 어휘 | C | 0.4 | - | '세 가지 중 하나'처럼 선택지를 먼저 깔아 놓는 틀. |
| `ko.tic.empty-answer` | ko | 과다 어휘 | C | 0.35 | - | '빈 답변'. 무엇이 비었는지 밝히지 않는다. |
| `ko.puffery.authority` | ko | 의미 부풀리기 | C | 0.35 | - | 깊이나 무게를 주장하는 말('핵심은', '본질적으로'). |
| `ko.puffery.closer-line` | ko | 의미 부풀리기 | B | 0.6 | - | 앞 문장을 되풀이하는 한 줄 맺음. |
| `ko.signpost.candor` | ko | 예고·안내 | C | 0.4 | - | 솔직함을 알리는 말만 있고 내용은 따로다. |
| `ko.signpost.no-one` | ko | 예고·안내 | C | 0.4 | - | 아무도 하지 않은 반론에 답한다. |
| `ko.puffery.novelty` | ko | 의미 부풀리기 | B | 0.6 | - | 알려진 것을 아무도 모르는 것처럼 말한다. |
| `ko.signpost.numbered` | ko | 예고·안내 | C | 0.3 | - | 항목 수를 앞세운 틀. |
| `ko.puffery.reaction` | ko | 의미 부풀리기 | C | 0.25 | - | 정형 반응 틀. 실제 반응은 남기고 빈 틀만 뺀다. |
| `ko.signpost.endorse` | ko | 예고·안내 | C | 0.35 | - | 이유 없는 추천 맺음. |
| `ko.signpost.reasoning` | ko | 예고·안내 | B | 0.5 | - | 추론 과정의 비계가 글에 남았다. |
| `ko.puffery.lingering` | ko | 의미 부풀리기 | C | 0.5 | - | 필자의 주의가 머물렀다는 확인할 수 없는 주장. |
| `ko.trans.enable` | ko | 번역투 | C | 0.3 | - | 무생물 주어가 '~를 가능하게 한다'로 서술한다(영어 allow, enable의 직역). |
| `ko.trans.plural` | ko | 번역투 | C | 0.0 | - | 복수 표지가 겹친다('여러 정보들'). 영어 복수형의 직역(실측에서 사람이 쓴 글과 구분되지 않아 점수에서 뺀다). |
| `ko.opaque.differ-on` | ko | 해독 부담 | C | 0.45 | - | '갈린다'. '~에서', '여기서' 같은 조사와 상관없이, 무엇이 어떻게 달라지는지 말하지 않고 갈림만 말한다. |
| `ko.opaque.divide` | ko | 해독 부담 | C | 0.4 | - | '나뉜다'. 무엇이 어떻게 다른지 말하지 않고 나뉨만 말한다('에세이는 잘 나뉘었다'). |
| `ko.opaque.cut-apart` | ko | 해독 부담 | C | 0.4 | - | '갈랐다', '가른다'. 구분되는 정도를 칼로 베는 동작에 빗댄다('에세이는 잘 갈랐다'). |
| `ko.figure.moat` | ko | 해독 부담 | C | 0.35 | - | 방어 시설 비유('해자', '방어선'). 독자가 풀어야 뜻이 나온다. |
| `ko.opaque.closes-on` | ko | 해독 부담 | C | 0.4 | - | '~에 닫힌다'. 끝난다는 말을 구조물에 빗댄다. |
| `ko.opaque.self-qa-dash` | ko | 해독 부담 | C | 0.4 | - | 묻고 줄표로 바로 답하는 틀('그럼 무엇이 문제인가 — 기준이 없다'). |
| `ko.opaque.arrow` | ko | 해독 부담 | C | 0.25 | - | 화살표가 동사나 인과를 대신한다. |
| `ko.opaque.telegraphic-end` | ko | 해독 부담 | C | 0.3 | - | 명사로 끝나는 개조식 줄이 문서 안에서 되풀이된다. |
| `ko.opaque.vague-referent` | ko | 해독 부담 | C | 0.2 | - | '그 부분', '해당 건'처럼 무엇을 가리키는지 앞에 없는 말. |
| `ko.opaque.inanimate-verb` | ko | 해독 부담 | C | 0.4 | - | 사물이 사람처럼 말하고 버틴다. |
| `ko.figure.load-bearing` | ko | 해독 부담 | C | 0.45 | - | 영어 'load-bearing'의 직역('하중을 받는'). 중요하다는 말을 건축 비유로 한다. |
| `ko.genre.pronoun-repeat` | ko | 번역투 | C | 0.3 | - | '그녀는', '그것은'으로 여는 문장이 되풀이된다. 영어 대명사를 옮긴 버릇이고 한국어는 주어를 생략해도 자연스럽다. |
| `ko.genre.synonym-pair` | ko | 군더더기·유보 | B | 0.45 | - | 같은 뜻의 말을 겹쳐 꾸민다('빠르고 신속한'). |
| `ko.genre.will-look` | ko | 예고·안내 | B | 0.4 | - | '~를 살펴보겠습니다'. 할 일을 예고하고 내용은 뒤로 미룬다. |
| `ko.genre.strawman` | ko | 구조 습관 | B | 0.45 | - | 아무도 제기하지 않은 반론을 세우고 반박한다('비싸다고 생각할 수 있지만'). |
| `ko.genre.vague-authority` | ko | 출처 없는 권위 | B | 0.4 | - | 출처 없이 권위를 빌린다('전문가들은', '알려져 있다'). |
| `ko.genre.noun-chain` | ko | 번역투 | B | 0.5 | - | 명사를 '~의 ~을 통한 ~의'로 잇는다('성능의 향상을 통한 효율의 증대'). |
| `ko.genre.genitive-chain` | ko | 번역투 | C | 0.35 | - | '~의 ~의 ~의'처럼 속격 조사가 세 번 이어진다. |
| `ko.genre.ripple` | ko | 의미 부풀리기 | C | 0.35 | - | '파급 효과', '나비 효과'. 무엇이 어디까지 바뀌는지 말하지 않고 파급만 말한다. |
| `ko.genre.rather-than` | ko | 구조 습관 | C | 0.25 | - | 'A보다는 B'가 되풀이된다. 'A가 아니라 B' 대구의 변종이다. |
| `ko.genre.contribution` | ko | 의미 부풀리기 | B | 0.45 | - | 결론의 의의 부풀리기('기여할 것으로 기대된다', '의의가 크다'). |
| `ko.genre.must-have-been` | ko | 아첨·공치사 | B | 0.4 | - | '정말 속상하셨겠어요'. 정형화된 공감 문구. |
| `ko.genre.cheer` | ko | 아첨·공치사 | C | 0.35 | - | '응원합니다'. 대화를 닫는 정형 문구. |
| `ko.genre.echo-question` | ko | 챗봇 잔재 | B | 0.45 | - | '~가 궁금하셨군요'. 질문받은 것을 되짚고 답을 미룬다. |
| `ko.genre.double-hedge` | ko | 군더더기·유보 | B | 0.45 | - | 유보가 두 겹이다('~일 수 있을 것으로 사료된다'). |
| `ko.genre.about-repeat` | ko | 번역투 | C | 0.3 | - | '~에 관한'이 되풀이된다. |
| `ko.genre.double-particle` | ko | 번역투 | C | 0.3 | - | 이중 조사('~에서의', '~으로의'). 읽다가 숨이 걸린다. |
| `ko.genre.aim-to` | ko | 번역투 | C | 0.35 | - | '~하는 것을 목표로'. 명사화한 목적 표현. |
| `ko.genre.need-for` | ko | 번역투 | C | 0.35 | - | '필요성이 있다', '필요성이 대두된다'. |
| `ko.genre.suffix-pile` | ko | 번역투 | C | 0.2 | - | 한자어 접미사 '-성', '-화'가 한 글에 쌓인다(안정성, 고도화, 최적화). |
| `ko.genre.would-you` | ko | 아첨·공치사 | C | 0.3 | - | '~하시겠어요?'가 되풀이된다. |
| `ko.genre.as-you-know` | ko | 구조 습관 | B | 0.4 | - | '너도 알다시피'. 인물끼리 아는 사실을 독자에게 설명하려고 대사로 말한다. |
| `ko.genre.realize-late` | ko | 구조 습관 | B | 0.45 | - | '그제야 깨달았다'. 깨달음을 선언하는 문장으로 장면을 닫는다. |
| `ko.genre.ellipsis-dialogue` | ko | 서식 신호 | C | 0.35 | - | 대사 하나에 말줄임표가 둘 이상이다. |
| `ko.genre.named-emotion` | ko | 감정 직접 서술 | B | 0.45 | - | '깊은 상실감', '벅찬 감동'. 감정에 이름을 붙여 설명한다. |
| `ko.genre.double-simile` | ko | 과다 어휘 | C | 0.3 | - | 한 문장에 비유가 둘 이상 겹친다. |
| `ko.tic.surface` | ko | 과다 어휘 | B | 0.5 | - | '표면'. 땅이나 물체의 겉면이 아닌 곳에서 '문제의 표면', '표면 위로 드러난다'처럼 겉이나 드러난 부분을 가리킨다. |
| `ko.tic.atomic` | ko | 과다 어휘 | B | 0.5 | - | '원자적'. 물리나 데이터베이스 용어가 아닌 곳에서 '더 쪼갤 수 없는', '한 번에 끝나는'을 가리키는 말로 쓴다. |
| `ko.tic.and-start` | ko | 과다 어휘 | C | 0.3 | - | '그리고'가 한 글에 자주 나온다. 문장과 문장, 낱말과 낱말을 잇는 말로 번번이 붙인다. |
| `ko.tic.write-diff` | ko | 과다 어휘 | B | 0.5 | - | '차이를 씁니다'. 사용한다는 뜻을 '쓰다'로 바꿔 쓴다. 글을 적는 일이 아니다. |
| `ko.tic.write-use` | ko | 과다 어휘 | B | 0.3 | - | '쓰다'가 한 글에 되풀이된다. 글을 적는 때가 아니면 사용한다, 넣는다, 정한다를 '쓰다' 하나로 뭉뚱그린다. |
| `ko.tic.turn-verb` | ko | 과다 어휘 | B | 0.45 | - | '돌리다'. 물체를 회전시킬 때가 아니면 실행한다, 반복한다, 적용한다를 '돌린다'로 바꿔 쓴다. |
| `ko.tic.link-verb` | ko | 과다 어휘 | B | 0.45 | - | '잇다'. 선이나 줄로 물리적으로 이을 때가 아니면 연결한다, 관련짓는다, 따른다를 '잇는다'로 바꿔 쓴다. |
| `ko.tic.window` | ko | 과다 어휘 | B | 0.45 | - | '창', '창문'. 실제 창이나 화면 창이 아닌 곳에서 '관찰 창', '창을 열어 둔다'처럼 범위나 기회, 시야를 가리킨다. |
| `ko.tic.frame-noun` | ko | 과다 어휘 | B | 0.4 | - | '틈', '이음', '테두리', '격자', '빗살'. 건축이나 공작 어휘로 추상적인 구조를 가리킨다('틈이 생긴다', '테두리를 정한다'). |
| `ko.tic.deal-with` | ko | 과다 어휘 | B | 0.5 | - | '다룬다'. 반려동물이나 사람을 대하는 일이 아니면 설명한다, 검사한다, 처리한다, 포함한다를 '다룬다' 하나로 뭉뚱그리고 '~를 다룬다', '~는 다루지 않는다'로 범위만 말한다. |
| `ko.tic.split-verb` | ko | 과다 어휘 | B | 0.45 | - | '가른다', '가릅니다'. 물체를 실제로 가르는 일이 아니면 구분한다, 나눈다, 결정한다를 '가른다'로 바꿔 쓴다('승부를 가른다'). |
| `ko.tic.contain-verb` | ko | 과다 어휘 | B | 0.45 | - | '담는다', '담았다', '담겨 있다'. 물체를 그릇에 담는 일이 아니면 포함한다, 적는다, 넣는다, 나타낸다를 '담는다'로 바꿔 쓴다. |
| `ko.tic.impression-give` | ko | 과다 어휘 | B | 0.5 | - | '인상을 준다', '인상을 남긴다'. 사람 얼굴이 아닌 글이나 결과에서 '~한 느낌이다'를 '인상'으로 감싸 판단을 흐린다. |
| `ko.tic.impression-bare` | ko | 과다 어휘 | B | 0.5 | - | '인상'. 사람 얼굴이나 가격 인상이 아닌 곳에서 '인상적', '인상이 강하다'로 근거 없이 평가한다. |
| `ko.tic.fit-together` | ko | 과다 어휘 | B | 0.5 | - | '맞아떨어집니다', '들어맞는다', '맞물린다'. 수치나 사실이 일치한다는 말을 딱 맞는 부품에 빗대어 결과의 일치를 근거 없이 보증한다. |
| `ko.tic.bind-verb` | ko | 과다 어휘 | B | 0.45 | - | '묶습니다', '묶어서'. 끈이나 줄로 실제로 묶는 일이 아니면 합친다, 분류한다, 함께 다룬다를 '묶는다'로 바꿔 쓴다. |
| `ko.tic.generation` | ko | 과다 어휘 | B | 0.5 | - | '세대'. 조부모, 부모, 자녀처럼 시간으로 이어지는 사람의 세대나 가구 수를 말하는 때가 아니면 '차세대 모델', '이전 세대'처럼 제품이나 모델의 버전을 '세대'로 부른다. |
| `ko.tic.destination` | ko | 과다 어휘 | B | 0.5 | - | '목적지'. 실제로 가는 장소가 아닌 곳에서 목표, 결론, 결과를 '목적지'라는 여행 어휘로 부른다('최종 목적지'). |
| `ko.tic.jot-verb` | ko | 과다 어휘 | B | 0.4 | - | '적습니다', '적는다'. 글로 작성하거나 기록한다는 뜻을 '적다'로 바꿔 쓴다. '많다'의 반대인 '적다'와 형태가 같아 읽다가 걸린다. |
| `ko.tic.same-opener` | ko | 과다 어휘 | C | 0.35 | - | '같은'으로 시작하는 문장이 되풀이된다. 앞 문장과 무엇이 같은지 말하지 않고 연결만 한다('같은 방식으로'). |
| `ko.tic.add-verb` | ko | 과다 어휘 | C | 0.35 | - | '더하다'. 수를 합치거나 실제로 덧붙일 때가 아니면 높인다, 보탠다, 늘린다를 '더한다'로 뭉뚱그린다. |
| `ko.tic.evidence-grade` | ko | 과다 어휘 | B | 0.6 | - | '증거 등급' 같은 조어. 읽는 사람이 처음 보는 말을 만들어 쓴다. |
| `ko.tic.grade-bare` | ko | 과다 어휘 | C | 0.3 | - | '등급'이 한 글에 자주 나온다. 실제 등급 제도가 아닌 곳에서 분류나 수준을 '등급'으로 부른다. |
| `ko.tic.anchor` | ko | 과다 어휘 | B | 0.5 | - | '기준점'. 비교 대상이나 출발점을 '기준점'이라는 측량 용어로 부른다. |
| `ko.tic.same-meaning` | ko | 과다 어휘 | B | 0.55 | - | '같다는 뜻이다'. 앞 문장을 다시 풀어 같은 말을 되풀이한다. |
| `ko.tic.means-that` | ko | 과다 어휘 | C | 0.4 | - | '~라는 뜻입니다'가 되풀이된다. 앞 문장을 한 번 더 풀어 말한다. |
| `ko.tic.numbering` | ko | 과다 어휘 | B | 0.45 | - | '첫 줄', '둘째 줄', '하나는', '둘은'처럼 번호를 매겨 항목을 짚는다. |
| `ko.tic.section-word` | ko | 과다 어휘 | B | 0.5 | - | '절'. 문서의 부분이나 문법의 한 덩어리를 '절'이라는 학술 용어로 가리킨다('이 절에서는', '있는 절은'). |
| `ko.tic.a-set` | ko | 과다 어휘 | B | 0.55 | - | '한 벌', '두 벌', '세 벌'. 숫자 뒤에 '벌'을 붙여 옷이 아닌 것을 세는 단위로 쓴다('규칙 두 벌'). |
| `any.markup.oaicite` | any | 누출된 마크업 | A | 1.0 | safe | 누출된 인용 토큰. |
| `any.markup.turn-ref` | any | 누출된 마크업 | A | 1.0 | safe | 누출된 도구 참조 토큰. |
| `any.markup.private-use` | any | 누출된 마크업 | A | 1.0 | safe | 비공개 영역 인용 표지. |
| `any.placeholder.lorem` | any | 빈 자리표시자 | A | 0.8 | - | 더미 문구. |
| `any.format.emoji-lead` | any | 서식 신호 | B | 0.5 | standard | 줄머리 이모지(불릿, 제목). |
| `any.format.emoji-any` | any | 서식 신호 | C | 0.3 | strong | 본문 이모지. |
| `any.format.bold-lead` | any | 서식 신호 | B | 0.5 | strong | 불릿마다 굵은 라벨로 시작한다. |
| `any.format.bold-line` | any | 서식 신호 | C | 0.3 | - | 굵은 글씨만 있는 줄이 제목 구실을 한다. |
| `any.format.hashtags` | any | 서식 신호 | C | 0.3 | - | 해시태그 묶음. |
| `any.format.heading-title-case` | any | 서식 신호 | C | 0.3 | - | 제목이 모두 대문자로 시작한다(제목식 대문자). |
| `any.hygiene.nbsp` | any | 보이지 않는 문자 | B | 0.0 | safe | 줄바꿈 없는 공백 문자가 섞였다. |
| `any.hygiene.zero-width` | any | 보이지 않는 문자 | B | 0.0 | safe | 보이지 않는 문자(너비 0, 연자 부호)가 섞였다. |
