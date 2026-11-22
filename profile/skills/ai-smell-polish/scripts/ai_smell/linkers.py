"""문장을 잇는 말의 사전과 언어 판별. 규칙 파일이 아니라 분석기(cohesion.py)가 쓰는 데이터다.

품사표와 문법 개념표를 이렇게 옮겼다(출처와 근거는 docs/research.md 7절).
  접속사(기능사류)          conj  and, but, 그리고, そして   | 종속 접속사는 sub (because, although)
  접속부사(부사류)          adv   그러나, however, sin embargo, しかし
  전치사·조사가 이끄는 구   phrase because of, 그 때문에, そのため, por eso
  수사·순서어               ord   첫째, first, 次に, primero
  대명사·지시 관형사·한정사 ref   이/그, this, ce, dieser, この, 这  (관사 the/le/der는 너무 흔해서 세지 않는다)
  명사의 성·수·격·인칭      ref 목록에 굴절형을 모두 둔다(de dieser/diesem/diesen, ru этот/этого/этой, es este/esta/estos)
  굴절·교착                 ko·ja는 조사가 붙은 어절에서 조사를 떼고, ja·zh는 어절 구분이 없어 접두 일치로 본다
  의미(의외성·유표성)        relation: adversative가 '기대가 꺾임'(의외성)을 나타내는 표지다
관계는 Halliday & Hasan(1976)의 접속 네 갈래(추가·대조·인과·시간)에 환언을 더해 다섯으로 나눈다.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Dict, List, Optional, Tuple

RELATIONS = ("additive", "adversative", "causal", "temporal", "restate")
REL_KO = {"additive": "추가", "adversative": "대조·양보", "causal": "이유·결과", "temporal": "순서·시간",
          "restate": "환언·예시", "reference": "지시"}
REL_EN = {"additive": "addition", "adversative": "contrast", "causal": "cause/result", "temporal": "sequence",
          "restate": "restatement/example", "reference": "reference"}
LANG_NAME = {"ko": ("한국어", "Korean"), "en": ("영어", "English"), "ja": ("일본어", "Japanese"),
             "zh": ("중국어", "Chinese"), "es": ("스페인어", "Spanish"), "fr": ("프랑스어", "French"),
             "de": ("독일어", "German"), "pt": ("포르투갈어", "Portuguese"), "it": ("이탈리아어", "Italian"),
             "ru": ("러시아어", "Russian"), "other": ("기타 언어", "other language")}
SUPPORTED = tuple(k for k in LANG_NAME if k != "other")

# 문장 하나가 '짧다'고 보는 길이(한국어는 어절, 일본어·중국어는 글자, 나머지는 낱말)와 문단 평균의 중간 길이.
# 영어 낱말 8개 안팎을 짧은 문장으로 보는 실무 기준(docs/research.md 7절)에서 출발했고, 11월 실측으로 언어별로 다시 맞췄다
# (docs/evaluation.md): 사람 글(위키백과, 뉴스, 소설)에서 끊긴 단문 연속이 걸리는 비율이 5~10% 안에 들도록 잡았다.
# 한국어는 6어절이 사람 글 10.6% 대 2025년 모델 글 25.3%로 가장 갈렸다(8어절은 21.2% 대 34.8%).
SHORT = {"ko": 6, "en": 9, "es": 10, "fr": 10, "pt": 10, "it": 10, "de": 7, "ru": 5, "ja": 14, "zh": 18, "other": 9}
RUN = {"ja": 4, "ru": 4, "zh": 4}
TIER2 = {"ko": (8, 5)}                            # 둘째 기준(길이, 연속). 한국어는 8어절 이하 5문장 연속도 센다: 사람 글 오탐 4.5%, 합집합 11.1%(6/3은 10.6%)                 # 끊긴 단문이 이만큼 이어져야 센다(기본 3). 사람 글 오탐이 5%를 넘던 언어
MEDIUM = {"ko": 9, "en": 13, "es": 14, "fr": 14, "pt": 14, "it": 14, "de": 12, "ru": 11, "ja": 40, "zh": 30, "other": 13}

# 줄마다: 종류 관계 항목|항목|...  (앞쪽이 흔한 말이라 menu()가 앞에서부터 고른다)
_RAW: Dict[str, str] = {
    "ko": """
adv additive 그리고|또|또한|게다가|더구나|더욱이|아울러|더불어|나아가|그뿐 아니라|이와 함께|덧붙여|그 밖에
adv adversative 하지만|그러나|그런데|그렇지만|그래도|다만|반면|반면에|오히려|대신|그럼에도|그럼에도 불구하고|그렇더라도|물론
adv causal 그래서|따라서|그러므로|그러니까|그러니|그리하여|그 결과|결과적으로|왜냐하면|그 때문에|이 때문에|그렇기 때문에|이로 인해|그렇다면|그러면|그럼
adv temporal 먼저|우선|다음으로|이어서|마지막으로|끝으로|그다음|그 다음|그 뒤|그 후|이후|그때|그러다가|그러자|이윽고
ord temporal 첫째|둘째|셋째|넷째
adv restate 즉|다시 말해|요컨대|예를 들어|예컨대|가령|특히|무엇보다|사실|실제로|구체적으로|결국|결론적으로|정리하면
ref reference 이|그|저|이런|그런|이러한|그러한|이와|그와|이것|그것|이들|그들|이때|그때|이처럼|그처럼|이렇게|그렇게|여기|거기|이곳|그곳|이날|그날|그녀|해당|앞서
""",
    "en": """
conj additive and|also|plus
adv additive moreover|furthermore|additionally|in addition|besides|likewise|similarly|what's more|not to mention|on top of that
conj adversative but|yet
adv adversative however|still|nevertheless|nonetheless|on the other hand|in contrast|by contrast|conversely|instead|otherwise|even so|that said|then again|on the contrary|rather
sub adversative although|though|while|whereas|even though
conj causal so
adv causal therefore|thus|hence|consequently|accordingly|as a result|that is why|for this reason
sub causal because|since|as|if|unless|once|when
adv temporal then|next|afterwards|afterward|later|meanwhile|subsequently|eventually|finally|lastly|at first|in the end|first of all|first|second|third
sub temporal after|before|until|while
adv restate for example|for instance|in other words|that is|specifically|in particular|namely|indeed|in fact|actually|of course|after all|in short|in conclusion
ref reference this|that|these|those|such|it|they|he|she|its|their|his|her|both|another|the same
""",
    "ja": """
adv additive そして|また|さらに|それに|しかも|そのうえ|その上|おまけに|なお|かつ
adv adversative しかし|だが|でも|ところが|けれども|けれど|それでも|ただし|とはいえ|もっとも|一方|逆に|むしろ|といっても
adv causal だから|それで|そのため|したがって|ゆえに|よって|そこで|すると|そうすると|なぜなら|というのも|そのせいで
adv temporal それから|次に|まず|最初に|やがて|その後|のちに|最後に|ついに|そのとき|その時
adv restate つまり|すなわち|要するに|たとえば|例えば|いわば|実際|実は|特に|言い換えれば|ちなみに
ref reference この|その|あの|これ|それ|あれ|ここ|そこ|こうした|そうした|このように|そのように|彼女|彼ら|彼
""",
    "zh": """
adv additive 而且|并且|此外|另外|同时|还有|再说|不仅如此|除此之外|况且|加之
adv adversative 但是|可是|然而|不过|但|却|反而|相反|尽管如此|话虽如此|与此相反
adv causal 所以|因此|因而|于是|因为|由于|既然|结果|从而|为此|这样一来|如此一来
adv temporal 然后|接着|随后|首先|其次|最后|后来|起初|之后|与此同时|最终|终于
adv restate 也就是说|换句话说|即|例如|比如|比方说|总之|总的来说|其实|事实上|实际上|具体来说|尤其|特别是
ref reference 这些|那些|这样|那样|这种|那种|这个|那个|它们|他们|她们|这|那|它|他|她|此|该|其
""",
    "es": """
conj additive y|e
adv additive además|también|asimismo|igualmente|incluso
conj adversative pero|sino
adv adversative sin embargo|no obstante|en cambio|por el contrario|ahora bien|aun así
sub adversative aunque|mientras|si bien
adv causal por eso|por lo tanto|por tanto|así que|entonces|de modo que|como resultado|en consecuencia|por esta razón|así pues
sub causal porque|ya que|puesto que|como|si|cuando
adv temporal luego|después|finalmente|primero|segundo|por último|mientras tanto|más tarde|al principio|a continuación
adv restate es decir|o sea|por ejemplo|en otras palabras|en resumen|de hecho|en realidad|en particular|en concreto
ref reference este|esta|estos|estas|esto|ese|esa|esos|esas|eso|aquel|aquella|aquello|él|ella|ellos|ellas|tal
""",
    "fr": """
conj additive et
adv additive de plus|en outre|par ailleurs|aussi|également|d'ailleurs
conj adversative mais|or
adv adversative pourtant|cependant|toutefois|néanmoins|en revanche|par contre|au contraire|certes
sub adversative bien que|quoique|alors que
adv causal donc|ainsi|alors|par conséquent|c'est pourquoi|en effet|du coup|de ce fait|dès lors
sub causal car|parce que|puisque|comme|si|quand
adv temporal puis|ensuite|enfin|d'abord|premièrement|deuxièmement|finalement|entre-temps|plus tard|au début
adv restate c'est-à-dire|autrement dit|par exemple|en d'autres termes|en résumé|en fait|en particulier|notamment|bref
ref reference ce|cet|cette|ces|celui|celle|ceux|celles|cela|ça|ceci|il|elle|ils|elles|tel|telle
""",
    "de": """
conj additive und
adv additive außerdem|zudem|ferner|darüber hinaus|auch|ebenso|ebenfalls|überdies
conj adversative aber|doch|sondern
adv adversative jedoch|dennoch|trotzdem|allerdings|hingegen|dagegen|stattdessen|andererseits|indessen
sub adversative obwohl|während|obgleich
adv causal deshalb|daher|deswegen|also|folglich|somit|darum|infolgedessen|aus diesem grund|dadurch
sub causal weil|da|denn|wenn|falls
adv temporal dann|danach|anschließend|zuerst|zunächst|schließlich|später|inzwischen|zuletzt|erstens|zweitens
adv restate das heißt|nämlich|zum beispiel|beispielsweise|mit anderen worten|kurz gesagt|tatsächlich|insbesondere|übrigens
ref reference dieser|diese|dieses|diesem|diesen|dies|jener|jene|jenes|er|sie|es|solche|solch|derselbe|dieselbe
""",
    "pt": """
conj additive e
adv additive além disso|também|ademais|igualmente
conj adversative mas
adv adversative porém|contudo|no entanto|entretanto|todavia|por outro lado|ao contrário
sub adversative embora|enquanto
adv causal por isso|portanto|logo|então|assim|por esse motivo|em consequência
sub causal porque|pois|já que|como|se|quando
adv temporal depois|em seguida|primeiro|finalmente|por fim|enquanto isso|mais tarde|a seguir
adv restate ou seja|isto é|por exemplo|em outras palavras|em resumo|na verdade|de fato|em particular
ref reference este|esta|isto|esse|essa|isso|aquele|aquela|aquilo|ele|ela|eles|elas
""",
    "it": """
conj additive e
adv additive inoltre|anche|in più|per di più|altresì
conj adversative ma
adv adversative però|tuttavia|eppure|invece|comunque|anzi|d'altra parte|al contrario
sub adversative nonostante|sebbene|mentre
adv causal quindi|perciò|dunque|pertanto|di conseguenza|per questo motivo|così
sub causal perché|siccome|poiché|se|quando
adv temporal poi|dopo|infine|prima|intanto|successivamente|in seguito|alla fine|innanzitutto|per prima cosa
adv restate cioè|ovvero|ad esempio|per esempio|in altre parole|in sintesi|in effetti|infatti|in particolare
ref reference questo|questa|questi|queste|quello|quella|quelli|ciò|egli|ella|essi|lui|lei|loro
""",
    "ru": """
conj additive и|а также
adv additive кроме того|к тому же|также|тоже|притом|более того
conj adversative но|а|да
adv adversative однако|зато|тем не менее|всё же|наоборот|впрочем
sub adversative хотя|несмотря на то
adv causal поэтому|следовательно|итак|таким образом|из-за этого|в результате|ведь
sub causal потому что|так как|если|когда|поскольку
adv temporal затем|потом|после этого|сначала|во-первых|во-вторых|наконец|тем временем|позже
adv restate то есть|иначе говоря|например|в частности|в общем|в итоге|на самом деле|действительно
ref reference этот|эта|это|эти|этого|этой|этому|этим|этом|этих|этими|тот|та|то|те|того|той|тому|тем|том|тех|такой|такая|такое|такие|он|она|оно|они|его|её|их
""",
}

_STOP = {
    "en": "the of and to is that it for with as on are this be was not have from by which they an at or but we you "
          "he she his her has had were will can would their there been more one all about",
    "es": "el los las del y en por con para una un es se como pero más su sus lo está qué al muy ya también sin "
          "sobre entre cuando donde son fue hay esta este esto",
    "fr": "le les des et est dans qui pas sur au aux ce il elle ne une pour que nous vous ils elles mais ou avec "
          "sont fait plus par comme cette ces leur son sa ses",
    "de": "der die das und ist nicht ein eine zu den mit von auf für sich im dem auch wir sie er es aber wenn oder "
          "wie hat haben werden wird sind kann können nur noch bei aus nach über zwei jeder seine einer einem einen als",
    "pt": "os as em uma não é do da dos das no na mais mas com para ele ela são também foi está isso muito já ser "
          "ou por seu sua entre quando",
    "it": "il lo gli di che è sono del della dei delle nel più ma per non con una anche come se questo questa "
          "quella suo sua molto già fra tra",
}
_STOP_SETS = {k: set(v.split()) for k, v in _STOP.items()}
_JOSA = ("에서는", "으로는", "에는", "에서", "으로", "에게", "까지", "부터", "는", "은", "도", "만", "엔", "의", "이", "가", "을", "를", "에", "로", "와", "과")
_PUNCT = " \t\r\n\"'“”‘’()[]{}«»<>,，、.。!?！？;:：…—–-*#>•「」『』（）【】"


class _Lex:
    """언어 하나의 사전. 한 줄에 한 번만 정규화해서 보관한다."""

    def __init__(self, lang: str, raw: str):
        self.lang = lang
        self.items: Dict[str, Tuple[str, str]] = {}
        for line in raw.strip().splitlines():
            kind, rel, words = line.split(" ", 2)
            for w in words.split("|"):
                w = w.strip().lower()
                if w and w not in self.items:
                    self.items[w] = (kind, rel)
        self.max_chars = max(len(w) for w in self.items)
        self.max_tokens = max(w.count(" ") + 1 for w in self.items)
        self.by_rel: Dict[str, List[str]] = {}      # menu()용: 지시어를 뺀 말을 관계별로, 적힌 순서대로
        for line in raw.strip().splitlines():
            kind, rel, words = line.split(" ", 2)
            if kind != "ref":
                self.by_rel.setdefault(rel, []).extend(words.split("|"))


_LEX: Dict[str, _Lex] = {}


def lexicon(lang: str) -> Optional[_Lex]:
    if lang not in _RAW:
        return None
    if lang not in _LEX:
        _LEX[lang] = _Lex(lang, _RAW[lang])
    return _LEX[lang]


def _script(ch: str) -> str:
    o = ord(ch)
    if 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F:
        return "ko"
    if 0x3040 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF:
        return "kana"
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
        return "han"
    if 0x0400 <= o <= 0x04FF:
        return "cyr"
    if ch.isalpha() and o < 0x250:
        return "latin"
    return "other" if ch.isalpha() else ""


def detect(text: str) -> str:
    """문단 하나의 언어. 문자 종류로 한국어·일본어·중국어·러시아어를 가르고, 라틴 문자는 흔한 낱말로 가린다."""
    c = Counter(s for s in map(_script, text) if s)
    total = sum(c.values())
    if total == 0:
        return "other"
    if c["ko"] >= max(6, 0.1 * total):                 # 영문 이름이 많이 섞인 한국어 문단도 한국어다
        return "ko"
    if c["kana"] >= 0.1 * total:
        return "ja"
    if c["han"] >= 0.5 * total:
        return "zh"
    if c["cyr"] >= 0.5 * total:
        return "ru"
    if c["latin"] >= 0.5 * total:
        words = re.findall(r"[^\W\d_]+", text.lower())
        score = {k: sum(1 for w in words if w in v) for k, v in _STOP_SETS.items()}
        best = max(score, key=lambda k: (score[k], k == "en"))
        return best if score[best] >= 2 and score[best] >= 0.1 * len(words) else "other"
    return "other"


def length_units(sentence: str, lang: str) -> int:
    """문장 길이. 일본어·중국어는 글자 수, 나머지는 공백으로 나눈 덩어리 수(한국어는 어절)."""
    if lang in ("ja", "zh"):
        return sum(1 for ch in sentence if unicodedata.category(ch)[0] in "LN")
    return sum(1 for t in sentence.split() if any(ch.isalnum() for ch in t))


def _norm(tok: str) -> str:
    return tok.strip(_PUNCT).lower().replace("’", "'")


def lead_link(sentence: str, lang: str) -> Optional[Tuple[str, str, str]]:
    """문장 첫머리가 앞 문장과 잇는 말이면 (종류, 관계, 찾은 말). 아니면 None."""
    lex = lexicon(lang)
    if lex is None:
        return None
    s = sentence.lstrip(_PUNCT + "0123456789")
    if lang in ("ja", "zh"):
        head = s[: lex.max_chars]
        for n in range(len(head), 0, -1):
            hit = lex.items.get(head[:n])
            if hit:
                return hit[0], hit[1], head[:n]
        return None
    toks = s.split()[: lex.max_tokens]
    for n in range(len(toks), 0, -1):
        head = " ".join(_norm(t) for t in toks[:n])
        hit = lex.items.get(head)
        if hit:
            return hit[0], hit[1], head
        if lang == "ko" and n == 1:
            for j in _JOSA:                      # 교착: 조사가 붙은 첫 어절은 조사를 떼고 본다
                if head.endswith(j) and len(head) > len(j):
                    hit = lex.items.get(head[: -len(j)])
                    if hit:
                        return hit[0], hit[1], head
    return None


def menu(lang: str, ui: str = "ko", per: int = 4) -> str:
    """관계별로 고른 접속부사·순서어 예시를 한 줄로. 검출 항목의 고치는 법과 프롬프트에 쓴다."""
    lex = lexicon(lang)
    if lex is None:
        return ""
    names = REL_KO if ui == "ko" else REL_EN
    parts = []
    for rel in RELATIONS:
        words = list(dict.fromkeys(lex.by_rel.get(rel, [])))[:per]
        if words:
            parts.append(f"{names[rel]}({'·'.join(words)})")
    return " ".join(parts) if ui == "ko" else "; ".join(parts)


def lang_name(lang: str, ui: str = "ko") -> str:
    return LANG_NAME.get(lang, LANG_NAME["other"])[0 if ui == "ko" else 1]


KIND_KO = {"adv": "접속부사", "conj": "접속사", "sub": "종속 접속사·접속어미형", "ord": "순서어", "ref": "대명사·지시어"}
KIND_EN = {"adv": "conjunctive adverb", "conj": "conjunction", "sub": "subordinator", "ord": "ordinal",
           "ref": "pronoun/demonstrative"}


def table(lang: str, ui: str = "ko") -> str:
    """언어 하나의 이어지는 말을 관계와 품사별로 정리해 준다. 윤문할 때 알맞은 말을 고르는 용도다."""
    raw = _RAW.get(lang)
    if raw is None:
        return ""
    names, kinds = (REL_KO, KIND_KO) if ui == "ko" else (REL_EN, KIND_EN)
    out = [f"[{lang_name(lang, ui)}]"]
    for line in raw.strip().splitlines():
        kind, rel, words = line.split(" ", 2)
        out.append(f"  {names[rel]:<10} {kinds[kind]:<14} {', '.join(words.split('|'))}")
    return "\n".join(out)
