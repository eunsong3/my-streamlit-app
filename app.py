import streamlit as st
import pandas as pd
import openai
import os

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="Y-Mobile Saver",
    page_icon="📱",
    layout="centered"
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# 더미 요금제 데이터 (MVP용)
# -----------------------------
plans = pd.DataFrame([
    {
        "name": "알뜰폰 LTE 10GB",
        "price": 19000,
        "data": 10,
        "carrier": "MVNO",
        "type": "가성비"
    },
    {
        "name": "알뜰폰 무제한",
        "price": 29000,
        "data": 100,
        "carrier": "MVNO",
        "type": "무제한"
    },
    {
        "name": "통신3사 5G 베이직",
        "price": 55000,
        "data": 150,
        "carrier": "SKT/Kt/LGU+",
        "type": "프리미엄"
    },
    {
        "name": "자급제 + 알뜰폰 15GB",
        "price": 23000,
        "data": 15,
        "carrier": "MVNO",
        "type": "자급제"
    }
])

# -----------------------------
# 추천 로직 (Rule-based)
# -----------------------------
def recommend_plans(budget, data_usage):
    filtered = plans[
        (plans["price"] <= budget) &
        (plans["data"] >= data_usage)
    ]

    if filtered.empty:
        return plans.sort_values("price").head(3)

    return filtered.sort_values("price").head(3)

# -----------------------------
# OpenAI 설명 생성
# -----------------------------
def generate_ai_explanation(user_profile, recommended_plans):
    prompt = f"""
너는 통신비 전문 상담가이자 연세대 선배야.

[사용자 정보]
- 예산: {user_profile['budget']}원
- 월 데이터 사용량: {user_profile['data']}GB
- 사용자 유형: {user_profile['scenario']}
- 주 사용 OTT: {user_profile['ott']}

[추천 요금제]
{recommended_plans.to_string(index=False)}

단통법 폐지 이후의 상황을 고려해서,
왜 이 요금제들이 적합한지
신입생도 이해할 수 있게 친절하게 설명해줘.
톤은 친근하지만 정보는 정확하게.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

# -----------------------------
# UI
# -----------------------------
st.title("📱 Y-Mobile Saver")
st.caption("연세대 신입생과 외국인 유학생을 위한 맞춤형 통신비 최적화 AI")

st.divider()

st.subheader("📝 간단한 정보만 입력해 주세요")

budget = st.slider("월 통신비 예산 (원)", 10000, 80000, 30000, step=5000)
data_usage = st.slider("월 데이터 사용량 (GB)", 1, 150, 10)
ott = st.multiselect(
    "주로 사용하는 OTT 서비스",
    ["유튜브", "넷플릭스", "웨이브", "티빙", "디즈니+"]
)

scenario = st.radio(
    "내 상황에 가장 가까운 유형은?",
    [
        "외국인 신입생",
        "경제적 자립 신입생",
        "기기 교체를 고민 중인 신입생"
    ]
)

if st.button("🔍 나에게 딱 맞는 요금제 찾기"):
    user_profile = {
        "budget": budget,
        "data": data_usage,
        "ott": ", ".join(ott) if ott else "없음",
        "scenario": scenario
    }

    recommended = recommend_plans(budget, data_usage)

    st.divider()
    st.subheader("✅ 추천 요금제 TOP 3")

    for idx, row in recommended.iterrows():
        st.markdown(
            f"""
            **{row['name']}**  
            - 월 요금: {row['price']:,}원  
            - 데이터: {row['data']}GB  
            - 통신사 유형: {row['carrier']}
            """
        )

    # 절감 비용 시각화
    st.subheader("💸 월 예상 비용 비교")
    chart_df = recommended[["name", "price"]].set_index("name")
    st.bar_chart(chart_df)

    # AI 설명
    with st.spinner("AI가 추천 이유를 정리 중이에요..."):
        explanation = generate_ai_explanation(user_profile, recommended)

    st.subheader("🤖 AI 상담사의 한마디")
    st.write(explanation)
