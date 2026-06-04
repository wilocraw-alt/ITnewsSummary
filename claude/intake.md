# intake.md — New-project intake

## 요약 (사용자용)

- PROJECT.md 필수 항목이 비어 있을 때 실행되는 짧은 대화 흐름.
- 요청 메모 요약 → 파악 질문(최대 3개) → profile 추천 → 기술 스택 제안 → PROJECT.md 자동 작성.
- 요청 메모 자체가 비어 있으면 → 작성 안내 후 멈춤.

---

**When to read**: at session start, if PROJECT.md required fields are empty.

> 요청이 구체적 스펙이 아니라 **모호한 희망**이면, 먼저 `/ideate`(`claude/ideate.md`)로 발산→수렴 구체화한 뒤
> 채워진 PROJECT.md를 가지고 이 인테이크로 오세요. 이미 채워져 있으면 가볍게 확인만 하고 plan으로 진행합니다.

---

## 1. What intake does

Reads what the user wrote in PROJECT.md's "요청 메모" (request memo) and fills the structured sections through a short dialogue.

Three areas to fill:
- **Project info** — name, purpose, input, output, key constraints.
- **profile** — dev / research / docs / data — Claude recommends, user confirms.
- **Tech stack** — start from the profile's defaults, propose adaptations, user confirms.

---

## 2. Trigger conditions

Run intake if **any** of the following holds:

- A required field in PROJECT.md "프로젝트 정보" (`이름` / `목적` / `입력` / `출력`) is empty.
- "요청 메모" has text but the rest is still template defaults.
- The user says things like "처음부터 시작", "새 프로젝트", "PROJECT 채워줘".

If "요청 메모" itself is empty → ask the user to write it first, then halt.

---

## 3. Procedure

### 3.1 Read the request memo

1. Read "요청 메모" and **summarize in 2–3 sentences**.
   - Confirm in the form "~을 하시려는 거죠?".
   - Collect any unclear points and ask them together in §3.2.

### 3.2 Discovery questions (only if needed)

Ask **at most three** questions at once. If more than three would come to mind, pick the three most important.

Priority order:
1. Input data shape — where it comes from, what format.
2. Output shape — what must be produced.
3. Key constraints — unusual environment, access limits, deadlines.

**Don't ask about the tech stack here** — Claude proposes it.

### 3.3 Profile recommendation

Extract keywords from the request memo and §3.2 answers, then recommend a profile.

Keyword map (heuristic):
- **dev**: 앱 / 라이브러리 / CLI / 스크립트 / 자동화 / 코드 / 함수
- **research**: 조사 / 분석 / 논문 / 보고서 / 문헌 / 리뷰 / 연구 / 동향
- **docs**: 문서 / README / 매뉴얼 / 번역 / 정리 / 가이드
- **data**: 크롤링 / 스크래핑 / 수집 / 엑셀 / ETL / 시세 / 알림 / DB

Present the top candidate **and** one alternative.

Format:
```
이 프로젝트는 다음 profile이 맞아 보입니다:
  추천 : data — 외부 데이터 수집·텔레그램 알림이 핵심
  대안 : dev  — 코드 산출 중심으로 본다면

profile에 따라 적용되는 산출물·도구 규칙(`profiles/{profile}.md`)이 달라집니다.
이대로 갈까요, 아니면 다른 profile로 변경할까요?
```

Record the confirmed profile in PROJECT.md's `profile` field.

### 3.4 Tech-stack proposal

Take the confirmed profile's defaults (`profiles/{profile}.md §2`) as a starting point, adapt to project specifics, propose **with reasons**.

Format:
```
언어/런타임  : Python 3.11
환경 관리    : .venv — 프로젝트 내부 가상환경(python -m venv .venv), 폴더와 함께 이동
주요 라이브러리
  - 데이터   : pandas, openpyxl
  - 스크래핑 : requests + BeautifulSoup4
데이터 저장  : SQLite (중간) + JSONL (최종)
외부 연동    : 없음

→ 이대로 가도 될까요? 바꿀 항목 있으면 말씀해 주세요.
```

Present alternatives **only** when the choice is genuinely consequential (e.g., dynamic-rendering requirement). Don't list options for the sake of it.

### 3.5 Write PROJECT.md

Once the user confirms, fill the structured sections immediately.

- Use `Edit` to fill each blank.
- **Preserve** the original "요청 메모" wording.
- Domain notes and output-format sections: fill only if applicable; otherwise delete those sections.

### 3.6 Render the project README (replace the scaffold README)

The root `README.md` shipped with the scaffold describes **make_Harness itself** — it does not fit a copied project. Once PROJECT.md is filled, replace it:

1. Read `templates/project/README.md`.
2. Fill every `{{...}}` from the matching PROJECT.md field (이름·목적·입력·출력·주요 제약·경로·기술 스택). Drop rows whose source field is empty rather than leaving `{{...}}`.
3. **Overwrite** the root `README.md` with the rendered result (the scaffold reference still lives in `DESIGN.md`).
4. Strip the template's `<!-- ... -->` usage comments.

> 스캐폴드를 직접 개발 중일 때(= 이 프로젝트가 make_Harness 자체일 때)는 이 단계를 건너뛴다.

### 3.7 Announcement

Right after writing PROJECT.md and the project README:

```
인테이크 완료.
채운 항목    : 이름, 목적, profile, 입력, 출력, 기술 스택, 경로
적용 profile : [dev | research | docs | data]
README       : 프로젝트용으로 교체됨
다음         : 작업 요청을 주시면 시작하겠습니다.
```

---

## 4. Principles

- **One question at a time.** If grouping is needed, up to three in a numbered list.
- **Explain tech-term choices.** The user may not know the stack; give a one-line reason for each pick.
- **Minimize guessing.** Always confirm input / output shape. Fill the rest with sensible defaults and note they can be revised.
- **Don't over-ask.** Things you'll learn naturally while coding (column names, control-flow details) belong **in the work**, not in intake.
