<p align="center">
  <img src="https://img.shields.io/badge/AgentCamp-OJT_AI-blue?style=for-the-badge" alt="AgentCamp"/>
  <img src="https://img.shields.io/badge/Offline--first-100%25-green?style=for-the-badge" alt="Offline-first"/>
  <img src="https://img.shields.io/badge/LLM-Enhanced-orange?style=for-the-badge" alt="LLM Enhanced"/>
  <br/><br/>
  <a href="https://agentcamp-demo-kvnmnjquyv6jfmwqhjt4f4.streamlit.app/">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo"/>
  </a>
</p>

<h1 align="center">AgentCamp</h1>

<p align="center">
  <strong>AI로 바꾸는 온보딩(OJT) 운영</strong><br/>
  <code>회사 지식 → 질문 → 리뷰 → 지표</code> 폐루프
</p>

<p align="center">
  <a href="https://agentcamp-demo-kvnmnjquyv6jfmwqhjt4f4.streamlit.app/"><strong>🚀 Live Demo</strong></a> •
  <a href="#-tldr">TL;DR</a> •
  <a href="#-핵심-흐름">핵심 흐름</a> •
  <a href="#-제품-개요">제품 개요</a> •
  <a href="#-사업성">사업성</a> •
  <a href="#-기술">기술</a> •
  <a href="#-quick-start">Quick Start</a>
</p>

---

## TL;DR

> **AgentCamp**는 조직의 '일상 텍스트'를 자동으로 **회사 룰·실수 패턴·프로세스**로 정리하고,
> 그 지식이 **질문 답변 → 제출 리뷰 → HR 대시보드**까지 즉시 연결되는 **OJT 운영 AI**입니다.

<br/>

### "AI로 바꾸는 일과 업무"

실제 업무에서 AI가 바꿔야 하는 건 "한 번 멋진 답변"이 아니라 **업무 운영의 비용 구조**입니다.

| 비용 유형 | 문제 |
|:----------|:-----|
| **반복 질문 비용** | 신입은 같은 질문을 반복하고, 리드/시니어는 같은 답을 반복 |
| **리뷰 품질 편차 비용** | 제출물 평가 기준이 사람마다 달라 "재작업" 발생 |

<br/>

> **AgentCamp는 이 지점을 "문서화"가 아니라 운영 시스템으로 바꿉니다.**

<br/>

### 지식이 답변에서 끝나지 않고, 평가와 지표로 연결된다

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   회사 지식      │ ──▶ │   질문 답변      │ ──▶ │   제출 리뷰      │
│  (룰/실수/프로세스) │     │   (근거로 인용)   │     │   (기준으로 반영)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   운영 지표      │
                                               │ (리스크/적응도)   │
                                               └─────────────────┘
```

<p align="center">
  <strong>AI는 "대화"가 아니라 "업무 운영"을 바꿉니다.</strong>
</p>

---

## 핵심 흐름

```
📁 팀의 회의/슬랙 텍스트 업로드
      │
      ▼
📚 회사 지식 (규칙/실수/프로세스)로 변환
      │
      ▼
🤖 신입 질문 → 4명 Digital Twin(CEO/PM/FE/BE) 중 적절한 역할이 답변
      │
      ▼
✅ 제출물 → 원인/재현/재발방지/증거 기준으로 자동 리뷰
      │
      ▼
📊 HR/리드 → 적응도/리스크/질문량/완료율 한 화면에서 확인
```

---

## 제품 개요

> **3모드로 완결되는 OJT 운영**

<br/>

### 1️⃣ Admin (회사 세팅/데이터 업로드)

| 기능 | 설명 |
|:-----|:-----|
| 회사/직무 세팅 | 회사명, 직무, 루브릭(데모) 설정 |
| 지식 업로드 | 회의 STT/Slack 텍스트 → 규칙/실수/프로세스 자동 추출 |
| Active Knowledge | **Top-3** "운영에 쓰이는 지식" 고정 표시 |

<br/>

### 2️⃣ New Hire (OJT 실행)

| 기능 | 설명 |
|:-----|:-----|
| 오늘의 미션 | 업무 컨텍스트 포함된 미션 수령 |
| 질문하기 | Digital Twin 라우팅 + 근거(키워드/스코어) 노출 |
| 제출하기 | 구조 루브릭 점수/피드백 + 회사 지식 인용 |

<br/>

### 3️⃣ Dashboard (HR/리드 운영)

| 기능 | 설명 |
|:-----|:-----|
| 통합 현황 | 질문량/트윈 호출/재제출/완료 업무/적응도/리스크 |
| 리스크 규칙 | 지표의 의미를 명시하여 고정 |

---

## 사업성

### 문제는 보편적이고 반복된다

| 조직 유형 | 문제 |
|:----------|:-----|
| **스타트업/중소팀** | 온보딩 문서가 없거나 최신성 유지 안됨 |
| **성장기 조직** | 제품/프로세스 변화 속도 빨라 사람이 따라가기 어려움 |
| **원격·분산팀** | Slack/회의에 지식 흩어짐, 온보딩 개인 의존적 |

<br/>

### AgentCamp의 ROI (정량화가 쉬움)

| ROI 항목 | 효과 |
|:---------|:-----|
| 반복 질문 감소 | 리드/시니어 시간 절감 |
| 리뷰 기준 표준화 | 재작업 감소 |
| 리스크 조기 감지 | 근거 부족/재현 부재 등 패턴 추적 |
| 온보딩 기간 단축 | 성과 도달 시간 단축 |

<br/>

### 비즈니스 모델 (해커톤 이후 확장)

| 플랜 | 내용 |
|:-----|:-----|
| **B2B SaaS** | 온보딩/교육 대상 인원 기준 과금 (per seat) |
| **팀 플랜** | Slack/회의 연동 + 지식 거버넌스 + 감사 로그 |
| **Enterprise** | SSO, 권한관리, 개인정보/보안 정책, 모델 선택 |

---

## 기술

### Offline-first + LLM Enhanced

| 모드 | 설명 |
|:-----|:-----|
| **Offline (기본)** | API Key 없이도 100% 동작 — 데모 안정성 최우선 |
| **LLM Enhanced** | Key가 있으면 답변/추출/리뷰 품질 업그레이드 |
| **Fail-safe** | LLM 실패/지연 시 즉시 오프라인 모드로 폴백 |

<br/>

### Tech Stack

```
┌────────────────────────────────────────────┐
│  Frontend      │  Streamlit               │
├────────────────────────────────────────────┤
│  Backend       │  Python                  │
├────────────────────────────────────────────┤
│  LLM (Optional)│  OpenAI / Anthropic      │
├────────────────────────────────────────────┤
│  Deployment    │  Minimal dependencies    │
└────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 실행
streamlit run app.py
```

---

## 2-Min Demo Script

> **Click-by-click 데모 시나리오**

<br/>

| Step | Mode | Action |
|:----:|:-----|:-------|
| 1 | **Admin** | STT/Slack 텍스트 업로드 → "지식 추출 & 저장" → Active Knowledge Top-3 확인 |
| 2 | **New Hire** | 질문 입력 → 라우팅 근거/후보 확인 → 트윈 답변(역할별 스키마) + 지식 인용 확인 |
| 3 | **New Hire** | 제출 → 구조 루브릭(원인/재현/재발/증거) 체크 + 점수/피드백 확인 |
| 4 | **Dashboard** | 질문량/업무완료/리스크/적응도 확인 |

---

<p align="center">
  <strong>Team Veluga</strong><br/>
  <sub>Built with Streamlit + Python</sub>
</p>
