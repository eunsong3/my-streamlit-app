# app.py

import streamlit as st
from data_calculator import calculate_monthly_data
from device_plans import DEVICE_PLANS
from public_api import fetch_mobile_plans
from recommender import recommend_plans

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =====================
# Sidebar
# =====================
st.sidebar.title("⚙️ 설정")

if "page" not in st.session_state:
    st.session_state.page = "main"

if st.sidebar.button("📊 평균 데이터 사용량 계산기"):
    st.session_state.page = "calculator"

scenario = st.sidebar.radio(
    "👤 사용자 시나리오",
    ["외국인 유학생", "경제적 자립 준비 학생", "기기 교체 희망 학생"]
)

# =====================
# 데이터 계산기 페이지
# =====================
if st.session_state.page == "calculator":
    st.title("📊 내 평균 데이터 사용량은?")
    st.subheader("평균 데이터 사용량 계산기")

    hours = st.slider("와이파이 없는 환경에서 주 평균 사용시간", 1, 80, 20)

    apps = st.multiselect(
        "즐겨 사용하는 앱",
        ["SNS/메신저", "유튜브/넷플릭스", "게임", "지도/검색"]
    )

    downloads = st.checkbox("파일/앱을 자주 다운로드하나요?")

    if st.button("계산하기") and apps:
        result = calculate_monthly_data(hours, apps, downloads)
        st.success(f"📱 예상 월 데이터 사용량은 약 **{result}GB** 입니다.")

    st.stop()

# =====================
# 기기 교체 시나리오
# =====================
if scenario == "기기 교체 희망 학생":
    st.title("📲 기기 교체 요금제 추천")

    maker = st.selectbox("제조사", ["애플", "삼성"])

    model = st.selectbox(
        "휴대폰 기종",
        ["아이폰 17 (256GB)"] if maker == "애플"
        else ["갤럭시 S25", "갤럭시 Z 플립7 (256GB)"]
    )

    price = st.selectbox("요금 수준 선택", ["~4만원", "~5만원", "~6만원"])

    key = (maker, model, price)

    if key in DEVICE_PLANS:
        for name, fee, discount, support in DEVICE_PLANS[key]:
            st.success(
                f"""
**{name}**
- 요금제 및 월정액: 월 {fee:,}원  
- 선택약정할인 (2년): {discount:,}원  
- 공통지원금 (기기변경): {support:,}원
"""
            )
    st.stop()

# =====================
# 알뜰폰 요금제 추천
# =====================
st.title("📱 알뜰폰 요금제 추천")

budget = st.number_input("월 예산 (원)", 10000, 70000, 30000, step=5000)
data = st.number_input("월 데이터 사용량 (GB)", 1, 100, 15)

plans = fetch_mobile_plans("")
user = {"budget": budget, "data_usage": data, "scenario": scenario}
reco = recommend_plans(user, plans)

for p in reco:
    st.success(f"{p['name']} | {p['price']}원 | {p['data_gb']}GB")
