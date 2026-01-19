# Changelog

All notable changes to AgentCamp project will be documented in this file.

## [1.4.0] - 2026-01-19

### 답변 신뢰도 향상 (Answer Trustworthiness Improvement)

이번 버전은 Digital Twin의 답변 신뢰도와 평가의 타당성을 높이는 2가지 핵심 기능을 추가합니다.

---

### A. Explainable Routing (ADR-108)

**문제**: 라우팅 결정이 블랙박스 → "왜 이 트윈이 선택되었나" 설명 불가

**해결**:
- `schemas/routing.py`: `Candidate`, `RoutingResult` 스키마 신규
  - 매칭 키워드, 신뢰도 점수, 대안 후보 포함
  - `confidence_percent`, `has_alternatives` 프로퍼티
  - `format_reason_display()` UI 표시용 포맷
- `core/orchestrator.py`:
  - `ROUTING_LEXICON`: 트윈별 확장된 키워드 사전
  - `route_agent_with_reason()`: 설명가능 라우팅 함수
  - `_match_keywords()`, `_calculate_routing_score()` 헬퍼 함수
- `core/twin_renderer.py`: 트윈별 구조화된 응답 렌더러 신규
  - `StructuredSection`, `StructuredAnswer` 데이터클래스
  - `render_ceo_answer()`: CEO 의사결정 구조 (결론→근거→리스크→액션)
  - `render_pm_answer()`: PM 체크리스트 구조 (문제→가설→AC→우선순위)
  - `render_frontend_answer()`: FE UX 구조 (흐름→에러→구현→개선)
  - `render_backend_answer()`: BE 증거 구조 (현상→원인→검증→해결)
  - `render_twin_answer()`: 통합 디스패처
- `app.py`: 라우팅 근거 UI 추가
  - 신뢰도 퍼센트 표시
  - 매칭 키워드 목록
  - 대안 후보 표시
  - 트윈별 구조화된 응답 렌더링

**SOLID 원칙**:
- SRP: 라우팅/렌더링/스키마 각 모듈 분리
- OCP: 새 트윈 추가 시 렌더러 확장 가능
- DIP: Pydantic/Dataclass 스키마에 의존

---

### B. Structured Rubric Scoring (ADR-109)

**문제**: 키워드 매칭 기반 평가 → "키워드 게이밍" 가능, 구조적 평가 부재

**해결**:
- `schemas/rubric.py`: 4칸 구조 평가 스키마 신규
  - `ChecklistItem`: 체크리스트 항목
  - `RubricColumn`: 루브릭 칸 (25점 만점)
  - `RubricReviewResult`: 4칸 통합 평가 결과
  - `calculate_grade()`: 등급 계산 함수
  - 기본 체크리스트 팩토리 함수들
- `core/evaluation.py`:
  - `rubric_review()`: 4칸 구조 평가 함수
  - `_evaluate_column()`: 칸별 평가 로직
  - `_validate_submission_structure()`: 구조 검증 (키워드 게이밍 방지)
  - 칸별 패턴 매칭 정의 (`_CAUSE_PATTERNS`, `_REPRODUCTION_PATTERNS`, etc.)
- `app.py`: 4칸 체크리스트 UI 추가
  - 4칸 점수 시각화
  - 칸별 체크리스트 표시
  - 종합 피드백 및 등급
  - 누락된 요소 목록

**4칸 구조**:
| 칸 | 설명 | 점수 |
|----|------|------|
| 원인 분석 (Cause) | 문제 현상, 근본 원인, 인과관계 | 25점 |
| 재현 방법 (Reproduction) | 재현 스텝, 환경/조건, 구체성 | 25점 |
| 재발 방지 (Prevention) | 단기 대응, 장기 개선, 모니터링 | 25점 |
| 증거 (Evidence) | 로그/스크린샷, 메트릭, 타임라인 | 25점 |

**키워드 게이밍 방지**:
- 최소 길이 검증 (100자)
- 문장 구조 검증 (3문장)
- 구조화된 포맷 권장

---

### Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `schemas/routing.py` | **New** | Candidate, RoutingResult 스키마 |
| `schemas/rubric.py` | **New** | ChecklistItem, RubricColumn, RubricReviewResult 스키마 |
| `core/twin_renderer.py` | **New** | 트윈별 구조화된 응답 렌더러 |
| `core/orchestrator.py` | Modified | route_agent_with_reason() 추가 |
| `core/evaluation.py` | Modified | rubric_review() 4칸 구조 평가 추가 |
| `core/__init__.py` | Modified | 새 함수/클래스 export |
| `schemas/__init__.py` | Modified | 새 스키마 export |
| `app.py` | Modified | 라우팅 근거/4칸 체크리스트 UI 추가 |

---

### ADR (Architecture Decision Records)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-108 | Explainable Routing | Accepted |
| ADR-109 | Structured Rubric Scoring | Accepted |

---

## [1.3.0] - 2026-01-19

### 심사 대비 개선 (Hackathon Review Preparation)

이번 버전은 해커톤 심사에서 지적될 수 있는 3가지 핵심 비판점을 해결합니다.

---

### A. Citation Transparency (ADR-106)

**문제**: 업로드된 지식이 실제로 답변/리뷰에 사용되는지 UI에서 확인 불가

**해결**:
- `schemas/response.py`: `Citation`, `AnswerResult`, `KeywordMatch`, `ReviewResult` 스키마 추가
- `core/citation.py`: 지식 인용 서비스 모듈 신규
  - `find_relevant_knowledge()`: 질문과 관련된 지식 검색
  - `extract_keyword_context()`: 키워드 주변 컨텍스트 추출
- `core/orchestrator.py`:
  - `answer_with_citations()`: 인용 정보 포함 답변 반환
  - `route_and_answer()`: 라우팅 + 답변 + 인용 통합 함수
- `core/evaluation.py`:
  - `review_with_evidence()`: 키워드 매칭 근거 포함 리뷰 반환
- `app.py`: UI에 "📚 참고된 지식" 및 "🔍 키워드 매칭 상세" expander 추가

**SOLID 원칙**:
- SRP: Citation 로직을 별도 모듈로 분리
- OCP: 새로운 매칭 알고리즘 추가 시 확장 가능
- DIP: Pydantic 스키마에 의존

---

### B. Digital Twin Differentiation (ADR-107)

**문제**: 트윈별 출력이 동일한 템플릿 → "캐릭터만 다른 것" 오해 가능

**해결**:
- `agents.py`:
  - `ResponseFormat` 데이터클래스 추가 (greeting, sections, closing, emoji, tone)
  - 트윈별 고유 응답 포맷 정의
- `llm_client.py`:
  - `MockLLMClient`: 트윈별 차별화된 섹션 구조 생성
  - `ClaudeLLMClient`, `OpenAILLMClient`: 시스템 프롬프트에 응답 포맷 지시 추가

**트윈별 포맷**:
| Twin | Emoji | Sections | Tone |
|------|-------|----------|------|
| Sam Lee (CEO) | 🎯 | 결론 → 근거 → 리스크 → 다음 액션 | direct |
| JH Kim (PM) | 📋 | 문제 정의 → 성공 조건 → 체크리스트 → 우선순위 | friendly |
| Seul Kim (FE) | 🎨 | 사용자 흐름 → 에러 케이스 → 구현 포인트 → 개선 제안 | friendly |
| Jin Park (BE) | 🔧 | 현상 분석 → 원인 가설 → 검증 방법 → 해결 방안 | analytical |

---

### C. Deployment Strategy Clarification

**문제**: README에 Streamlit Cloud로 명시되어 있으나, 사용자 요청은 Vercel

**해결**:
- `README.md`: Deployment 섹션 추가
  - Streamlit Cloud 단일화 명시
  - Vercel 미지원 사유 설명 (Streamlit 네이티브 지원 X)
  - 배포 방식 비교표 추가

---

### Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `schemas/response.py` | **New** | Citation, AnswerResult, ReviewResult 스키마 |
| `core/citation.py` | **New** | 지식 인용 서비스 |
| `core/orchestrator.py` | Modified | Citation 포함 응답 함수 추가 |
| `core/evaluation.py` | Modified | 키워드 매칭 근거 포함 리뷰 함수 추가 |
| `core/__init__.py` | Modified | 새 함수 export |
| `schemas/__init__.py` | Modified | 새 스키마 export |
| `agents.py` | Modified | ResponseFormat 추가, 트윈별 포맷 정의 |
| `llm_client.py` | Modified | 트윈별 차별화 응답 생성 |
| `app.py` | Modified | Citation/Keyword Match UI 추가 |
| `README.md` | Modified | Deployment 섹션 추가 |

---

### ADR (Architecture Decision Records)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-106 | Citation Transparency | Accepted |
| ADR-107 | Twin Differentiation | Accepted |

---

## [1.2.0] - 2026-01-19

### Added
- Architecture refactoring (core/, schemas/, tests/)
- ADR-101: UI/Core Boundary Separation
- ADR-102: Pydantic Data Contracts
- ADR-104: Protocol-based LLM Interface
- LOG-002: Loguru logging
- ERR-001: Sentry error handling
- 126 unit tests

### Changed
- Module structure reorganization
- Default OJT role: Project Manager

---

## [1.0.0] - 2026-01-19

### Added
- Initial release
- 4 Digital Twin agents (Sam Lee, JH Kim, Seul Kim, Jin Park)
- Mock/Claude/OpenAI LLM support
- Admin/NewHire/Dashboard modes
- Knowledge ingestion pipeline
- Rubric-based evaluation
