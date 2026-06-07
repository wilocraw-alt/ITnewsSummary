# PROJECT.md

## 요청 메모

- AI 소식들을 정리해서 보여주는 프로젝트
- 미국, 중국, 한국 등에서 발생하는 여러 모델이나 프로모션의 정보들을 취합하여 전달
- 구독에 대한 가격 프로모션 정보는 반드시 있으면 좋음.
- 정식 뉴스도 포함되어야 하지만, 커뮤니티, SNS, X, thread, youtube 등 다양한 개인들이 올리는 콘텐츠에서 주목받는 경향을 조사하여 전달 받고 싶어.
- 여러 방법을 이용하여 하루에 2번 정도 정리해서 뿌려줄 수 있도록 scheduleA을 정리하고 싶어. 

### 추가요청 - 2026-06-08 월
- 게시판으로 된 community에 대해서 목록, 개별항목 상세보기가 필요한 case에 대한 처리가 필요할 때 기존의 html의 community가 제대로 동작하지 않아. https://arca.live/b/alpaca 을 사례로 추가해줘. 
- antropic news에서 Introducing Claude Opus 4.8 의 경우가 지속적으로 노출되는 문제가 생겼어. 최초로 그 정보가 저장된 다음에 일주일 넘게 게속 반복적으로 나오는 것은 막을 수 있는 방법이 있었으면 좋겠어.

---

## 프로젝트 정보

- **이름**: ITnewsSummary
- **목적**: 미국·중국·한국 AI 모델 출시, 성능 변화, 요금제·구독 프로모션, 기업 발표, 커뮤니티/SNS 화제를 매일 아침/저녁 2회 요약하여 로컬 Markdown 파일로 저장하고 Email로 발송
- **상태**: 아이디에이션 완료, 구현 전
- **profile**: dev
- **입력**: AI 뉴스 소스 (공식 블로그 RSS, 테크 미디어 RSS, 가격 페이지, X/SNS, 커뮤니티, YouTube)
- **출력**: 로컬 Markdown 파일 + Email 발송 (아침/저녁)
- **주요 제약**: Semi-automated (Human-in-the-loop), 가격 프로모션 우선 포함, 한국어 요약

---

## 기술 스택

- **언어/런타임**: Python 3.11+
- **환경 관리**: venv
- **주요 라이브러리**: requests/httpx, beautifulsoup4, openai/anthropic SDK, smtplib/email
- **데이터 저장**: 로컬 파일시스템 (Markdown + JSON 메타)
- **외부 연동**: LLM API (OpenAI/Anthropic), Email SMTP, RSS 피드
- **실행 환경**: cron / systemd timer

---

## 경로 · 실행

- **입력 위치**: `sources/` (소스 설정 파일)
- **출력 위치**: `output/` (날짜별 Markdown 파일)
- **진입점**: `main.py` — collect → summarize → format → send
- **환경 구축**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

---

## GitHub

- **리모트 계정**: 
- **레포명**: ITnewsSummary
- **브랜치 정책**: main (직접)
- **커밋 메시지**: 한국어 간결 요약

---

## 도메인 메모

(해당 시에만 작성 — 없으면 삭제)

---

## 산출물 포맷

(프로젝트별 특수 포맷 규칙 — 없으면 삭제)
