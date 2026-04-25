import streamlit as st
import json, re, time
from datetime import datetime

from notes_generator       import generate_notes
from quiz_generator        import generate_quiz
from study_planner         import generate_plan
from agent                 import ask_ai
from mindmap_generator     import generate_mindmap_data
from auth                  import register_user, login_user
from subjective_generator  import generate_subjective_questions
from progress_tracker import (
    save_progress, get_progress,
    save_quiz_score, get_quiz_scores, get_all_scores,
    save_quiz, get_saved_quizzes,
    save_plan, get_saved_plans,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Study Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:linear-gradient(135deg,#0a0f1e 0%,#0d1b2a 50%,#0a1628 100%);min-height:100vh;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1b2a 0%,#112240 100%);border-right:1px solid rgba(100,220,255,0.1);}
[data-testid="stSidebar"] *{color:#cdd9e8 !important;}
.stButton>button{background:linear-gradient(135deg,#1e88e5,#42a5f5)!important;color:white!important;border:none!important;border-radius:10px!important;padding:0.55rem 1.4rem!important;font-weight:600!important;font-size:0.95rem!important;transition:all 0.25s ease!important;box-shadow:0 4px 15px rgba(30,136,229,0.35)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(30,136,229,0.5)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div>div{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(100,200,255,0.2)!important;border-radius:10px!important;color:#e2e8f0!important;font-size:0.95rem!important;}
label,.stSelectbox label,.stRadio label{color:#94a3b8!important;font-weight:500!important;font-size:0.9rem!important;}
p,li,.stMarkdown p{color:#cbd5e1;}
h1,h2,h3{color:#e2e8f0!important;}
.card{background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.12);border-radius:16px;padding:1.5rem;margin-bottom:1rem;color:#cbd5e1;line-height:1.7;}
div[data-testid="stRadio"]>div{flex-direction:column;gap:0.4rem;}
div[data-testid="stRadio"] label{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(100,200,255,0.12)!important;border-radius:10px!important;padding:0.6rem 1rem!important;color:#cbd5e1!important;transition:all 0.2s!important;font-size:0.95rem!important;}
div[data-testid="stRadio"] label:hover{background:rgba(30,136,229,0.15)!important;border-color:rgba(30,136,229,0.4)!important;}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#1e88e5,#42a5f5)!important;}
.streamlit-expanderHeader{background:rgba(255,255,255,0.04)!important;border-radius:10px!important;color:#94a3b8!important;}
hr{border-color:rgba(100,200,255,0.1)!important;}
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,0.04);border-radius:12px;padding:4px;}
.stTabs [data-baseweb="tab"]{color:#64748b!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:rgba(30,136,229,0.2)!important;color:#42a5f5!important;}
.correct-ans{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.35);border-radius:10px;padding:0.7rem 1rem;color:#4ade80;font-weight:600;}
.wrong-ans{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.35);border-radius:10px;padding:0.7rem 1rem;color:#f87171;font-weight:600;}
.explanation-box{background:rgba(30,136,229,0.08);border:1px solid rgba(30,136,229,0.2);border-radius:10px;padding:0.7rem 1rem;color:#93c5fd;margin-top:0.5rem;font-size:0.9rem;}
.timer-box{background:rgba(30,136,229,0.12);border:1px solid rgba(30,136,229,0.3);border-radius:12px;padding:0.6rem 1.2rem;text-align:center;font-size:1.4rem;font-weight:800;color:#42a5f5;letter-spacing:2px;}
.timer-warning{background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);color:#f59e0b;}
.timer-danger{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.35);color:#f87171;}
.saved-card{background:rgba(255,255,255,0.03);border:1px solid rgba(100,200,255,0.08);border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;}
#MainMenu,footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = {
    "logged_in": False, "username": "",
    "messages": [],
    "quiz_data": [], "quiz_topic": "", "quiz_difficulty": "",
    "quiz_answers": {}, "quiz_submitted": False, "quiz_score": 0,
    "quiz_start_time": None, "quiz_time_limit": 180, "quiz_time_taken": 0,
    "subj_data": None, "subj_topic": "",
    "plan_text": "", "plan_subjects": "", "plan_exam_date": "", "plan_hours": 4,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def parse_quiz(raw: str) -> list:
    questions = []
    blocks = re.split(r'\nQ\d+[:.]\s*', raw)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        q_text = lines[0].strip()
        options, answer, explanation = {}, "", ""
        for line in lines[1:]:
            m = re.match(r'^([A-D])[.)]\s*(.+)', line.strip())
            if m:
                options[m.group(1)] = m.group(2).strip()
            if line.lower().startswith("answer:"):
                answer = line.split(":", 1)[1].strip()
            if line.lower().startswith("explanation:"):
                explanation = line.split(":", 1)[1].strip()
        if q_text and len(options) >= 2:
            questions.append({"question": q_text, "options": options, "answer": answer, "explanation": explanation})
    return questions

def grade_color(pct):
    if pct >= 80: return "#4ade80"
    if pct >= 60: return "#f59e0b"
    return "#f87171"

def fmt_time(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def render_mindmap(data: dict):
    center = data.get("center", "Topic")
    branches = data.get("branches", [])
    colors = ["#42a5f5","#4ade80","#f59e0b","#c084fc","#fb7185"]
    st.markdown(f"""
    <div style='text-align:center;margin-bottom:1.5rem;'>
        <span style='background:linear-gradient(135deg,#1e88e5,#42a5f5);color:white;
            padding:0.6rem 2rem;border-radius:30px;font-size:1.3rem;font-weight:700;
            box-shadow:0 4px 20px rgba(30,136,229,0.4);'>🧠 {center}</span>
    </div>""", unsafe_allow_html=True)
    cols = st.columns(min(len(branches), 5))
    for i, branch in enumerate(branches[:5]):
        color = colors[i % len(colors)]
        children_html = "".join(
            f"<li style='margin:4px 0;color:#94a3b8;font-size:0.82rem;'>{c}</li>"
            for c in branch.get("children", []))
        cols[i].markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid {color}44;
            border-radius:14px;padding:1rem;text-align:center;'>
            <div style='background:{color}22;border:1px solid {color}66;border-radius:20px;
                padding:0.4rem 0.8rem;color:{color};font-weight:700;font-size:0.9rem;margin-bottom:0.8rem;'>
                {branch.get("name","Branch")}</div>
            <ul style='list-style:none;padding:0;margin:0;text-align:left;'>{children_html}</ul>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
def render_auth():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style='text-align:center;margin-bottom:2rem;'>
            <span style='font-size:3rem;'>🧠</span>
            <h1 style='color:#e2e8f0;font-size:2rem;font-weight:800;margin:0;'>AI Study Agent</h1>
            <p style='color:#64748b;font-size:0.95rem;margin-top:0.3rem;'>Your intelligent learning companion</p>
        </div>""", unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔑  Sign In", "✨  Create Account"])
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="li_user", placeholder="Enter username")
            password = st.text_input("Password", key="li_pass", type="password", placeholder="Enter password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if username and password:
                    result = login_user(username, password)
                    if result["success"]:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(f"Welcome back, {username}! 🎉")
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please fill in all fields.")
        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_user  = st.text_input("Username", key="reg_user",  placeholder="Choose a username")
            reg_email = st.text_input("Email",    key="reg_email", placeholder="Your email address")
            reg_pass  = st.text_input("Password", key="reg_pass",  type="password", placeholder="Create a password")
            reg_pass2 = st.text_input("Confirm",  key="reg_pass2", type="password", placeholder="Confirm password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_reg"):
                if not all([reg_user, reg_email, reg_pass, reg_pass2]):
                    st.warning("Please fill in all fields.")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match.")
                elif len(reg_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    result = register_user(reg_user, reg_pass, reg_email)
                    if result["success"]:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error(result["message"])

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:1rem 0 0.5rem;'>
            <div style='font-size:1.5rem;font-weight:800;color:#e2e8f0;'>🧠 Study Agent</div>
            <div style='font-size:0.82rem;color:#42a5f5;margin-top:0.2rem;'>
                Logged in as <b>{st.session_state.username}</b></div>
        </div>""", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("Navigation", [
            "📚  Notes Generator",
            "🗺️  Mind Map",
            "📝  Quiz (MCQ)",
            "✍️  Subjective Questions",
            "📅  Study Planner",
            "💾  Saved Items",
            "📊  Progress Tracker",
            "💬  AI Chat",
        ], label_visibility="collapsed")
        st.divider()
        stats = get_all_scores(st.session_state.username)
        st.markdown(f"""
        <div style='font-size:0.78rem;color:#475569;font-weight:600;
            text-transform:uppercase;letter-spacing:1px;margin-bottom:0.6rem;'>Quick Stats</div>
        <div style='display:flex;gap:0.5rem;flex-wrap:wrap;'>
            <div style='background:rgba(30,136,229,0.12);border:1px solid rgba(30,136,229,0.2);
                border-radius:10px;padding:0.5rem 0.7rem;flex:1;min-width:60px;text-align:center;'>
                <div style='font-size:1.3rem;font-weight:800;color:#42a5f5;'>{stats["total_quizzes"]}</div>
                <div style='font-size:0.7rem;color:#475569;'>Quizzes</div></div>
            <div style='background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.2);
                border-radius:10px;padding:0.5rem 0.7rem;flex:1;min-width:60px;text-align:center;'>
                <div style='font-size:1.3rem;font-weight:800;color:#4ade80;'>{stats["avg_score"]}%</div>
                <div style='font-size:0.7rem;color:#475569;'>Avg</div></div>
        </div>""", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪  Sign Out", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    return menu

# ─────────────────────────────────────────────
# PAGE: NOTES GENERATOR
# ─────────────────────────────────────────────
def page_notes():
    st.markdown("## 📚 Notes Generator")
    st.markdown("<p style='color:#64748b;'>Generate structured AI study notes on any topic.</p>", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns([3, 1])
    with c1:
        topic = st.text_input("Topic", placeholder="e.g. Photosynthesis, Machine Learning...")
    with c2:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    if st.button("✨ Generate Notes"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return
        with st.spinner("Generating notes..."):
            notes = generate_notes(topic, difficulty)
            save_progress(st.session_state.username, topic)
        st.markdown("### 📖 Your Study Notes")
        st.markdown(f"<div class='card'>{notes}</div>", unsafe_allow_html=True)
        st.download_button("⬇️ Download Notes", data=notes,
            file_name=f"{topic.replace(' ','_')}_notes.txt", mime="text/plain")

# ─────────────────────────────────────────────
# PAGE: MIND MAP
# ─────────────────────────────────────────────
def page_mindmap():
    st.markdown("## 🗺️ Mind Map Generator")
    st.markdown("<p style='color:#64748b;'>Visualize any topic as a mind map.</p>", unsafe_allow_html=True)
    st.divider()
    topic = st.text_input("Topic", placeholder="e.g. World War II, Python Programming...")
    if st.button("🗺️ Generate Mind Map"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return
        with st.spinner("Building mind map..."):
            raw = generate_mindmap_data(topic)
            raw_clean = re.sub(r'```json|```', '', raw).strip()
            match = re.search(r'\{.*\}', raw_clean, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    save_progress(st.session_state.username, f"MindMap: {topic}")
                    st.markdown("---")
                    render_mindmap(data)
                    st.markdown("---")
                    st.info("💡 Each branch represents a key concept.")
                except json.JSONDecodeError:
                    st.error("Couldn't parse mind map. Try a different topic.")
            else:
                st.error("AI returned unexpected format.")

# ─────────────────────────────────────────────
# PAGE: QUIZ (MCQ) with TIMER
# ─────────────────────────────────────────────
def page_quiz():
    st.markdown("## 📝 Quiz (MCQ)")
    st.markdown("<p style='color:#64748b;'>Timed multiple-choice quiz with instant scoring and explanations.</p>", unsafe_allow_html=True)
    st.divider()

    # ── RESULT SCREEN ──
    if st.session_state.quiz_submitted and st.session_state.quiz_data:
        score   = st.session_state.quiz_score
        total   = len(st.session_state.quiz_data)
        pct     = round((score / total) * 100) if total else 0
        color   = grade_color(pct)
        grade   = "🏆 Excellent!" if pct >= 80 else "👍 Good job!" if pct >= 60 else "📚 Keep studying!"
        elapsed = st.session_state.quiz_time_taken

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.1);
            border-radius:14px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2.5rem;font-weight:900;color:{color};'>{pct}%</div>
            <div style='color:#94a3b8;font-size:0.85rem;'>{score}/{total} correct</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.1);
            border-radius:14px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2.5rem;font-weight:900;color:#42a5f5;'>{fmt_time(elapsed)}</div>
            <div style='color:#94a3b8;font-size:0.85rem;'>Time taken</div>
        </div>""", unsafe_allow_html=True)
        c3.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.1);
            border-radius:14px;padding:1.2rem;text-align:center;'>
            <div style='font-size:1.5rem;font-weight:700;color:#e2e8f0;'>{grade}</div>
            <div style='color:#94a3b8;font-size:0.82rem;'>{st.session_state.quiz_topic}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Save quiz button
        col_save, col_new = st.columns(2)
        with col_save:
            if st.button("💾 Save Quiz & Results"):
                save_quiz(
                    st.session_state.username,
                    st.session_state.quiz_topic,
                    st.session_state.quiz_difficulty,
                    st.session_state.quiz_data,
                    score, total, elapsed
                )
                st.success("Quiz saved! View it in Saved Items.")

        with col_new:
            if st.button("🔄 Take Another Quiz"):
                for k in ["quiz_data","quiz_answers","quiz_submitted","quiz_score",
                          "quiz_start_time","quiz_time_taken"]:
                    st.session_state[k] = [] if k=="quiz_data" else {} if k=="quiz_answers" else False if k=="quiz_submitted" else 0 if k in ["quiz_score","quiz_time_taken"] else None
                st.rerun()

        # Build downloadable report
        report_lines = [
            f"QUIZ REPORT",
            f"Topic: {st.session_state.quiz_topic}",
            f"Difficulty: {st.session_state.quiz_difficulty}",
            f"Score: {score}/{total} ({pct}%)",
            f"Time Taken: {fmt_time(elapsed)}",
            f"Date: {datetime.now().strftime('%d %b %Y %H:%M')}",
            "="*50, ""
        ]
        for i, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.quiz_answers.get(i, "")
            correct_letter = q["answer"][0].upper() if q["answer"] else ""
            is_correct = user_ans.upper() == correct_letter
            report_lines.append(f"Q{i+1}: {q['question']}")
            for letter, opt in q["options"].items():
                report_lines.append(f"  {letter}) {opt}")
            report_lines.append(f"Your answer: {user_ans}  |  Correct: {correct_letter}  |  {'✓ Correct' if is_correct else '✗ Wrong'}")
            if q.get("explanation"):
                report_lines.append(f"Explanation: {q['explanation']}")
            report_lines.append("")

        report_text = "\n".join(report_lines)
        st.download_button("⬇️ Download Quiz Report", data=report_text,
            file_name=f"quiz_{st.session_state.quiz_topic.replace(' ','_')}.txt", mime="text/plain")

        st.markdown("### 📋 Review")
        for i, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.quiz_answers.get(i, "")
            correct_letter = q["answer"][0].upper() if q["answer"] else ""
            is_correct = user_ans.upper() == correct_letter
            with st.expander(f"Q{i+1}: {q['question'][:80]}..."):
                for letter, opt in q["options"].items():
                    icon = " ✅" if letter == correct_letter else (" ❌" if letter == user_ans and not is_correct else "")
                    st.markdown(f"**{letter})** {opt}{icon}")
                if is_correct:
                    st.markdown(f"<div class='correct-ans'>✅ Correct! You answered: {user_ans}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='wrong-ans'>❌ You answered: {user_ans or 'None'} — Correct: {correct_letter}</div>", unsafe_allow_html=True)
                if q.get("explanation"):
                    st.markdown(f"<div class='explanation-box'>💡 {q['explanation']}</div>", unsafe_allow_html=True)
        return

    # ── SETUP FORM ──
    if not st.session_state.quiz_data:
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            topic = st.text_input("Topic", placeholder="e.g. Solar System, Python Loops...")
        with c2:
            difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
        with c3:
            time_limit = st.selectbox("Time Limit", [1, 2, 3, 5], index=2, format_func=lambda x: f"{x} min")

        if st.button("🎯 Generate Quiz"):
            if not topic.strip():
                st.warning("Please enter a topic.")
                return
            with st.spinner("Generating quiz..."):
                raw_quiz = generate_quiz(topic, difficulty)
                questions = parse_quiz(raw_quiz)
            if not questions:
                st.error("Couldn't parse quiz. Try a different topic.")
                return
            st.session_state.quiz_data       = questions
            st.session_state.quiz_topic      = topic
            st.session_state.quiz_difficulty = difficulty
            st.session_state.quiz_answers    = {}
            st.session_state.quiz_submitted  = False
            st.session_state.quiz_score      = 0
            st.session_state.quiz_time_limit = time_limit * 60
            st.session_state.quiz_start_time = time.time()
            st.rerun()
        return

    # ── ACTIVE QUIZ ──
    questions   = st.session_state.quiz_data
    total_q     = len(questions)
    answered    = len(st.session_state.quiz_answers)
    elapsed     = time.time() - (st.session_state.quiz_start_time or time.time())
    remaining   = max(0, st.session_state.quiz_time_limit - elapsed)

    # Timer display
    timer_class = "timer-box"
    if remaining < 60:
        timer_class = "timer-box timer-danger"
    elif remaining < 120:
        timer_class = "timer-box timer-warning"

    t_col, info_col = st.columns([1, 3])
    with t_col:
        st.markdown(f"<div class='{timer_class}'>⏱ {fmt_time(remaining)}</div>", unsafe_allow_html=True)
    with info_col:
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.1);
            border-radius:14px;padding:0.8rem 1.2rem;'>
            <span style='color:#e2e8f0;font-weight:700;'>{st.session_state.quiz_topic}</span>
            <span style='margin-left:0.6rem;background:rgba(30,136,229,0.15);color:#42a5f5;
                border-radius:20px;padding:2px 10px;font-size:0.8rem;font-weight:600;'>
                {st.session_state.quiz_difficulty}</span>
            <span style='margin-left:0.6rem;color:#64748b;font-size:0.9rem;'>
                {answered}/{total_q} answered</span>
        </div>""", unsafe_allow_html=True)

    st.progress(answered / total_q if total_q else 0)

    # Auto-submit if time runs out
    if remaining <= 0 and not st.session_state.quiz_submitted:
        score = sum(
            1 for i, q in enumerate(questions)
            if st.session_state.quiz_answers.get(i, "").upper() == (q["answer"][0].upper() if q["answer"] else "")
        )
        st.session_state.quiz_score     = score
        st.session_state.quiz_submitted = True
        st.session_state.quiz_time_taken = st.session_state.quiz_time_limit
        save_quiz_score(st.session_state.username, st.session_state.quiz_topic,
                        score, total_q, st.session_state.quiz_difficulty)
        st.warning("⏰ Time's up! Quiz auto-submitted.")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    for i, q in enumerate(questions):
        st.markdown(f"""
        <div style='font-size:0.78rem;color:#42a5f5;font-weight:600;
            text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;'>
            Question {i+1} of {total_q}</div>
        <div style='font-size:1.05rem;font-weight:600;color:#e2e8f0;margin-bottom:0.8rem;'>
            {q["question"]}</div>""", unsafe_allow_html=True)
        options_list = [f"{k}) {v}" for k, v in q["options"].items()]
        choice = st.radio(f"q_{i}", options_list, key=f"radio_{i}", label_visibility="collapsed")
        if choice:
            st.session_state.quiz_answers[i] = choice[0]
        st.divider()

    _, c2, _ = st.columns([1, 1, 1])
    with c2:
        if st.button("🏁 Submit Quiz", use_container_width=True):
            if len(st.session_state.quiz_answers) < total_q:
                st.warning(f"Please answer all {total_q} questions.")
                return
            score = sum(
                1 for i, q in enumerate(questions)
                if st.session_state.quiz_answers.get(i, "").upper() == (q["answer"][0].upper() if q["answer"] else "")
            )
            st.session_state.quiz_score      = score
            st.session_state.quiz_submitted  = True
            st.session_state.quiz_time_taken = int(elapsed)
            save_quiz_score(st.session_state.username, st.session_state.quiz_topic,
                            score, total_q, st.session_state.quiz_difficulty)
            st.rerun()

    # Refresh to keep timer live
    time.sleep(1)
    st.rerun()

# ─────────────────────────────────────────────
# PAGE: SUBJECTIVE QUESTIONS
# ─────────────────────────────────────────────
def page_subjective():
    st.markdown("## ✍️ Subjective Questions")
    st.markdown("<p style='color:#64748b;'>Short answer and long answer questions with model answers.</p>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns([3, 1])
    with c1:
        topic = st.text_input("Topic", key="subj_topic_input", placeholder="e.g. French Revolution, Photosynthesis...")
    with c2:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"], key="subj_diff")

    if st.button("✍️ Generate Questions"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return
        with st.spinner("Generating questions..."):
            raw = generate_subjective_questions(topic, difficulty)
            st.session_state.subj_data  = raw
            st.session_state.subj_topic = topic
            save_progress(st.session_state.username, f"Subjective: {topic}")

    if st.session_state.subj_data:
        raw = st.session_state.subj_data
        topic_label = st.session_state.subj_topic

        # Split into short and long sections
        sections = re.split(r'(SHORT ANSWER QUESTIONS|LONG ANSWER QUESTIONS)', raw, flags=re.IGNORECASE)

        st.markdown("<br>", unsafe_allow_html=True)

        current_section = ""
        for part in sections:
            part = part.strip()
            if not part:
                continue
            if "SHORT" in part.upper() and "ANSWER" in part.upper() and "QUESTION" in part.upper():
                current_section = "short"
                st.markdown("""
                <div style='background:rgba(66,165,245,0.1);border:1px solid rgba(66,165,245,0.25);
                    border-radius:12px;padding:0.7rem 1.2rem;margin-bottom:1rem;'>
                    <span style='color:#42a5f5;font-weight:700;font-size:1rem;'>
                        📝 Short Answer Questions</span>
                    <span style='color:#64748b;font-size:0.82rem;margin-left:0.5rem;'>2-3 sentence answers</span>
                </div>""", unsafe_allow_html=True)
                continue
            elif "LONG" in part.upper() and "ANSWER" in part.upper() and "QUESTION" in part.upper():
                current_section = "long"
                st.markdown("""
                <div style='background:rgba(196,132,252,0.1);border:1px solid rgba(196,132,252,0.25);
                    border-radius:12px;padding:0.7rem 1.2rem;margin-bottom:1rem;margin-top:1.5rem;'>
                    <span style='color:#c084fc;font-weight:700;font-size:1rem;'>
                        📖 Long Answer Questions</span>
                    <span style='color:#64748b;font-size:0.82rem;margin-left:0.5rem;'>detailed answers with examples</span>
                </div>""", unsafe_allow_html=True)
                continue

            # Parse Q&A blocks
            blocks = re.split(r'\nQ\d+:', part)
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                if "Model Answer:" in block:
                    q_part, a_part = block.split("Model Answer:", 1)
                    q_text = q_part.strip().lstrip("=").strip()
                    a_text = a_part.strip()
                    border_color = "#42a5f5" if current_section == "short" else "#c084fc"
                    with st.expander(f"Q: {q_text[:100]}"):
                        st.markdown(f"""
                        <div style='background:rgba(255,255,255,0.03);border-left:3px solid {border_color};
                            border-radius:0 10px 10px 0;padding:0.8rem 1rem;color:#cbd5e1;line-height:1.7;'>
                            <div style='font-size:0.78rem;color:{border_color};font-weight:600;
                                margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:1px;'>
                                Model Answer</div>
                            {a_text}
                        </div>""", unsafe_allow_html=True)
                else:
                    if len(block) > 10:
                        st.markdown(f"<div style='color:#94a3b8;padding:0.4rem 0;'>{block}</div>",
                                    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("⬇️ Download Questions",
            data=raw,
            file_name=f"{topic_label.replace(' ','_')}_subjective_questions.txt",
            mime="text/plain")

# ─────────────────────────────────────────────
# PAGE: STUDY PLANNER
# ─────────────────────────────────────────────
def page_planner():
    st.markdown("## 📅 Study Planner")
    st.markdown("<p style='color:#64748b;'>Create a personalised hourly study schedule.</p>", unsafe_allow_html=True)
    st.divider()

    subjects  = st.text_input("Subjects", placeholder="e.g. Maths, Physics, Chemistry")
    exam_date = st.date_input("Exam Date")
    hours     = st.slider("Study Hours per Day", 1, 12, 4)

    if st.button("📅 Generate Plan"):
        if not subjects.strip():
            st.warning("Please enter subjects.")
            return
        with st.spinner("Building your plan..."):
            plan = generate_plan(subjects, exam_date, hours)
        st.session_state.plan_text      = plan
        st.session_state.plan_subjects  = subjects
        st.session_state.plan_exam_date = str(exam_date)
        st.session_state.plan_hours     = hours

    if st.session_state.plan_text:
        st.markdown("### 🗓️ Your Study Plan")
        st.markdown(f"<div class='card'>{st.session_state.plan_text}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download Plan",
                data=st.session_state.plan_text,
                file_name="study_plan.txt", mime="text/plain")
        with col2:
            if st.button("💾 Save Plan to Library"):
                save_plan(
                    st.session_state.username,
                    st.session_state.plan_subjects,
                    st.session_state.plan_exam_date,
                    st.session_state.plan_hours,
                    st.session_state.plan_text,
                )
                st.success("✅ Plan saved! View it in Saved Items.")

# ─────────────────────────────────────────────
# PAGE: SAVED ITEMS
# ─────────────────────────────────────────────
def page_saved():
    st.markdown("## 💾 Saved Items")
    st.markdown("<p style='color:#64748b;'>Your saved quizzes and study plans.</p>", unsafe_allow_html=True)
    st.divider()

    tab_quizzes, tab_plans = st.tabs(["📝 Saved Quizzes", "📅 Saved Plans"])

    with tab_quizzes:
        quizzes = get_saved_quizzes(st.session_state.username)
        if not quizzes:
            st.info("No saved quizzes yet. Submit a quiz and click 'Save Quiz & Results'.")
        else:
            st.markdown(f"**{len(quizzes)} saved quiz(zes)**")
            for idx, q in enumerate(quizzes):
                pct   = q.get("percentage", 0)
                color = grade_color(pct)
                date_str = q["date"].strftime("%d %b %Y, %I:%M %p") if isinstance(q.get("date"), datetime) else str(q.get("date",""))
                with st.expander(f"📝 {q.get('topic','')} — {pct}% — {date_str}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Score", f"{q.get('score',0)}/{q.get('total',0)}")
                    c2.metric("Percentage", f"{pct}%")
                    c3.metric("Time", fmt_time(q.get("time_taken", 0)))

                    # Build report for download
                    questions = q.get("questions", [])
                    report_lines = [
                        f"SAVED QUIZ REPORT",
                        f"Topic: {q.get('topic','')}",
                        f"Difficulty: {q.get('difficulty','')}",
                        f"Score: {q.get('score',0)}/{q.get('total',0)} ({pct}%)",
                        f"Time: {fmt_time(q.get('time_taken',0))}",
                        f"Date: {date_str}", "="*50, ""
                    ]
                    for i, qitem in enumerate(questions):
                        report_lines.append(f"Q{i+1}: {qitem.get('question','')}")
                        for letter, opt in qitem.get("options", {}).items():
                            report_lines.append(f"  {letter}) {opt}")
                        report_lines.append(f"Answer: {qitem.get('answer','')}")
                        if qitem.get("explanation"):
                            report_lines.append(f"Explanation: {qitem['explanation']}")
                        report_lines.append("")

                    if questions:
                        st.markdown("#### Questions & Answers")
                        for i, qitem in enumerate(questions):
                            st.markdown(f"**Q{i+1}:** {qitem.get('question','')}")
                            for letter, opt in qitem.get("options", {}).items():
                                is_ans = qitem.get("answer","").startswith(letter)
                                icon = " ✅" if is_ans else ""
                                st.markdown(f"&nbsp;&nbsp;{letter}) {opt}{icon}")
                            if qitem.get("explanation"):
                                st.markdown(f"<div class='explanation-box'>💡 {qitem['explanation']}</div>",
                                            unsafe_allow_html=True)
                            st.markdown("---")

                    st.download_button(
                        f"⬇️ Download Quiz {idx+1}",
                        data="\n".join(report_lines),
                        file_name=f"saved_quiz_{q.get('topic','').replace(' ','_')}_{idx}.txt",
                        mime="text/plain",
                        key=f"dl_quiz_{idx}"
                    )

    with tab_plans:
        plans = get_saved_plans(st.session_state.username)
        if not plans:
            st.info("No saved plans yet. Generate a study plan and click 'Save Plan to Library'.")
        else:
            st.markdown(f"**{len(plans)} saved plan(s)**")
            for idx, p in enumerate(plans):
                date_str = p["date"].strftime("%d %b %Y") if isinstance(p.get("date"), datetime) else str(p.get("date",""))
                with st.expander(f"📅 {p.get('subjects','')} — Exam: {p.get('exam_date','')} — Saved {date_str}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Subjects:** {p.get('subjects','')}")
                    c2.markdown(f"**Hours/day:** {p.get('hours','')}")
                    st.markdown(f"<div class='card'>{p.get('plan','')}</div>", unsafe_allow_html=True)
                    st.download_button(
                        f"⬇️ Download Plan {idx+1}",
                        data=p.get("plan",""),
                        file_name=f"saved_plan_{idx}.txt",
                        mime="text/plain",
                        key=f"dl_plan_{idx}"
                    )

# ─────────────────────────────────────────────
# PAGE: PROGRESS TRACKER
# ─────────────────────────────────────────────
def page_progress():
    st.markdown("## 📊 Progress Tracker")
    st.markdown("<p style='color:#64748b;'>Track your learning journey and quiz performance.</p>", unsafe_allow_html=True)
    st.divider()

    stats  = get_all_scores(st.session_state.username)
    scores = get_quiz_scores(st.session_state.username)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color in [
        (c1, "Total Quizzes",   str(stats["total_quizzes"]),          "#42a5f5"),
        (c2, "Average Score",   f"{stats['avg_score']}%",             "#4ade80"),
        (c3, "Best Score",      f"{stats['best_score']}%",            "#f59e0b"),
        (c4, "Topics Studied",  str(len(stats["topics_studied"])),    "#c084fc"),
    ]:
        col.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.1);
            border-radius:14px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2rem;font-weight:800;color:{color};'>{value}</div>
            <div style='font-size:0.8rem;color:#475569;margin-top:0.2rem;'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_scores, tab_activity = st.tabs(["🏆 Quiz Scores", "📚 Study Activity"])

    with tab_scores:
        if not scores:
            st.info("No quiz scores yet. Take a quiz to see your progress!")
        else:
            for s in scores:
                pct   = s.get("percentage", 0)
                color = grade_color(pct)
                date_str = s["date"].strftime("%d %b %Y, %I:%M %p") if isinstance(s.get("date"), datetime) else ""
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(100,200,255,0.08);
                    border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;
                    display:flex;align-items:center;justify-content:space-between;'>
                    <div>
                        <div style='font-weight:600;color:#e2e8f0;'>{s.get("topic","")}</div>
                        <div style='font-size:0.78rem;color:#475569;'>{s.get("difficulty","")} · {date_str}</div>
                    </div>
                    <div style='text-align:right;'>
                        <span style='font-size:1.4rem;font-weight:800;color:{color};'>{pct}%</span>
                        <div style='font-size:0.78rem;color:#475569;'>{s.get("score",0)}/{s.get("total",0)}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            if len(scores) >= 2:
                st.markdown("#### 📈 Score History")
                for s in reversed(scores[:10]):
                    pct   = s.get("percentage", 0)
                    color = grade_color(pct)
                    label = s.get("topic","")[:20]
                    st.markdown(f"""
                    <div style='margin-bottom:0.5rem;display:flex;align-items:center;gap:0.6rem;'>
                        <div style='width:120px;font-size:0.78rem;color:#64748b;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{label}</div>
                        <div style='flex:1;background:rgba(255,255,255,0.06);border-radius:6px;height:20px;overflow:hidden;'>
                            <div style='width:{int(pct)}%;background:{color};height:100%;border-radius:6px;'></div>
                        </div>
                        <div style='width:42px;font-size:0.82rem;font-weight:700;color:{color};text-align:right;'>{pct}%</div>
                    </div>""", unsafe_allow_html=True)

    with tab_activity:
        progress = get_progress(st.session_state.username)
        if not progress:
            st.info("No activity recorded yet.")
        else:
            st.markdown(f"**{len(progress)} total activities**")
            for p in reversed(progress[-20:]):
                date_str = p["date"].strftime("%d %b %Y, %I:%M %p") if isinstance(p.get("date"), datetime) else ""
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.03);border-left:3px solid #42a5f5;
                    border-radius:0 10px 10px 0;padding:0.6rem 1rem;margin-bottom:0.4rem;
                    display:flex;justify-content:space-between;'>
                    <span style='color:#e2e8f0;font-size:0.9rem;'>{p.get("topic","")}</span>
                    <span style='color:#475569;font-size:0.78rem;'>{date_str}</span>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: AI CHAT
# ─────────────────────────────────────────────
def page_chat():
    st.markdown("## 💬 AI Chat")
    st.markdown("<p style='color:#64748b;'>Ask anything about your studies.</p>", unsafe_allow_html=True)
    st.divider()
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_input = st.chat_input("Ask anything…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            response = ask_ai(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ─────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    render_auth()
else:
    menu = render_sidebar()
    if   "Notes Generator" in menu:       page_notes()
    elif "Mind Map"        in menu:       page_mindmap()
    elif "Quiz (MCQ)"      in menu:       page_quiz()
    elif "Subjective"      in menu:       page_subjective()
    elif "Planner"         in menu:       page_planner()
    elif "Saved Items"     in menu:       page_saved()
    elif "Progress"        in menu:       page_progress()
    elif "Chat"            in menu:       page_chat()
