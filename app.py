import streamlit as st
import requests

# =============================
# 기본 설정
# =============================
st.set_page_config(
    page_title="🎬 나와 어울리는 영화는?",
    page_icon="🎬",
    layout="wide"
)

# =============================
# CSS (Netflix 카드 스타일)
# =============================
st.markdown(
    """
    <style>
    .movie-card {
        background-color: #141414;
        padding: 15px;
        border-radius: 12px;
        height: 100%;
        color: white;
    }
    .movie-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .movie-rating {
        color: #f5c518;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .movie-overview {
        font-size: 14px;
        line-height: 1.4;
        color: #dddddd;
    }
    .movie-reason {
        font-size: 13px;
        margin-top: 10px;
        color: #bbbbbb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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


# =============================
# 성향 분석
# =============================
def analyze_answers(answers):
    scores = {g: 0 for g in GENRES}

    mapping = [
        ("집에서 휴식", {"드라마": 2, "로맨스": 1}),
        ("친구와 놀기", {"코미디": 2}),
        ("새로운 곳 탐험", {"액션": 2, "판타지": 1}),
        ("혼자 취미생활", {"SF": 2}),
    ]
    for key, pts in mapping:
        if answers[0] == key:
            for g, v in pts.items():
                scores[g] += v

    if answers[1] == "수다 떨기":
        scores["코미디"] += 2
        scores["로맨스"] += 1
    elif answers[1] == "운동하기":
        scores["액션"] += 2
    elif answers[1] == "혼자 있기":
        scores["드라마"] += 2

    if answers[2] == "감동 스토리":
        scores["드라마"] += 2
        scores["로맨스"] += 1
    elif answers[2] == "시각적 영상미":
        scores["SF"] += 2
        scores["판타지"] += 2
    elif answers[2] == "웃는 재미":
        scores["코미디"] += 3

    if answers[3] == "액티비티":
        scores["액션"] += 3
    elif answers[3] == "힐링":
        scores["로맨스"] += 2
        scores["드라마"] += 1

    if answers[4] == "분위기 메이커":
        scores["코미디"] += 2
    elif answers[4] == "주도하기":
        scores["액션"] += 2

    best_genre = max(scores, key=scores.get)
    return best_genre, GENRES[best_genre]


# =============================
# TMDB API
# =============================
def fetch_movies(api_key, genre_id, min_rating):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key.strip(),
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "vote_average.gte": min_rating,
        "page": 1
    }

    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        st.error("TMDB API 요청 실패")
        st.json(r.json())
        return []

    data = r.json()
    return data.get("results", [])[:7]


# =============================
# UI
# =============================
st.title("🎬 나와 어울리는 영화는?")
st.write("당신의 성향을 분석해 **지금 보면 딱 좋은 영화**를 추천해드려요.")

with st.sidebar:
    st.header("🔑 TMDB 설정")
    api_key = st.text_input("TMDB API Key", type="password")
    min_rating = st.slider("⭐ 최소 평점", 0.0, 9.0, 6.5, 0.5)

st.divider()

questions = [
    st.radio("1. 주말에 가장 하고 싶은 것은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"], index=None),
    st.radio("2. 스트레스 받으면?", ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"], index=None),
    st.radio("3. 영화에서 중요한 것은?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"], index=None),
    st.radio("4. 여행 스타일?", ["계획적", "즉흥적", "액티비티", "힐링"], index=None),
    st.radio("5. 친구 사이에서 나는?", ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"], index=None),
]

st.divider()

# =============================
# 결과
# =============================
if st.button("결과 보기", type="primary"):
    if None in questions:
        st.warning("모든 질문에 답해주세요!")
        st.stop()
    if not api_key:
        st.error("TMDB API Key를 입력해주세요!")
        st.stop()

    with st.spinner("분석 중..."):
        genre_name, genre_id = analyze_answers(questions)
        movies = fetch_movies(api_key, genre_id, min_rating)

    st.subheader(f"🎯 추천 장르: {genre_name}")
    st.write(
        f"""
        당신은 **{genre_name} 장르**에서 만족도가 높을 가능성이 커요.  
        감정선, 몰입도, 전개 속도 모두 당신의 선택 패턴과 잘 맞는 영화들이에요.
        """
    )

    cols = st.columns(4)

    for idx, movie in enumerate(movies):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{POSTER_BASE_URL + movie['poster_path'] if movie.get('poster_path') else ''}" width="100%">
                    <div class="movie-title">{movie.get('title')}</div>
                    <div class="movie-rating">⭐ {movie.get('vote_average')}</div>
                    <div class="movie-overview">{movie.get('overview', '줄거리 정보 없음')[:120]}...</div>
                    <div class="movie-reason">
                        이 영화는 당신이 선호한 <b>{genre_name}</b> 감성과 잘 어울리며,  
                        평점 조건을 충족한 작품이라 몰입해서 보기 좋아요.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
