# Changelog

All notable changes to AgentCamp project will be documented in this file.

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
