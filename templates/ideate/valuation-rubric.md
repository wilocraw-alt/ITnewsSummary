# 아이디어 가치판정 루브릭 (Idea Valuation Rubric)

아이디어 발굴 과정에서 도출된 여러 후보안 중 하네스 프로젝트로 추진할 최적의 안을 선별하기 위한 정량적·정성적 평가 도구입니다. 이 루브릭은 수렴 단계(S3)에서 워커들의 검토 결과(VERIFY)를 종합하여 최종 의사결정을 내릴 때 사용됩니다.

---

## 1. Overview
This rubric provides a structured framework for the Manager to evaluate and compare candidate ideas generated during the divergence phase. It ensures that the transition from a vague "wish" to a concrete `PROJECT.md` is based on objective criteria rather than intuition alone.

## 2. Evaluation Criteria (1-5 Scale)

Each candidate is scored from 1 to 5 on the following four dimensions.

### 2.1 Feasibility (실현성)
*Can we build it?* Assessment of technical possibility, resource availability, and environmental constraints.
- **5 (Excellent)**: No technical unknowns; all resources available; fits perfectly in current environment.
- **3 (Fair)**: Minor technical hurdles; requires common libraries or external docs; low risk.
- **1 (Poor)**: Major technical unknowns; high resource costs; potential environment conflicts.

### 2.2 Impact (임팩트)
*Should we build it?* The magnitude of value, effectiveness, or improvement the project provides.
- **5 (Excellent)**: High utility; solves a major pain point; provides significant learning or output.
- **3 (Fair)**: Moderate utility; incremental improvement; clear but limited benefit.
- **1 (Poor)**: Negligible utility; "nice to have" but solves no real problem; low relevance.

### 2.3 Fit (적합도)
*Is it what we wanted?* Alignment with the user's original intent and the initial "wish" captured during intake.
- **5 (Excellent)**: Directly addresses the core wish; perfect alignment with user goals.
- **3 (Fair)**: Addresses the main goal but diverges in non-essential details.
- **1 (Poor)**: Concept has drifted significantly from the original intent.

### 2.4 Effort (노력 - Reversed Scoring)
*What does it cost?* Time, complexity, and mental load required. 
**Note**: Lower effort is better. For calculation, use **(6 - Measured Effort)** to normalize the score (e.g., Effort 1 → Score 5).
- **5 (Low Effort)**: Simple implementation; few steps; can be completed quickly.
- **3 (Medium Effort)**: Moderate complexity; requires standard planning and multiple turns.
- **1 (High Effort)**: Very complex; involves high risk of failure or extreme duration.

---

## 3. Scoring & Selection Logic

### 3.1 Calculation
- **Total Score** = Feasibility + Impact + Fit + (6 - Effort)
- **Max Score**: 20 points.

### 3.2 Decision Thresholds
- **16 - 20 (Promote)**: Highly recommended. Proceed to `PROJECT.md` definition immediately.
- **12 - 15 (Refine)**: Promising but has weaknesses. Iterate once more on the lowest-scoring criterion before deciding.
- **Below 12 (Park)**: Not viable at this time. Archive the idea in `AIMemory/` for future reference.

### 3.3 Tie-Breaking
If two candidates have the same total score, the **Fit** score takes priority. If still tied, the **Impact** score is the secondary tie-breaker.

---

## 4. Valuation Matrix (Example)

| Candidate Idea | Feasibility | Impact | Fit | Effort (Raw) | Total (Normalized) | Decision |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **A: Full-Auto App** | 2 | 5 | 5 | 5 | **13** | Refine (High Effort) |
| **B: Skill Template** | 5 | 4 | 5 | 2 | **19** | **Promote** |
| **C: Simple Doc** | 5 | 2 | 3 | 1 | **15** | Refine (Low Impact) |

---

## 5. Usage Context
The Manager applies this rubric during the **Convergence** phase. 
1. Collect reports from WORKERs (VERIFY/INSPECT).
2. Fill the matrix based on the evidence provided in the reports.
3. Present the matrix to the User for final Gate approval before finalizing `PROJECT.md`.
