# ITnewsSummary — Clustering Refactor (2026-06-04)

## 변경 사항

### summarizer.py — 개별 번역 → 주제별 클러스터링 + 그룹 요약

**As-Is (before):**
- 40개 아이템 각각을 LLM에 개별 전송 → 40회 LLM 호출
- 동일 주제 뉴스가 분산되어 중복 요약 발생
- 소요 시간: ~40분 (Ollama gemma4:e4b 기준)

**To-Be (after):**
1. `cluster_items()`: 전체 아이템 제목을 한 번에 LLM에 전송 → 주제별 그룹화
2. `summarize_cluster()`: 클러스터당 1회 LLM 호출로 통합 한국어 요약 생성
3. 결과: **40회 → (1 + N)회** (1 클러스터링 + N개 클러스터 요약)
4. 소요 시간: ~40분 → ~2분

**추가된 함수:**
- `_llm_call()` — OpenAI/Anthropic 공통 호출 추상화
- `cluster_items()` — LLM 기반 주제 군집화
- `summarize_cluster()` — 군집별 통합 요약
- `extract_json_array()` — JSON 배열 추출

### formatter.py — 클러스터 출력 포맷

- `organize_items()` → `organize_clusters()`: 클러스터 단위 섹션 분류
- `generate_markdown()`: 클러스터별 주제명 + 통합 요약 + 소스 목록 출력
- HTML 템플릿: 클러스터 기반 레이아웃으로 변경

## 클러스터링 예시 (2026-06-04)

| 클러스터 | 아이템 수 | 영향도 |
|---|---|---|
| OpenAI 기술적 확장 및 AI 거버넌스 정책 수립 | 5 | HIGH |
| 거대 기술 기업의 AI 플랫폼 통합 및 산업 재편 동향 | 8 | HIGH |
| 지역 LLM 및 오픈소스 모델의 개인화/최적화 동향 | 25 | HIGH |
| 주요 기술 기업 및 블로그/뉴스룸 업데이트 활동 | 2 | HIGH |

## 파일 구조

```
ITnewsSummary/
├── summarizer.py      # 클러스터링 + 그룹 요약
├── formatter.py       # 클러스터 출력 포맷
├── main.py            # 파이프라인 (변경 없음)
├── collector.py       # 수집 (변경 없음)
├── sender.py          # 발송 (변경 없음)
└── output/YYYY-MM-DD/ # 생성된 Markdown/HTML/JSON
```

## LLM 호출 최적화

- **Before**: 40 items × 1 call = 40 calls, ~10-15s each
- **After**: 1 clustering call + 4 cluster summary calls = 5 calls
- **절감**: ~87.5% API 호출 감소, ~95% 시간 감소
