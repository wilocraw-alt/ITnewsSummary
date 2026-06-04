# profile: data — Data collection, scraping, ETL

## 요약 (사용자용)

- 외부 데이터 수집·가공·변환·보고용 Excel 생성·알림 전송 등.
- 크롤링은 사람처럼: 정상 UA, 랜덤 지연(1~3초), 동시 요청 제한.
- 장시간 작업에는 `status.sh` / `check_status.py` 필수.
- 공공 연구데이터(KISTI 등)는 AS-IS 현황 조사 중심, 임의 해결 방안 제시 X.

---

**Project type**: collecting external data, transformation, generating Excel reports, sending notifications.

---

## 1. Deliverables

- Raw data: `data/input/` (gitignored).
- Processed output: `data/output/` — JSONL, SQLite, Excel.
- Logs: `logs/YYYY-MM-DD.jsonl` (one file per day).
- Notifications: Telegram bot — Korean, no emoji, ≤ 200 chars recommended.

---

## 2. Default tool stack

- Data: `pandas`, `openpyxl`, `sqlite3`.
- Scraping: `requests`, `httpx`, `beautifulsoup4`. Dynamic pages: `Playwright` (only after user agreement).
- Finance: `FinanceDataReader` first; Naver Finance crawl as fallback.
- Notifications: `python-telegram-bot`.
- External APIs / sites (KRX, Naver Finance, Telegram Bot API, etc.) must be listed in PROJECT.md.

---

## 3. Scraping / crawling rules

- **Behave like a human**: normal User-Agent, random delays (1–3 s), bounded concurrency.
- On 403 / 429: try mitigations **first** — header tuning, sticky sessions, Referer. Escalate to the user only if those fail.
- When the user pastes a browser-devtools cURL, **convert to Python `requests`** as step zero.
- Pages that require JS rendering: agree on the tool (Playwright, etc.) with the user up front.

---

## 4. Storage rules

- Intermediate results in SQLite; final output in JSONL or Excel.
- Excel column headers may be Korean. Sheet layout: specified in PROJECT.md.
- Korean text in UTF-8 (no BOM). If cp949 compatibility is required, declare it in PROJECT.md.
- Excel files that will open on Windows: check encoding compatibility.

---

## 5. Workflow

```
1. Confirm target schema and source
2. Small-sample (N = 10–100) collection and validation
3. Full collection + progress monitoring        → status.sh / check_status.py
4. Transformation / aggregation
5. Output generation + notification
```

Long-running work must ship with a status script — see `core.md §4` and `implement.md §8`.

---

## 6. Domain note — Public R&D data (KISTI etc.)

- AS-IS systems (eGovFramework, Spring, MyBatis, PostgreSQL / Oracle): treat as **survey / fact-finding**.
  Don't propose remediation unless explicitly asked.
- HWPX templates: parse / generate XML directly. Don't depend on Hancom Office.
- Identifier, metadata, PII-encryption issues: **read the relevant policy document first**.

---

## 7. References

- General implementation rules: `implement.md`
- Token efficiency (large logs / CSVs): `token-efficiency.md`
