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
# Session State (찜 목록)
# =============================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# =============================
# CSS (Netflix 스타일)
# =============================
st.markdown("""
<style>
body {
    background-color: #000000;
}
.netflix-title {
    color: #E50914;
    font-size: 42px;
    font-weight: 900;
}
.movie-card {
    background-color: #141414;
    padding: 14px;
    border-radius: 12px;
    color: white;
    transition: transform 0.2s ease;
}
.movie-card:hover {
    transform: scale(1.03);
}
.movie-title {
    font-size: 18px;
    font-weight: 700;
}
.movie-rating {
    color: #ffffff;
    font-weight: 600;
    margin: 4px 0;
}
.movie-overview {
    font-size: 13px;
    color: #cccccc;
}
.movie-reason {
    font-size: 13px;
    color: #f5f5f5;
    margin-top: 8px;
}
.fav-btn {
    background-color: #E50914;
    color: white;
    border-radius: 6px;
    padding: 4px 10px;
}
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

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

AGE_CERT_MAP = {
    "전체 이용가": "ALL",
    "12세 이상": "12",
    "15세 이상": "15",
    "19세 이상": "19"
}

# =============================
# 성향 분석
# =============================
def analyze_answers(answers):
    scores = {g: 0 for g in GENRES}

    if answers[0] == "집에서 휴식":
        scores["드라마"] += 2
        scores["로맨스"] += 1
    elif answers[0] == "친구와 놀기":
        scores["코미디"] += 2
    elif answers[0] == "새로운 곳 탐험":
        scores["액션"] += 2
    elif answers[0] == "혼자 취미생활":
        scores["SF"] += 2

    if answers[2] == "웃는 재미":
        scores["코미디"] += 3
    elif answers[2] == "감동 스토리":
        scores["드라마"] += 2

    return max(scores, key=scores.get), GENRES[max(scores, key=scores.get)]

# =============================
# TMDB API
# =============================
def fetch_movies(api_key, genre_id, min_rating, min_age):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "vote_average.gte": min_rating,
        "certification_country": "KR",
        "certification.gte": min_age,
        "sort_by": "popularity.desc",
        "page": 1
    }
    return requests.get(url, params=params).json().get("results", [])[:8]

# =============================
# GPT 추천 이유
# =============================
def gpt_reason(client, answers, movie, genre):
    prompt = f"""
사용자 성향: {answers}
영화 제목: {movie['title']}
장르: {genre}
줄거리: {movie.get('overview','')}

이 사용자가 왜 이 영화를 좋아할지 2~3문장으로 한국어로 설명해줘.
"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

# =============================
# UI
# =============================
st.markdown("<div class='netflix-title'>🎬 나와 어울리는 영화는?</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔑 API 설정")
    tmdb_key = st.text_input("TMDB API Key", type="password")
    openai_key = st.text_input("OpenAI API Key", type="password")
    min_rating = st.slider("⭐ 최소 평점", 0.0, 9.0, 6.5, 0.5)
    min_age = AGE_CERT_MAP[st.selectbox("🎞 관람 연령", AGE_CERT_MAP.keys())]

questions = [
    st.radio("주말에 가장 하고 싶은 것은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"], index=None),
    st.radio("영화에서 중요한 것은?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"], index=None),
]

if st.button("결과 보기", type="primary"):
    if None in questions or not tmdb_key or not openai_key:
        st.warning("모든 항목을 입력해주세요")
        st.stop()

    genre_name, genre_id = analyze_answers(questions)
    movies = fetch_movies(tmdb_key, genre_id, min_rating, min_age)

    client = OpenAI(api_key=openai_key)

    st.subheader(f"🎯 추천 장르: {genre_name}")

    cols = st.columns(4)
    for i, movie in enumerate(movies):
        with cols[i % 4]:
            reason = gpt_reason(client, questions, movie, genre_name)

            st.markdown(f"""
            <div class="movie-card">
                <img src="{POSTER_BASE_URL + movie['poster_path']}" width="100%">
                <div class="movie-title">{movie['title']}</div>
                <div class="movie-rating">⭐ {movie['vote_average']}</div>
                <div class="movie-reason">{reason}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("❤️ 찜하기", key=movie["id"]):
                if movie not in st.session_state.favorites:
                    st.session_state.favorites.append(movie)

# =============================
# 찜 목록
# =============================
if st.session_state.favorites:
    st.divider()
    st.subheader("❤️ 내가 찜한 영화")
    for fav in st.session_state.favorites:
        st.write(f"🎬 {fav['title']}")
