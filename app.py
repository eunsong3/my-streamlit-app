import streamlit as st
from recommender import recommend_plans
from device_plans import DEVICE_PLANS
from ai_advisor import chat_with_ai

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

# =====================
# 기기 교체 시나리오 (기존 유지)
# =====================
if scenario == "기기 교체 희망 학생":
    st.subheader("📱 기기 교체 요금제 추천")

    maker = st.selectbox("제조사", ["애플"])
    model = st.selectbox("기종", ["아이폰 17 (256GB)"])
    price = st.selectbox("요금 수준", ["~4만원"])

    key = (maker, model, price)
    if key in DEVICE_PLANS:
        for name, fee, discount, support in DEVICE_PLANS[key]:
            st.success(
                f"{name}\n"
                f"- 월 요금: {fee}원\n"
                f"- 선택약정(2년): {discount}원\n"
                f"- 기기변경 지원금: {support}원"
            )
    st.stop()

# =====================
# 전체 요금제(JSON) 기반 추천
# =====================
st.subheader("📊 요금제 추천")

budget = st.number_input("월 예산 (원)", 10000, 80000, 40000, step=5000)
data = st.number_input("월 데이터 사용량 (GB)", 1, 200, 20)

if st.button("💬 상담 시작하기") and openai_key:
    user = {
        "budget": budget,
        "data_usage": data,
        "scenario": scenario
    }

    recommended = recommend_plans(user)

    st.session_state.chat = [{
        "role": "user",
        "content": (
            f"나는 {scenario}이야.\n"
            f"월 예산은 {budget}원이고\n"
            f"월 데이터 사용량은 {data}GB야.\n"
            f"아래 요금제 중에서 추천해줘."
        )
    }]

    st.subheader("📌 추천 요금제")
    for p in recommended:
        st.success(
            f"{p['carrier']} | {p['name']} | {p['price']}원\n"
            f"데이터: {p['data']} | 통화/문자: {p['call_text']}"
        )

st.caption("⚠️ 요금제 정보는 예시 데이터이며 실제 가입 시 최신 조건을 확인하세요.")

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("궁금한 점을 물어보세요"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    answer = chat_with_ai(st.session_state.chat, openai_key)
    st.session_state.chat.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
