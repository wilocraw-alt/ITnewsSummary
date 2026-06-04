# gate-checklist.md — ideate 게이트 체크리스트 (실행 인스턴스)

## 요약 (사용자용)

- 발굴 1회 실행마다 복사해서 쓰는 **체크리스트**. 각 게이트 통과를 기록.
- 게이트 질문·기준의 정의는 `.claude/skills/ideate/gate.md` 참조.

---

**Usage**: copy this into the ideation record for a run and tick each gate as it passes. Note the user's actual decision next to each — this is the audit trail of "사용자가 무엇에 합의했는가".

---

## Run header

- 희망(원문 한 줄): 
- 모호도: ☐ Vague  ☐ Fuzzy  ☐ Clear
- 모드: ☐ aimux(워커 위임)  ☐ solo(매니저 단독)
- 날짜: 

## Gates

- [ ] **G0 — 의도 확인** (after S0)
  - 제시한 프레이밍: 
  - 사용자 결정: ☐ 승인  ☐ 보정 요청 → 재프레이밍
- [ ] **G1 — 방법 승인** (after S1)
  - 선택 방법(2~3) + 각 미지수: 
  - 사용자 결정: ☐ 승인  ☐ auto-pass(Clear)  ☐ 변경 요청
- [ ] **G2 — 컨셉 확정** (after S3)
  - 추천 컨셉 / 대안: 
  - 루브릭 점수 요약: 
  - 사용자 결정: ☐ 확정  ☐ 보정  ☐ 다른 후보  ☐ 추진 가치 없음(중단)
- [ ] **G3 — 설계도 승인** (after S4)
  - 산출 PROJECT.md 경로: 
  - 추천 profile: 
  - 사용자 결정: ☐ 확정  ☐ 수정 요청

## Exit

- [ ] PROJECT.md 최종 확정 → `claude/intake.md`로 인계
- [ ] 종료 NOTE를 work.log에 기록(적용 방법론·확정 컨셉·추천 profile)
- 라운드 수(S1~S3 반복): ___ / 3 (cap)
