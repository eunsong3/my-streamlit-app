import streamlit as st
import requests
from openai import OpenAI

# =============================
# 기본 설정
# =============================
st.set_page_config(
    page_title="🎬 나와 어울리는 영화는?",
    page_icon="🎬",
    layout="wide"
)

# =============================
# Session State (찜하기)
# =============================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# =============================
# CSS (Netflix 스타일)
# =============================
st.markdown("""
<style>
body { background-color: #000000; }
.netflix-title {
    color: #E50914;
    font-size: 40px;
    font-weight: 900;
}
.movie-card {
    background-color: #141414;
    padding: 14px;
    border-radius: 12px;
    color: white;
    transition: transform 0.2s;
}
.movie-card:hover { transform: scale(1.04); }
.movie-title { font-size: 17px; font-weight: 700; }
.movie-rating { color: #f5c518; margin: 4px 0; }
.movie-reason { font-size: 13px; color: #dddddd; }
</style>
""", unsafe_allow_html=True)

# =============================
# 상수
# =============================
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

POSTER_URL = "https://image.tmdb.org/t/p/w500"

AGE_CERT_MAP = {
    "전체 이용가": "ALL",
    "12세 이상": "12",
    "15세 이상": "15",
    "19세 이상": "19"
}

# =============================
# 성향 분석 (5문제 기준)
# =============================
def analyze_answers(a):
    scores = {g: 0 for g in GENRES}

    if a[0] == "집에서 휴식":
        scores["드라마"] += 2
    elif a[0] == "친구와 놀기":
        scores["코미디"] += 2
    elif a[0] == "새로운 곳 탐험":
        scores["액션"] += 2
    else:
        scores["SF"] += 2

    if a[1] == "혼자 있기":
        scores["드라마"] += 1
    elif a[1] == "수다 떨기":
        scores["코미디"] += 1
    elif a[1] == "운동하기":
        scores["액션"] += 1

    if a[2] == "웃는 재미":
        scores["코미디"] += 2
    elif a[2] == "감동 스토리":
        scores["드라마"] += 2
    elif a[2] == "시각적 영상미":
        scores["SF"] += 2

    if a[3] == "액티비티":
        scores["액션"] += 2
    elif a[3] == "힐링":
        scores["로맨스"] += 2

    if a[4] == "분위기 메이커":
        scores["코미디"] += 1
    elif a[4] == "주도하기":
        scores["액션"] += 1

    genre = max(scores, key=scores.get)
    return genre, GENRES[genre]

# =============================
# TMDB
# =============================
def fetch_movies(key, genre_id, rating, age):
    params = {
        "api_key": key,
        "with_genres": genre_id,
        "vote_average.gte": rating,
        "certification_country": "KR",
        "certification.gte": age,
        "language": "ko-KR",
        "sort_by": "popularity.desc"
    }
    r = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
    return r.json().get("results", [])[:8]

# =============================
# UI
# =============================
st.markdown("<div class='netflix-title'>🎬 나와 어울리는 영화는?</div>", unsafe_allow_html=True)

with st.sidebar:
    tmdb_key = st.text_input("TMDB API Key", type="password")
    openai_key = st.text_input("OpenAI API Key", type="password")
    min_rating = st.slider("⭐ 최소 평점", 0.0, 9.0, 7.0, 0.5)
    min_age = AGE_CERT_MAP[st.selectbox("관람 연령", AGE_CERT_MAP.keys())]

questions = [
    st.radio("1. 주말에 가장 하고 싶은 것은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"], index=None),
    st.radio("2. 스트레스 받으면?", ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"], index=None),
    st.radio("3. 영화에서 중요한 것은?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"], index=None),
    st.radio("4. 여행 스타일?", ["계획적", "즉흥적", "액티비티", "힐링"], index=None),
    st.radio("5. 친구 사이에서 나는?", ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"], index=None),
]

if st.button("결과 보기"):
    if None in questions or not tmdb_key or not openai_key:
        st.warning("모든 항목을 입력해주세요")
        st.stop()

    genre, genre_id = analyze_answers(questions)
    movies = fetch_movies(tmdb_key, genre_id, min_rating, min_age)

    client = OpenAI(api_key=openai_key)

    st.subheader(f"🎯 추천 장르: {genre}")

    cols = st.columns(4)
    for i, m in enumerate(movies):
        with cols[i % 4]:
            prompt = f"""
사용자 성향: {questions}
영화 제목: {m['title']}
줄거리: {m.get('overview','')}

이 사용자에게 이 영화를 추천하는 이유를 2~3문장으로 설명해줘.
"""
            reason = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content

            st.markdown(f"""
            <div class="movie-card">
                <img src="{POSTER_URL + m['poster_path']}" width="100%">
                <div class="movie-title">{m['title']}</div>
                <div class="movie-rating">⭐ {m['vote_average']}</div>
                <div class="movie-reason">{reason}</div>
            </div>
            """, unsafe_allow_html=True)
