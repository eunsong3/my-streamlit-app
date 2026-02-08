import streamlit as st
from i18n import TEXT
from translator import translate
from ai_advisor import chat_with_ai
from data_calculator import calculate_monthly_data
from device_plans import DEVICE_PLANS
from public_api import fetch_mobile_plans
from recommender import recommend_plans

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =====================
# Session State
# =====================
if "lang" not in st.session_state:
    st.session_state.lang = "KO"
if "translated" not in st.session_state:
    st.session_state.translated = {}
if "chat" not in st.session_state:
    st.session_state.chat = []
if "page" not in st.session_state:
    st.session_state.page = "main"

# =====================
# Sidebar
# =====================
st.sidebar.title("⚙️ 설정")

deepl_key = st.sidebar.text_input("DeepL API Key", type="password")
openai_key = st.sidebar.text_input("ChatGPT API Key", type="password")

lang = st.sidebar.selectbox("언어 선택", ["한국어", "English"])
st.session_state.lang = "EN" if lang == "English" else "KO"

def t(text):
    if st.session_state.lang == "KO":
        return text
    if text in st.session_state.translated:
        return st.session_state.translated[text]
    translated = translate(text, "EN", deepl_key)
    st.session_state.translated[text] = translated
    return translated

if st.sidebar.button("📊 평균 데이터 사용량 계산기"):
    st.session_state.page = "calculator"

scenario = st.sidebar.radio(
    "👤 사용자 시나리오",
    ["외국인 유학생", "경제적 자립 준비 학생", "기기 교체 희망 학생"]
)

# =====================
# 데이터 계산기
# =====================
if st.session_state.page == "calculator":
    st.title(t("내 평균 데이터 사용량은?"))
    st.subheader(t("평균 데이터 사용량 계산기"))

    hours = st.slider(
        t("와이파이 없는 환경에서 주 평균 사용시간"),
        1, 80, 20
    )

    apps = st.multiselect(
        t("즐겨 사용하는 앱"),
        ["SNS/메신저", "유튜브/넷플릭스", "게임", "지도/검색"]
    )

    downloads = st.checkbox(t("파일/앱을 자주 다운로드하나요?"))

    if st.button(t("계산하기")) and apps:
        result = calculate_monthly_data(hours, apps, downloads)
        st.success(t(f"예상 월 데이터 사용량은 약 {result}GB 입니다."))

    st.stop()

# =====================
# 기기 교체 희망 학생
# =====================
if scenario == "기기 교체 희망 학생":
    st.title(t("📱 기기 교체 요금제 추천"))

    maker = st.selectbox(t("제조사"), ["애플", "삼성"])

    model = st.selectbox(
        t("휴대폰 기종"),
        ["아이폰 17 (256GB)"] if maker == "애플"
        else ["갤럭시 S25", "갤럭시 Z 플립7 (256GB)"]
    )

    price = st.selectbox(t("요금 수준 선택"), ["~4만원", "~5만원", "~6만원"])

    st.divider()
    st.subheader(t("추천 결과"))

    key = (maker, model, price)

    if key in DEVICE_PLANS:
        for name, fee, discount, support in DEVICE_PLANS[key]:
            message = (
                f"{name}\n"
                f"- 요금제 및 월정액: 월 {fee:,}원\n"
                f"- 선택약정할인 (2년): {discount:,}원\n"
                f"- 공통지원금 (기기변경): {support:,}원"
            )
            st.success(t(message))
    else:
        st.warning(t("선택한 조건에 대한 요금제가 없습니다."))

    st.stop()

# =====================
# 알뜰폰 요금제 (외국인 / 경제적 자립)
# =====================
st.title(t("📱 알뜰폰 요금제 AI 추천"))

budget = st.number_input(
    t("월 예산 (원)"),
    10000, 70000, 30000, step=5000
)

data = st.number_input(
    t("월 데이터 사용량 (GB)"),
    1, 100, 15
)

if st.button(t("💬 상담 시작하기")) and openai_key:
    plans = fetch_mobile_plans("")
    user = {
        "budget": budget,
        "data_usage": data,
        "scenario": scenario
    }
    recommended = recommend_plans(user, plans)

    st.session_state.chat = [
        {
            "role": "user",
            "content": (
                f"나는 {scenario}이야.\n"
                f"월 예산은 {budget}원이고,\n"
                f"월 데이터 사용량은 {data}GB야.\n"
                f"알뜰폰 요금제를 추천해줘."
            )
        }
    ]

    st.subheader(t("📌 추천 알뜰폰 요금제"))
    for p in recommended:
        st.success(
            t(f"{p['name']} | 월 {p['price']}원 | {p['data_gb']}GB")
        )

# =====================
# Chat UI
# =====================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(
            translate(msg["content"], st.session_state.lang, deepl_key)
        )

if prompt := st.chat_input(t("궁금한 점을 자유롭게 물어보세요")):
    st.session_state.chat.append({"role": "user", "content": prompt})

    answer = chat_with_ai(
        st.session_state.chat,
        openai_key,
        st.session_state.lang
    )

    st.session_state.chat.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(
            translate(answer, st.session_state.lang, deepl_key)
        )
