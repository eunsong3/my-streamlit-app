import streamlit as st
import requests

st.set_page_config(
    page_title="🎬 나와 어울리는 영화는?",
    page_icon="🎬",
    layout="centered"
)

# -----------------------------
# 상수 설정
# -----------------------------
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


# -----------------------------
# 성향 분석 함수
# -----------------------------
def analyze_answers(answers):
    scores = {genre: 0 for genre in GENRES}

    # Q1
    if answers[0] == "집에서 휴식":
        scores["드라마"] += 2
        scores["로맨스"] += 1
    elif answers[0] == "친구와 놀기":
        scores["코미디"] += 2
    elif answers[0] == "새로운 곳 탐험":
        scores["액션"] += 2
        scores["판타지"] += 1
    elif answers[0] == "혼자 취미생활":
        scores["SF"] += 2

    # Q2
    if answers[1] == "혼자 있기":
        scores["드라마"] += 2
    elif answers[1] == "수다 떨기":
        scores["코미디"] += 2
        scores["로맨스"] += 1
    elif answers[1] == "운동하기":
        scores["액션"] += 2
    elif answers[1] == "맛있는 거 먹기":
        scores["코미디"] += 1
        scores["드라마"] += 1

    # Q3
    if answers[2] == "감동 스토리":
        scores["드라마"] += 2
        scores["로맨스"] += 1
    elif answers[2] == "시각적 영상미":
        scores["SF"] += 2
        scores["판타지"] += 2
    elif answers[2] == "깊은 메시지":
        scores["드라마"] += 2
        scores["SF"] += 1
    elif answers[2] == "웃는 재미":
        scores["코미디"] += 3

    # Q4
    if answers[3] == "계획적":
        scores["드라마"] += 1
    elif answers[3] == "즉흥적":
        scores["코미디"] += 2
    elif answers[3] == "액티비티":
        scores["액션"] += 3
    elif answers[3] == "힐링":
        scores["로맨스"] += 2
        scores["판타지"] += 1

    # Q5
    if answers[4] == "듣는 역할":
        scores["드라마"] += 2
    elif answers[4] == "주도하기":
        scores["액션"] += 2
    elif answers[4] == "분위기 메이커":
        scores["코미디"] += 2
    elif answers[4] == "필요할 때 나타남":
        scores["SF"] += 2

    best_genre = max(scores, key=scores.get)
    return best_genre, GENRES[best_genre]


# -----------------------------
# TMDB API 호출
# -----------------------------
def fetch_movies(api_key, genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "page": 1
    }
    response = requests.get(url)
    return response.json()["results"][:5]


# -----------------------------
# UI
# -----------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("5가지 질문으로 당신의 성향에 딱 맞는 영화를 추천해드려요!")

with st.sidebar:
    st.header("🔑 TMDB API Key")
    api_key = st.text_input("API Key 입력", type="password")

st.divider()

q1 = st.radio(
    "1. 주말에 가장 하고 싶은 것은?",
    ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    index=None
)

q2 = st.radio(
    "2. 스트레스 받으면?",
    ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    index=None
)

q3 = st.radio(
    "3. 영화에서 중요한 것은?",
    ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    index=None
)

q4 = st.radio(
    "4. 여행 스타일?",
    ["계획적", "즉흥적", "액티비티", "힐링"],
    index=None
)

q5 = st.radio(
    "5. 친구 사이에서 나는?",
    ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    index=None
)

st.divider()

if st.button("결과 보기", type="primary"):
    answers = [q1, q2, q3, q4, q5]

    if None in answers:
        st.warning("모든 질문에 답해주세요!")
    elif not api_key:
        st.error("TMDB API Key를 입력해주세요!")
    else:
        with st.spinner("분석 중..."):
            genre_name, genre_id = analyze_answers(answers)
            movies = fetch_movies(api_key, genre_id)

        st.subheader(f"🎯 추천 장르: {genre_name}")
        st.write(f"당신의 성향을 분석한 결과 **{genre_name}** 장르가 가장 잘 어울려요!")

        st.divider()

        for movie in movies:
            col1, col2 = st.columns([1, 2])

            with col1:
                if movie["poster_path"]:
                    st.image(POSTER_BASE_URL + movie["poster_path"])

            with col2:
                st.markdown(f"### {movie['title']}")
                st.write(f"⭐ 평점: {movie['vote_average']}")
                st.write(movie["overview"] or "줄거리 정보가 없습니다.")
                st.caption(f"이 영화를 추천하는 이유: 당신의 선택과 잘 어울리는 {genre_name} 감성의 작품이에요.")

            st.divider()
