# llm-performance.md — LLM performance practices

## 요약 (사용자용)

- 추론은 영어로, 사용자 응답은 한국어. 한국어 텍스트 분석은 예외(한국어로 사고).
- 비자명한 작업은 단계 분해(Chain-of-Thought) 후 진행.
- 추측·환각 금지. 모르면 검증하거나 묻는다.
- 코드 작성 후 자체 점검: 입력 경계·타입·사이드이펙트·요구사항 누락.
- 작업 격리(서브에이전트)로 메인 추론 보호.

---

**When to read**: before reasoning-heavy work — design, debugging, deep analysis.
Routine file edits or formulaic responses don't need this.

These are **internal operating rules** that help produce more accurate, consistent results.
Independent of the user-facing response language.

---

## 1. Think in English

- The model's pre-training distribution is heavily English-dominant.
  For complex work, **reason internally in English** for higher accuracy.
- **User-facing output stays in Korean** (CLAUDE.md §0).
- Apply to:
  - Code analysis, algorithm design, debug reasoning.
  - Planning, step decomposition.
  - Computing tool-call arguments.
- Exception — think in Korean when:
  - Analyzing or summarizing Korean text.
  - Judging Korean tone or nuance.
  - Inferring intent from a Korean user message.

---

## 2. Chain-of-thought — decompose, then act

- For non-trivial work, don't answer in one shot. **Break it into steps** and verify each as you go.
- For reasoning-heavy work (design, migration, multi-file refactor), **externalize** the plan via the `Plan` agent or `ExitPlanMode`.
- At each step, briefly state "assumptions / observations / conclusions so far" — bad assumptions get caught early.

---

## 3. Distinguish guesses from facts

- If you don't know, **say so or verify**. No plausible hallucination.
- No unsourced assertions. Cite code / files as `file_path:line`.
- When API or library usage is unclear, fetch the official docs via `WebFetch` and quote.
- Library versions and function signatures: import + `dir` / `help` is faster and more accurate than guessing.

---

## 4. Self-check

After writing code, **re-read it** and check:
- Input edges (empty, `None`, large, non-ASCII).
- Type consistency, index ranges.
- Did you miss any user requirement?
- Are side effects within the intended scope?

For small changes, execute immediately and let the result speak.
Don't stop at type-check passes. Full procedure: `verify.md`.

---

## 5. Clear instructions and examples (recommended user-prompt patterns)

This section describes patterns the **user** can follow for better results.
From Claude's side, when a user prompt is vague, **restate using these patterns and confirm**.

- **Affirmative beats negative**: "vertical key:value" > "no tables".
- **Specify output format**: length, format, tone ("under 200 words", "JSON", "Korean report").
- **Add few-shot examples**: one or two example I/O pairs sharply increase format accuracy.
- **Assign a role**: "as a code reviewer", "from a security review perspective".
- **Repeat critical constraints at the end**: the model is more sensitive to the prompt's tail (recency).

---

## 6. Context priority and placement

- Put the **most important rules and constraints** short, at the top of CLAUDE.md or the tail of the user message.
- Don't load long reference docs in full — excerpt per `token-efficiency.md`.
- Strip obsolete decisions or stale debates — noise hurts reasoning.

---

## 7. Task isolation (sub-agents)

- When the domain differs or only the result matters, **isolate** the work in a sub-agent.
  Main reasoning stays focused.
- When isolating, tell the agent:
  1. Goal (one sentence).
  2. What is already confirmed.
  3. Output format and length.

---

## 8. Determinism and reproducibility

- For tasks needing same-input → same-output (data transforms, report generation), eliminate randomness and time dependence; **specify sort keys**.
- When code uses randomness, **fix seeds** (`random.seed`, `numpy.random.seed`) and **log the seed**.
