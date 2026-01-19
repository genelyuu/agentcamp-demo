# AgentCamp Task Backlog

> **Generated from Technical Strategy Consulting Report** | 2026-01-19
> **Total Tickets:** 47 | **Estimated Total:** 180+ hours

---

## Sprint Overview

| Sprint | Focus Area | Tickets | Priority |
|--------|-----------|---------|----------|
| Sprint 1 | Security & Stability | 12 | P0 |
| Sprint 2 | Data & Infrastructure | 10 | P0-P1 |
| Sprint 3 | Testing & Quality | 8 | P1 |
| Sprint 4 | LLM Enhancement | 9 | P1-P2 |
| Sprint 5 | Scalability & Performance | 8 | P2-P3 |

---

## Sprint 1: Security & Stability (P0)

| Ticket ID | Title | Description | Acceptance Criteria | Estimate | Dependencies |
|-----------|-------|-------------|---------------------|----------|--------------|
| SEC-001 | API Key 환경변수 마이그레이션 | API 키를 session_state에서 환경변수로 이전 | `.env` 파일에서 API 키 로드, session_state에 키 미노출 | 2h | - |
| SEC-002 | Streamlit Secrets 설정 | `.streamlit/secrets.toml` 기반 시크릿 관리 구현 | `st.secrets`로 API 키 접근 가능 | 1h | SEC-001 |
| SEC-003 | Input Validation 추가 (app.py) | 사용자 입력 필드에 Pydantic 검증 추가 | 모든 text_input에 길이/형식 검증 적용 | 3h | - |
| SEC-004 | Input Validation 추가 (orchestrator.py) | 질문 입력에 sanitization 적용 | XSS/Injection 방지 로직 구현 | 2h | SEC-003 |
| SEC-005 | User ID 검증 로직 | user_id 입력값 검증 및 정규화 | 영문/숫자만 허용, 길이 제한 (3-20자) | 1h | SEC-003 |
| LOG-001 | loguru 패키지 추가 | requirements.txt에 loguru 추가 | `pip install` 성공 | 0.5h | - |
| LOG-002 | 로깅 설정 모듈 생성 | `logger.py` 모듈 생성 및 포맷 설정 | JSON 포맷, 파일/콘솔 출력 | 2h | LOG-001 |
| LOG-003 | app.py 로깅 적용 | 주요 액션에 로그 추가 | 모드 전환, 질문, 제출 시 로그 기록 | 2h | LOG-002 |
| LOG-004 | orchestrator.py 로깅 적용 | LLM 호출 전후 로깅 | 라우팅 결과, 응답 시간 기록 | 1.5h | LOG-002 |
| LOG-005 | llm_client.py 로깅 적용 | API 호출 로깅 | 요청/응답 토큰 수, 에러 로깅 | 1.5h | LOG-002 |
| ERR-001 | Sentry 통합 설정 | Sentry SDK 설치 및 초기화 | 에러 발생 시 Sentry 대시보드 전송 | 2h | LOG-002 |
| ERR-002 | 글로벌 예외 핸들러 구현 | 앱 레벨 예외 처리 래퍼 | 예상치 못한 에러 시 사용자 친화적 메시지 | 2h | ERR-001 |

---

## Sprint 2: Data & Infrastructure (P0-P1)

| Ticket ID | Title | Description | Acceptance Criteria | Estimate | Dependencies |
|-----------|-------|-------------|---------------------|----------|--------------|
| DB-001 | Supabase 프로젝트 설정 | Supabase 프로젝트 생성 및 연결 정보 확보 | Connection string 획득 | 1h | - |
| DB-002 | Organization 테이블 스키마 | `organizations` 테이블 DDL 작성 | company, role, tools, rubric 컬럼 | 1h | DB-001 |
| DB-003 | Knowledge 테이블 스키마 | `knowledge_items` 테이블 DDL 작성 | id, source, tag, text, created_at 컬럼 | 1h | DB-001 |
| DB-004 | Sessions 테이블 스키마 | `user_sessions` 테이블 DDL 작성 | user_id, adapt_score, risk_score, tasks_done 컬럼 | 1h | DB-001 |
| DB-005 | Supabase 클라이언트 모듈 | `db_client.py` 생성 | Supabase Python SDK 연결 구현 | 2h | DB-001 |
| DB-006 | storage.py 리팩토링 (Organization) | `get_org`, `set_org` Supabase 연동 | JSON 대신 DB 읽기/쓰기 | 2h | DB-005 |
| DB-007 | storage.py 리팩토링 (Knowledge) | `get_knowledge`, `set_knowledge` Supabase 연동 | JSON 대신 DB 읽기/쓰기 | 2h | DB-006 |
| DB-008 | storage.py 리팩토링 (Sessions) | `get_sessions`, `set_sessions` Supabase 연동 | JSON 대신 DB 읽기/쓰기 | 2h | DB-007 |
| DB-009 | Migration 스크립트 작성 | 기존 JSON → DB 마이그레이션 | 기존 데이터 무손실 이전 | 3h | DB-008 |
| DB-010 | Fallback to JSON 로직 | DB 연결 실패 시 JSON 폴백 | DB 오류 시에도 앱 동작 | 2h | DB-008 |

---

## Sprint 3: Testing & Quality (P1)

| Ticket ID | Title | Description | Acceptance Criteria | Estimate | Dependencies |
|-----------|-------|-------------|---------------------|----------|--------------|
| TEST-001 | pytest 설정 | pytest, pytest-cov 설치 및 설정 | `pytest.ini` 생성, 테스트 실행 가능 | 1h | - |
| TEST-002 | agents.py 유닛 테스트 | `get_twins()` 테스트 | 4개 Twin 반환 검증, 필드 검증 | 2h | TEST-001 |
| TEST-003 | orchestrator.py 유닛 테스트 | `route_agent()` 테스트 | 키워드별 라우팅 정확성 검증 | 3h | TEST-001 |
| TEST-004 | llm_client.py 유닛 테스트 | MockLLMClient 테스트 | Mock 응답 포맷 검증 | 2h | TEST-001 |
| TEST-005 | storage.py 유닛 테스트 | CRUD 함수 테스트 | 파일 읽기/쓰기 정확성 검증 | 2h | TEST-001 |
| TEST-006 | ingestion.py 유닛 테스트 | `extract_knowledge()` 테스트 | 태그 분류 정확성 검증 | 2h | TEST-001 |
| TEST-007 | scoring.py 유닛 테스트 | `simple_review()` 테스트 | 점수 계산 로직 검증 | 2h | TEST-001 |
| TEST-008 | CI/CD 파이프라인 구축 | GitHub Actions 워크플로우 | PR 시 자동 테스트 실행 | 3h | TEST-002~007 |

---

## Sprint 4: LLM Enhancement (P1-P2)

| Ticket ID | Title | Description | Acceptance Criteria | Estimate | Dependencies |
|-----------|-------|-------------|---------------------|----------|--------------|
| LLM-001 | Streaming Response 구현 (Claude) | Claude API streaming 적용 | 토큰 단위 실시간 출력 | 4h | - |
| LLM-002 | Streaming Response 구현 (OpenAI) | OpenAI API streaming 적용 | 토큰 단위 실시간 출력 | 3h | LLM-001 |
| LLM-003 | Streaming UI 컴포넌트 | `st.write_stream()` 적용 | 응답 생성 중 타이핑 효과 | 2h | LLM-001, LLM-002 |
| LLM-004 | 대화 히스토리 저장 구조 | 세션별 대화 기록 스키마 | messages[] 배열 저장 | 2h | - |
| LLM-005 | Multi-turn Context 구현 | 이전 대화 컨텍스트 포함 | 최근 5턴 대화 참조 | 4h | LLM-004 |
| LLM-006 | LLM Response 캐싱 | Redis/메모리 캐시 구현 | 동일 질문 캐시 히트 | 4h | - |
| LLM-007 | 프롬프트 템플릿 외부화 | `prompts/` 디렉토리 생성 | YAML/JSON 기반 프롬프트 관리 | 3h | - |
| LLM-008 | Model Routing 로직 | 질문 복잡도 기반 모델 선택 | 단순 질문은 Haiku, 복잡 질문은 Sonnet | 4h | - |
| LLM-009 | Token Usage 트래킹 | 요청/응답 토큰 수 기록 | 일별/사용자별 토큰 사용량 집계 | 3h | LOG-005 |

---

## Sprint 5: Scalability & Performance (P2-P3)

| Ticket ID | Title | Description | Acceptance Criteria | Estimate | Dependencies |
|-----------|-------|-------------|---------------------|----------|--------------|
| PERF-001 | app.py Pages 구조 분리 | Streamlit multipage 적용 | `pages/admin.py`, `pages/newhire.py`, `pages/dashboard.py` | 4h | - |
| PERF-002 | 공통 컴포넌트 모듈화 | `components/` 디렉토리 생성 | sidebar, header 등 재사용 컴포넌트 | 3h | PERF-001 |
| PERF-003 | Async LLM Client 리팩토링 | `aiohttp` 기반 비동기 호출 | 동시 요청 처리 가능 | 6h | - |
| PERF-004 | Knowledge Chunking 구현 | 대용량 텍스트 청크 분할 | 1000자 단위 청크, 오버랩 200자 | 3h | - |
| PERF-005 | Batch Ingestion 구현 | 대량 데이터 일괄 처리 | 1000개 이상 아이템 처리 가능 | 3h | PERF-004 |
| PERF-006 | agents.py 외부 설정화 | YAML 기반 Twin 정의 | `config/twins.yaml` 로드 | 2h | - |
| PERF-007 | orchestrator.py DI 적용 | Dependency Injection 패턴 | 글로벌 변수 제거, 테스트 용이성 | 4h | - |
| PERF-008 | API Layer 분리 (FastAPI) | REST API 엔드포인트 구축 | `/api/v1/question`, `/api/v1/submit` | 8h | PERF-007 |

---

## Ticket Status Legend

| Status | Description |
|--------|-------------|
| `TODO` | 미착수 |
| `IN_PROGRESS` | 진행 중 |
| `REVIEW` | 리뷰 대기 |
| `DONE` | 완료 |
| `BLOCKED` | 차단됨 |

---

## Priority Definitions

| Priority | Description | SLA |
|----------|-------------|-----|
| **P0** | Critical - 보안/안정성 이슈 | 즉시 |
| **P1** | High - 핵심 기능 개선 | 1-2 주 |
| **P2** | Medium - 성능/UX 개선 | 1 개월 |
| **P3** | Low - Nice-to-have | 분기 |

---

## Dependencies Graph

```
SEC-001 ──► SEC-002
SEC-003 ──► SEC-004 ──► SEC-005
LOG-001 ──► LOG-002 ──► LOG-003
                    ──► LOG-004
                    ──► LOG-005 ──► LLM-009
LOG-002 ──► ERR-001 ──► ERR-002

DB-001 ──► DB-002 ──► DB-005 ──► DB-006 ──► DB-007 ──► DB-008 ──► DB-009
       ──► DB-003                                              ──► DB-010
       ──► DB-004

TEST-001 ──► TEST-002 ──► TEST-008
         ──► TEST-003
         ──► TEST-004
         ──► TEST-005
         ──► TEST-006
         ──► TEST-007

LLM-001 ──► LLM-003
LLM-002 ──►
LLM-004 ──► LLM-005

PERF-001 ──► PERF-002
PERF-004 ──► PERF-005
PERF-007 ──► PERF-008
```

---

## Quick Reference: File → Tickets Mapping

| File | Related Tickets |
|------|-----------------|
| `app.py` | SEC-003, LOG-003, PERF-001, PERF-002 |
| `agents.py` | TEST-002, PERF-006 |
| `orchestrator.py` | SEC-004, LOG-004, TEST-003, PERF-007 |
| `llm_client.py` | LOG-005, TEST-004, LLM-001~003, PERF-003 |
| `storage.py` | DB-006~010, TEST-005 |
| `ingestion.py` | TEST-006, PERF-004, PERF-005 |
| `scoring.py` | TEST-007 |
| `requirements.txt` | LOG-001, TEST-001, DB-005 |
| `.env` (new) | SEC-001 |
| `.streamlit/secrets.toml` | SEC-002 |
| `logger.py` (new) | LOG-002 |
| `db_client.py` (new) | DB-005 |
| `prompts/` (new) | LLM-007 |
| `config/twins.yaml` (new) | PERF-006 |
| `pages/` (new) | PERF-001 |
| `components/` (new) | PERF-002 |

---

## Estimation Summary

| Sprint | Tickets | Total Hours | Team Size (1 dev) |
|--------|---------|-------------|-------------------|
| Sprint 1 | 12 | ~20h | 3-4 days |
| Sprint 2 | 10 | ~17h | 2-3 days |
| Sprint 3 | 8 | ~17h | 2-3 days |
| Sprint 4 | 9 | ~29h | 4-5 days |
| Sprint 5 | 8 | ~33h | 5-6 days |
| **Total** | **47** | **~116h** | **~3 weeks** |

---

*Document Version: 1.0 | Last Updated: 2026-01-19*
