import streamlit as st
import json
from parser.code_parser import parse_code
from analyzer.static_analysis import analyze_code, calculate_rule_score
from utils.formatter import format_output
from analyzer.ai_review import review_code_with_ai, improve_code_with_ai
from utils.auth_storage import (
    verify_user, load_history, save_record, make_record
)

# ================= UI =================
st.set_page_config(page_title="AI Code Reviewer", layout="centered")

st.markdown("""
<style>
.big-title {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🤖 AI Code Reviewer</div>', unsafe_allow_html=True)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "improved_code" not in st.session_state:
    st.session_state.improved_code = None

if "last_code" not in st.session_state:
    st.session_state.last_code = None

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ================= LOGOUT =================
st.write(f"👤 Logged in as: {st.session_state.username}")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# ================= LANGUAGE =================
def detect_language(filename):
    if filename.endswith(".py"):
        return "python"
    elif filename.endswith(".js"):
        return "javascript"
    elif filename.endswith(".java"):
        return "java"
    elif filename.endswith(".cpp"):
        return "cpp"
    return "text"

# ================= FILE =================
uploaded_file = st.file_uploader("Upload code file", type=["py", "js", "java", "cpp"])

if uploaded_file:
    code = parse_code(uploaded_file)
    language = detect_language(uploaded_file.name)

    st.write(f"📂 {uploaded_file.name} | 🧠 {language}")

    st.subheader("📄 Code Preview")
    st.code(code, language=language)

    if st.button("Analyze Code"):
        st.session_state.analysis_done = True
        st.session_state.ai_result = None
        st.session_state.improved_code = None

    if st.session_state.analysis_done:

        # ---------- STATIC ----------
        if language == "python":
            issues = analyze_code(code)
        else:
            issues = ["Static analysis not supported"]

        st.subheader("🔍 Static Analysis")
        st.text(format_output(issues))

        # ---------- AI ----------
        if (
            st.session_state.ai_result is None
            or st.session_state.last_code != code
        ):
            with st.spinner("Analyzing..."):
                st.session_state.ai_result = review_code_with_ai(code, language)
                st.session_state.last_code = code

        ai_result = st.session_state.ai_result

        # ---------- SCORE ----------
        rule_score = calculate_rule_score(code) if language == "python" else 5
        ai_score = int(ai_result["score"]) if ai_result["score"].isdigit() else 5
        final_score = round((ai_score * 0.6) + (rule_score * 0.4), 1)

        st.subheader("📊 Scores")

        c1, c2, c3 = st.columns(3)
        c1.metric("AI", ai_score)
        c2.metric("Rule", rule_score)
        c3.metric("Final", final_score)

        # ---------- SAVE HISTORY ----------
        record = make_record(
            uploaded_file.name,
            language,
            ai_score,
            rule_score,
            final_score
        )
        save_record(st.session_state.username, record)

        # ---------- AI DETAILS ----------
        st.subheader("📋 AI Feedback")
        st.text(ai_result["raw"])

        # ---------- IMPROVE ----------
        st.subheader("🛠️ Improve Code")

        col1, col2 = st.columns(2)

        if col1.button("Generate"):
            with st.spinner("Improving..."):
                st.session_state.improved_code = improve_code_with_ai(code, language)

        if col2.button("🔁 Regenerate"):
            with st.spinner("Generating new..."):
                st.session_state.improved_code = improve_code_with_ai(code, language)

        if st.session_state.improved_code:
            st.code(st.session_state.improved_code, language=language)

            st.download_button(
                "📥 Download",
                st.session_state.improved_code,
                f"improved.{language}"
            )

# ================= HISTORY =================
st.markdown("---")
st.subheader("📜 History")

history = load_history(st.session_state.username)

if history:
    for item in history[:10]:
        st.write(
            f"{item['timestamp']} | {item['filename']} | "
            f"{item['language']} | ⭐ {item['final_score']}"
        )

    st.download_button(
        "Download History",
        json.dumps(history, indent=2),
        "history.json"
    )
else:
    st.info("No history yet")