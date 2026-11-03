# English

English AI prose has its own habits. Any one of them proves nothing, because people use these words too, but several in one paragraph read as machine-made. Rewrite the sentence rather than swapping a word for a synonym.

## Delete on sight

| Pattern | Do instead |
| --- | --- |
| `delve into`, `rich tapestry`, `testament to`, `navigate the complexities` | Use the plain verb and name the concrete thing |
| `It's important to note that`, `It's worth noting` | Delete the lead-in and state the point |
| `In today's fast-paced world`, `in the ever-evolving landscape` | Delete it and start with the fact |
| `game-changer`, `paradigm shift`, `unlock the full potential` | Say what changed and by how much |
| `adds depth to`, `adds a touch of` | Use a direct verb (`deepens`, `brings`) or describe the concrete fact |
| `sends a clear signal that`, `serves as a signal that` | State what is actually indicated (`indicates that`, `shows that`) |
| `happiness index`, `trust score` (abstract casual metrics) | Use plain terms (`level`) or describe the condition directly |
| `high information density`, `dense with` | Say `rich detail` or `rich in ...` |
| `In conclusion,`, `To sum up,` | Write the conclusion without the signpost |
| `I hope this helps`, `Feel free to`, `Great question` | Chat filler; it does not belong in a document |

## Fix them when they pile up

- Stock vocabulary such as `pivotal`, `seamless`, `robust`, `leverage`, `foster`, `underscore`, `showcase`, `multifaceted`, `holistic` and `cutting-edge`. Three in one paragraph is a tell, so use the ordinary word (`use` for `leverage`, `show` for `showcase`).
- Coupling clichés like `paired with`, `coupled with`, `hand in hand with`, and `two sides of the same coin`. Use `with` or state the concrete connection directly.
- Abstract measuring and spreading buzzwords: `gauge the impact/value/sentiment` (say `assess`, `measure`), `propagate across` (say `spread across`), `dissemination of` (say `distribution of`).
- Buzzword adverbs like `seamlessly integrates` (drop `seamlessly` and keep the verb) or `seamless automation`.
- Crude embedding slang like `hardcoded directly into` or `baked into` (use `written into` or `built into`).
- `serves as`, `stands as` and `acts as` where `is` would do.
- `not just X, but Y` and `It's not X. It's Y.` State Y unless you are correcting a misconception the reader actually holds.
- Lists of exactly three adjectives or benefits, again and again. Use the real count.
- `Additionally,`, `Moreover,` and `Furthermore,` opening sentence after sentence.
- `perfectly`, `flawless`, `production-ready`, `fully tested`, `guaranteed` and `all edge cases`. Attach the evidence and its scope, or drop the claim.
- Em dashes. A few are fine, but when every other sentence carries a dash-inserted aside the text reads as generated, so use commas, parentheses or a new sentence.

## Rhythm

Vary sentence length. Join sentences that belong together with `and`, `but`, `because`, `so` or `which`, and keep short sentences for emphasis or a turn in the argument. A paragraph in which every sentence has the same length and shape reads as generated even when no single word is a problem.

## Structure

Lead with the answer or the result. Skip the closing paragraph that restates the introduction, the bold phrase in every sentence and the emoji in headings. Keep bullet lists for items that are actually parallel, and tell a chain of reasons as prose.

## Checking

Run `prose` on English text the way you run it on Korean text. The phrases in the first table are blocked in English and Korean documents alike, and the pile-up rules above are reported as review signals. The 0 to 100 score is a rough density of the signals found. It was not calibrated on English, because the only labelled data (KatFish) is Korean, so read it as a trend inside one document and do not compare it with a Korean score or use it as a pass mark.

```bash
python3 "$GTG_RUNNER" prose --workspace /absolute/project/path README.md
```

When you polish a draft, add `--original draft.md`. It checks that numbers, quotes, URLs and code survived and reports the share of words that changed. It does not judge whether the English got better.

## Sources

- Wikipedia's "Signs of AI writing" page, maintained by WikiProject AI Cleanup.
- The English pattern packs in devswha/patina (MIT, commit 9ad44bc).
