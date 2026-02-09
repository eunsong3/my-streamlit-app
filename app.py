import streamlit as st
from recommender import recommend_plans
from ai_advisor import chat_with_ai
from data_calculator import calculate_monthly_data

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

if "chat" not in st.session_state:
    st.session_state.chat = []

st.sidebar.title("⚙️ 설정")
openai_key = st.sidebar.text_input("ChatGPT API Key", type="password")

scenario = st.sidebar.radio(
    "사용자 시나리오",
    ["외국인 유학생", "경제적 자립 준비 학생", "기기 교체 희망 학생"]
)

st.title("📱 Y-Mobile Saver")
st.subheader("JSON 기반 요금제 추천 & AI 상담")

budget = st.number_input("월 예산 (원)", 10000, 70000, 30000, step=5000)
data = st.number_input("월 데이터 사용량 (GB)", 1, 100, 15)

if st.button("💬 상담 시작하기") and openai_key:
    user = {"budget": budget, "data_usage": data, "scenario": scenario}
    plans = recommend_plans(user)

    st.session_state.chat = [{
        "role": "user",
        "content": f"""
나는 {scenario}이야.
월 예산은 {budget}원,
월 데이터 사용량은 {data}GB야.
아래 요금제 데이터 중에서 추천해줘.
"""
    }]

    st.subheader("📌 추천 요금제")
    for p in plans:
        st.success(
            f"{p['carrier']} | {p['name']} | {p['monthly_fee']}원 | {p['data_gb']}GB"
        )

st.caption("⚠️ 본 요금제 정보는 2026년 2월 기준이며 실제 가입 시 최신 정보를 확인하세요.")

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("궁금한 점을 물어보세요"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    answer = chat_with_ai(st.session_state.chat, openai_key, "KO")
    st.session_state.chat.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
