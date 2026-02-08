import streamlit as st
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
st.sidebar.title("⚙️ Settings" if st.session_state.lang == "EN" else "⚙️ 설정")

deepl_key = st.sidebar.text_input(
    "DeepL API Key", type="password"
)

openai_key = st.sidebar.text_input(
    "ChatGPT API Key", type="password"
)

lang = st.sidebar.selectbox(
    "Language" if st.session_state.lang == "EN" else "언어 선택",
    ["한국어", "English"]
)
st.session_state.lang = "EN" if lang == "English" else "KO"

def t(text):
    if st.session_state.lang == "KO":
        return text
    if text in st.session_state.translated:
        return st.session_state.translated[text]
    translated = translate(text, "EN", deepl_key)
    st.session_state.translated[text] = translated
    return translated

if st.sidebar.button(
    "📊 Average Data Calculator" if st.session_state.lang == "EN"
    else "📊 평균 데이터 사용량 계산기"
):
    st.session_state.page = "calculator"

scenario_labels = {
    "외국인 유학생": "International Student",
    "경제적 자립 준비 학생": "Financially Independent Student",
    "기기 교체 희망 학생": "Device Upgrade Student"
}

scenario_reverse = {v: k for k, v in scenario_labels.items()}

scenario_display = st.sidebar.radio(
    "👤 User Scenario" if st.session_state.lang == "EN" else "👤 사용자 시나리오",
    list(scenario_labels.values()) if st.session_state.lang == "EN"
    else list(scenario_labels.keys())
)

scenario = (
    scenario_reverse[scenario_display]
    if st.session_state.lang == "EN"
    else scenario_display
)

# =====================
# Data Calculator
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
# Device Upgrade Scenario
# =====================
if scenario == "기기 교체 희망 학생":
    st.title(t("📱 기기 교체 요금제 추천"))

    maker_map = {
        "애플": "Apple",
        "삼성": "Samsung"
    }
    maker_reverse = {v: k for k, v in maker_map.items()}

    maker_display = st.selectbox(
        t("제조사"),
        list(maker_map.values()) if st.session_state.lang == "EN"
        else list(maker_map.keys())
    )

    maker = (
        maker_reverse[maker_display]
        if st.session_state.lang == "EN"
        else maker_display
    )

    model_map = {
        "아이폰 17 (256GB)": "iPhone 17 (256GB)",
        "갤럭시 S25": "Galaxy S25",
        "갤럭시 Z 플립7 (256GB)": "Galaxy Z Flip 7 (256GB)"
    }
    model_reverse = {v: k for k, v in model_map.items()}

    models = (
        ["아이폰 17 (256GB)"]
        if maker == "애플"
        else ["갤럭시 S25", "갤럭시 Z 플립7 (256GB)"]
    )

    model_display = st.selectbox(
        t("휴대폰 기종"),
        [model_map[m] for m in models]
        if st.session_state.lang == "EN"
        else models
    )

    model = (
        model_reverse[model_display]
        if st.session_state.lang == "EN"
        else model_display
    )

    price_map = {
        "~4만원": "Under ₩40,000",
        "~5만원": "Under ₩50,000",
        "~6만원": "Under ₩60,000"
    }
    price_reverse = {v: k for k, v in price_map.items()}

    price_display = st.selectbox(
        t("요금 수준 선택"),
        list(price_map.values()) if st.session_state.lang == "EN"
        else list(price_map.keys())
    )

    price = (
        price_reverse[price_display]
        if st.session_state.lang == "EN"
        else price_display
    )

    st.divider()
    st.subheader(t("추천 결과"))

    key = (maker, model, price)

    if key in DEVICE_PLANS:
        for name, fee, discount, support in DEVICE_PLANS[key]:
            msg = (
                f"{name}\n"
                f"- Monthly fee: ₩{fee:,}\n"
                f"- Contract discount (2 years): ₩{discount:,}\n"
                f"- Device change subsidy: ₩{support:,}"
            )
            st.success(t(msg))
    else:
        st.warning(t("선택한 조건에 대한 요금제가 없습니다."))

    st.stop()

# =====================
# MVNO Scenarios
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
                f"I am a {scenario}.\n"
                f"My monthly budget is {budget} KRW.\n"
                f"My monthly data usage is {data} GB.\n"
                f"Please recommend an MVNO plan."
            )
        }
    ]

    st.subheader(t("📌 추천 알뜰폰 요금제"))
    for p in recommended:
        st.success(
            t(f"{p['name']} | ₩{p['price']} | {p['data_gb']}GB")
        )

# =====================
# Chat UI
# =====================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(
            translate(msg["content"], st.session_state.lang, deepl_key)
        )

if prompt := st.chat_input(
    "Ask anything about mobile plans"
    if st.session_state.lang == "EN"
    else "궁금한 점을 자유롭게 물어보세요"
):
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
