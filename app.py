# app.py

import streamlit as st
from scenario import classify_user
from recommender import recommend_plans
from ai_advisor import generate_prompt
from translator import translate_text

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =========================
# 🔐 Sidebar - API 입력
# =========================
st.sidebar.title("🔐 API 설정")

openai_api_key = st.sidebar.text_input(
    "ChatGPT API Key",
    type="password"
)

deepl_api_key = st.sidebar.text_input(
    "DeepL API Key (번역용)",
    type="password"
)

language = st.sidebar.selectbox(
    "언어 선택",
    ["한국어", "English"]
)

st.sidebar.markdown("---")
st.sidebar.caption("API 키는 저장되지 않습니다.")

# =========================
# 🏠 Main UI
# =========================
st.title("📱 Y-Mobile Saver")
st.subheader("연세대 신입생 · 외국인 유학생을 위한 통신비 AI 상담")

st.markdown("### 👤 사용자 정보 입력")

budget = st.number_input("월 예산 (원)", min_value=10000, step=5000)
data_usage = st.number_input("월 데이터 사용량 (GB)", min_value=1)
ott_apps = st.multiselect("주로 사용하는 OTT", ["Netflix", "YouTube", "Wavve"])
device_type = st.selectbox("단말 유형", ["자급제", "공시지원금"])

is_foreigner = st.checkbox("외국인 유학생인가요?")
want_new_device = st.checkbox("기기 변경을 고려 중인가요?")

# =========================
# ▶ 실행
# =========================
if st.button("📊 요금제 추천받기"):
    user = {
        "budget": budget,
        "data_usage": data_usage,
        "ott_apps": ott_apps,
        "device_type": device_type,
        "is_foreigner": is_foreigner,
        "want_new_device": want_new_device
    }

    scenario = classify_user(user)
    plans = recommend_plans(user)
    prompt = generate_prompt(user, scenario, plans)

    # 🌍 번역 (영어 선택 시)
    if language == "English" and deepl_api_key:
        prompt = translate_text(
            text=prompt,
            target_lang="EN",
            api_key=deepl_api_key
        )

    st.markdown("## ✅ 추천 요금제 TOP 3")
    for p in plans:
        st.success(f"{p['name']} | {p['price']}원 / {p['data_gb']}GB")

    st.markdown("## 🤖 AI 상담 프롬프트")
    st.text_area(
        "ChatGPT에 전달될 프롬프트",
        prompt,
        height=300
    )
