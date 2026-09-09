# `docs/rebuild/validation/2026-09-09-repeated-comparison/summary.txt`

- 형식: `100644`
- 바이트: 1325
- SHA-256: `31f3c213f241bbcbde6c90cd5c40f9eb60db7ad146221b2d160aa927da947834`
- 인코딩: `utf-8`

```
비교 가능: True  막힌 이유: []

팔            모델                         자동채점   통과     매번통과     사람검토     평균초       과제코드실행
----------------------------------------------------------------------------------------
agy-gtg      gemini-3.8-flash-high        14   14      7/7        2      65      16/16
agy-plain    gemini-3.8-flash-high        14   14      7/7        2      58      14/16
claude-code  claude-sonnet-5              14   12      6/7        2      52      14/16
codex-cli    gpt-5.6-terra                14   13      6/7        2      91      16/16

사람 검토 사례(자동 채점 불가): ['inspect-only']

자동 채점 사례별 (통과/시도)
사례                       agy-gtg     agy-plain   claude-code     codex-cli
bounds                   2/2           2/2           2/2           2/2    
dead-code                2/2           2/2           2/2           2/2    
merge-records            2/2           2/2           2/2           2/2    
refactor-pricing         2/2           2/2           2/2           2/2    
report-export            2/2           2/2           2/2           2/2    
resume-export            2/2           2/2           0/2           1/2    
run-tests-only           2/2           2/2           2/2           2/2    
```
