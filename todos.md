# AgentCamp Demo - 업무 처리 기록

## 프로젝트 정보
- **프로젝트명**: AgentCamp Demo (AI-Powered OJT Digital Twins Platform)
- **기준 문서**: TRD_v2.md
- **처리 일시**: 2026-01-16

---

## 업무 처리 요약

| Phase | 처리 방식 | 설명 |
|-------|----------|------|
| Phase 1 | 병렬 처리 | 독립 모듈 5개 동시 생성 (T-001 ~ T-005) |
| Phase 2 | 순차 처리 | agents.py 의존 모듈 (T-006) |
| Phase 3 | 순차 처리 | 전체 모듈 의존 UI + 병렬 데이터 (T-007 ~ T-009) |
| Phase 4 | 순차 처리 | 문서화 (T-010) |
| Phase 5 | 병렬/순차 | LLM 연동 (T-011 ~ T-015) |

---

## 티켓 처리 상세

| 티켓 ID | 업무명 | 파일/경로 | 의존성 | 처리 방식 | 처리 순서 | 상태 |
|---------|--------|-----------|--------|----------|----------|------|
| T-001 | requirements.txt 생성 | `requirements.txt` | 없음 | 병렬 | 1 | ✅ 완료 |
| T-002 | storage.py 구현 | `storage.py` | 없음 | 병렬 | 1 | ✅ 완료 |
| T-003 | agents.py 구현 | `agents.py` | 없음 | 병렬 | 1 | ✅ 완료 |
| T-004 | ingestion.py 구현 | `ingestion.py` | 없음 | 병렬 | 1 | ✅ 완료 |
| T-005 | scoring.py 구현 | `scoring.py` | 없음 | 병렬 | 1 | ✅ 완료 |
| T-006 | orchestrator.py 구현 | `orchestrator.py` | T-003 | 순차 | 2 | ✅ 완료 |
| T-007 | app.py 구현 | `app.py` | T-001~T-006 | 순차 | 3 | ✅ 완료 |
| T-008 | data/ 초기 파일 생성 | `data/*.json` | 없음 | 병렬 | 3 | ✅ 완료 |
| T-009 | 데모 입력 데이터 생성 | `data/demo_inputs/*` | 없음 | 병렬 | 3 | ✅ 완료 |
| T-010 | todos.md 문서화 | `todos.md` | T-001~T-009 | 순차 | 4 | ✅ 완료 |
| T-011 | requirements.txt LLM 패키지 추가 | `requirements.txt` | 없음 | 병렬 | 5 | ✅ 완료 |
| T-012 | llm_client.py 생성 | `llm_client.py` | T-003 | 병렬 | 5 | ✅ 완료 |
| T-013 | orchestrator.py LLM 모드 지원 | `orchestrator.py` | T-012 | 순차 | 6 | ✅ 완료 |
| T-014 | app.py LLM 설정 UI 추가 | `app.py` | T-013 | 순차 | 7 | ✅ 완료 |
| T-015 | Git commit & push | - | T-011~T-014 | 순차 | 8 | ✅ 완료 |

---

## 의존성 그래프

```
Phase 1 (병렬)
├── T-001: requirements.txt
├── T-002: storage.py
├── T-003: agents.py
├── T-004: ingestion.py
└── T-005: scoring.py

Phase 2 (순차 - T-003 의존)
└── T-006: orchestrator.py ──depends──> T-003 (agents.py)

Phase 3 (순차/병렬 혼합)
├── T-007: app.py ──depends──> T-001~T-006 (전체 모듈)
├── T-008: data/*.json (병렬)
└── T-009: demo_inputs/* (병렬)

Phase 4 (순차)
└── T-010: todos.md ──depends──> T-001~T-009

Phase 5 (LLM 연동 - 병렬/순차)
├── T-011: requirements.txt (병렬)
├── T-012: llm_client.py ──depends──> T-003 (병렬)
├── T-013: orchestrator.py ──depends──> T-012 (순차)
├── T-014: app.py ──depends──> T-013 (순차)
└── T-015: Git commit & push ──depends──> T-011~T-014
```

---

## 생성된 파일 목록

| 파일 경로 | 용도 | 티켓 |
|----------|------|------|
| `requirements.txt` | 의존성 목록 | T-001 |
| `storage.py` | JSON 저장소 모듈 | T-002 |
| `agents.py` | Digital Twin 정의 | T-003 |
| `ingestion.py` | 데이터 수집 파이프라인 | T-004 |
| `scoring.py` | 루브릭 기반 평가 | T-005 |
| `orchestrator.py` | 질문 라우팅 & 답변 생성 | T-006 |
| `app.py` | Streamlit UI 메인 | T-007 |
| `data/org.json` | 조직 설정 | T-008 |
| `data/knowledge.json` | 지식 베이스 | T-008 |
| `data/sessions.json` | 사용자 세션 | T-008 |
| `data/demo_inputs/meeting_transcript.txt` | 회의 STT 샘플 | T-009 |
| `data/demo_inputs/slack_export.txt` | Slack 대화 샘플 | T-009 |
| `todos.md` | 업무 처리 기록 | T-010 |
| `llm_client.py` | LLM 클라이언트 추상화 | T-012 |

---

## 모듈별 책임 (SOLID 원칙)

| 모듈 | 단일 책임 (SRP) | 의존 방향 |
|------|----------------|----------|
| `storage.py` | 데이터 영속화 | 없음 (기반 모듈) |
| `agents.py` | Twin 페르소나 정의 | 없음 (기반 모듈) |
| `ingestion.py` | 텍스트 → 지식 추출 | 없음 (기반 모듈) |
| `scoring.py` | 제출물 평가 | 없음 (기반 모듈) |
| `llm_client.py` | LLM API 추상화 | agents.py |
| `orchestrator.py` | 라우팅 + 답변 생성 | agents.py, llm_client.py |
| `app.py` | UI 렌더링 | 전체 모듈 |

---

## 실행 방법

```bash
cd agentcamp-demo
pip install -r requirements.txt
streamlit run app.py
```

---

## 버전 정보

- **Python**: 3.10+
- **Streamlit**: >= 1.37.0
- **Pydantic**: >= 2.8.0
- **python-dotenv**: >= 1.0.0
- **anthropic**: >= 0.18.0 (LLM 연동)
- **openai**: >= 1.0.0 (LLM 연동)
