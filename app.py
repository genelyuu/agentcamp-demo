"""
app.py - Streamlit UI 메인 엔트리포인트
책임: Admin / New Hire / Dashboard 모드 UI 렌더링
"""
import streamlit as st

from storage import get_org, set_org, get_knowledge, set_knowledge, get_sessions, set_sessions
from agents import get_twins
from ingestion import extract_knowledge
from orchestrator import route_agent, answer_with_twin
from scoring import simple_review

# 페이지 설정
st.set_page_config(
    page_title="AgentCamp (Veluga) - OJT Digital Twins Demo",
    layout="wide"
)

# 데이터 로드
ORG = get_org()
KNOW = get_knowledge()
SESS = get_sessions()
TWINS = get_twins()


def ensure_user(user_id: str) -> None:
    """사용자 세션 초기화"""
    if user_id not in SESS["users"]:
        SESS["users"][user_id] = {
            "name": user_id,
            "adapt_score": 50,
            "risk_score": 50,
            "tasks_done": 0,
            "questions": 0,
            "last_task": None,
        }


def pick_knowledge_snippet() -> str:
    """최근 지식 스니펫 반환"""
    items = KNOW.get("items", [])
    if not items:
        return ""
    return items[-1]["text"]


# ============================================================
# Sidebar
# ============================================================
st.sidebar.title("AgentCamp 데모")
mode = st.sidebar.radio("모드", ["Admin(회사 세팅)", "New Hire(OJT)", "Dashboard(HR)"])
user_id = st.sidebar.text_input("신입 사용자 ID", value="minsu")
ensure_user(user_id)


# ============================================================
# Admin Mode
# ============================================================
if mode == "Admin(회사 세팅)":
    st.header("Admin Console - Veluga OJT 설정")

    col1, col2 = st.columns(2)

    with col1:
        company = st.text_input("회사명", value=ORG.get("company", "Veluga"))
        role = st.text_input("OJT 직무", value=ORG.get("role", "Backend Engineer"))
        tools = st.text_input(
            "도구(콤마로)",
            value=",".join(ORG.get("tools", ["Slack", "GitHub"]))
        )

    with col2:
        st.subheader("기본 평가 루브릭(데모)")
        st.caption("실제 서비스에선 직무별 루브릭 템플릿 + 회사별 커스텀")
        keywords = st.text_input(
            "완료 기준 키워드(콤마)",
            value="원인,재현,재발방지,로그"
        )

    if st.button("저장"):
        new_org = {
            "company": company.strip(),
            "role": role.strip(),
            "tools": [t.strip() for t in tools.split(",") if t.strip()],
            "rubric": {
                "acceptance_keywords": [k.strip() for k in keywords.split(",") if k.strip()]
            },
        }
        set_org(new_org)
        st.success("회사 설정 저장 완료! (org.json)")

    st.divider()
    st.subheader("데이터 수집 파이프라인(데모)")
    st.caption("회의 STT / Slack-Discord 대화 / 고객미팅 STT를 업로드하면 지식으로 적재됩니다.")

    source = st.selectbox("소스 타입", ["meeting_stt", "slack_discord", "client_stt"])
    uploaded = st.file_uploader("텍스트 파일 업로드(.txt)", type=["txt"])
    raw_text = st.text_area("또는 텍스트 붙여넣기", height=150)

    if st.button("지식 추출 & 저장"):
        text = ""
        if uploaded is not None:
            text = uploaded.read().decode("utf-8", errors="ignore")
        else:
            text = raw_text

        if not text.strip():
            st.warning("텍스트가 비었습니다.")
        else:
            new_items = extract_knowledge(source, text)
            KNOW["items"].extend(new_items)
            set_knowledge(KNOW)
            st.success(f"{len(new_items)}개 지식 항목 저장 완료!")
            st.write(new_items[:5])

    st.divider()
    st.subheader("현재 지식(최근 10개)")
    for it in KNOW.get("items", [])[-10:]:
        st.write(f"- [{it['source']}/{it['tag']}] {it['text']}")


# ============================================================
# New Hire Mode
# ============================================================
elif mode == "New Hire(OJT)":
    st.header("New Hire - OJT 실행")

    user = SESS["users"][user_id]
    st.info(f"회사: {ORG.get('company')} | 직무: {ORG.get('role')} | 사용자: {user_id}")

    # 1) 오늘의 미션
    st.subheader("1) 오늘의 미션(업무)")
    if user.get("last_task") is None or st.button("오늘 미션 새로 받기"):
        task = {
            "title": "로그 기반 장애 원인 요약",
            "context": "최근 배포 이후 500 에러가 증가. 원인을 추정하고 재발 방지안을 제시.",
            "deliverable": "원인(가설) 1개 이상 + 재현 조건 + 재발 방지 1개 + 참고 로그 키워드",
            "acceptance_keywords": ORG.get("rubric", {}).get(
                "acceptance_keywords", ["원인", "재현", "재발방지", "로그"]
            ),
        }
        user["last_task"] = task
        set_sessions(SESS)

    task = user["last_task"]
    if task:
        st.write(f"**미션:** {task['title']}")
        st.write(f"- 상황: {task['context']}")
        st.write(f"- 제출물: {task['deliverable']}")
        st.caption(f"완료 키워드(데모): {', '.join(task['acceptance_keywords'])}")

    # 2) 질문하기
    st.subheader("2) 질문하기 (Digital Twins)")
    q = st.text_input(
        "질문 입력",
        placeholder="예: 이 장애 원인 확인을 위해 어떤 로그를 봐야 하나요?"
    )
    if st.button("질문 보내기") and q.strip():
        user["questions"] += 1
        snippet = pick_knowledge_snippet()
        who = route_agent(q)
        ans = answer_with_twin(TWINS[who], ORG, snippet, q)
        set_sessions(SESS)
        st.markdown(f"### 라우팅: **{who}**")
        st.code(ans)

    # 3) 제출 & 리뷰
    st.subheader("3) 제출하기 → 리뷰 받기")
    submission = st.text_area(
        "제출 내용",
        height=160,
        placeholder="원인/재현조건/재발방지/로그 키워드를 포함해 작성"
    )
    if st.button("제출 & 리뷰") and submission.strip() and task:
        score, feedback = simple_review(task, submission)
        user["tasks_done"] += 1
        user["adapt_score"] = min(100, user["adapt_score"] + int(score * 0.1))
        user["risk_score"] = max(0, user["risk_score"] - int(score * 0.05))
        set_sessions(SESS)

        st.success(f"리뷰 점수: **{score}점**")
        st.write("**강점**")
        for s in feedback["strengths"]:
            st.write(f"- {s}")
        st.write("**개선점**")
        for i in feedback["improvements"]:
            st.write(f"- {i}")
        st.write("**다음 스텝**")
        st.write(feedback["next_step"])


# ============================================================
# Dashboard Mode
# ============================================================
else:
    st.header("HR Dashboard - OJT 진행 현황")

    users = SESS.get("users", {})
    user_count = len(users)

    # 메트릭 계산
    avg_adapt = int(sum(u["adapt_score"] for u in users.values()) / max(1, user_count))
    avg_risk = int(sum(u["risk_score"] for u in users.values()) / max(1, user_count))
    total_tasks = sum(u["tasks_done"] for u in users.values())

    # 메트릭 표시
    cols = st.columns(4)
    cols[0].metric("신입 수", user_count)
    cols[1].metric("평균 적응도", avg_adapt)
    cols[2].metric("평균 리스크", avg_risk)
    cols[3].metric("총 완료 업무", total_tasks)

    # 개별 현황
    st.subheader("개별 현황")
    for uid, u in users.items():
        with st.expander(
            f"{uid} | adapt={u['adapt_score']} risk={u['risk_score']} "
            f"tasks={u['tasks_done']} q={u['questions']}"
        ):
            st.write(u)
