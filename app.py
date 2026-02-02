turn: (genre_name, genre_id, reason, scores)
import streamlit as st
import requests
from typing import Dict, List, Tuple

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="centered")

# -----------------------------
# TMDB / Genre settings
# -----------------------------
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}
POSTER_BASE = "https://image.tmdb.org/t/p/w500"


# -----------------------------
# Helpers: scoring & reasoning
# -----------------------------
def analyze_answers(answers: Dict[str, str]) -> Tuple[str, int, str, Dict[str, int]]:
    """
    answers: {"q1": "...", "q2": "...", ...}
    return: (genre_name, genre_id, reason, scores)
    """
    scores = {g: 0 for g in GENRES.keys()}
    reasons: List[str] = []

    # Q1
    a = answers["q1"]
    if a == "집에서 휴식":
        scores["드라마"] += 2
        scores["로맨스"] += 1
        reasons.append("주말에는 편하게 쉬는 걸 선호")
    elif a == "친구와 놀기":
        scores["코미디"] += 2
        scores["로맨스"] += 1
        reasons.append("사람들과 어울리며 즐기는 편")
    elif a == "새로운 곳 탐험":
        scores["액션"] += 2
        scores["판타지"] += 1
        scores["SF"] += 1
        reasons.append("새로운 자극/모험을 좋아함")
    elif a == "혼자 취미생활":
        scores["SF"] += 2
        scores["판타지"] += 1
        scores["드라마"] += 1
        reasons.append("혼자 몰입하는 시간을 즐김")

    # Q2
    a = answers["q2"]
    if a == "혼자 있기":
        scores["드라마"] += 2
        reasons.append("스트레스는 혼자 정리하며 푸는 편")
    elif a == "수다 떨기":
        scores["코미디"] += 1
        scores["로맨스"] += 2
        reasons.append("대화로 감정을 해소하는 편")
    elif a == "운동하기":
        scores["액션"] += 2
        scores["SF"] += 1
        reasons.append("에너지를 움직임으로 푸는 편")
    elif a == "맛있는 거 먹기":
        scores["코미디"] += 2
        scores["드라마"] += 1
        reasons.append("소확행으로 기분전환하는 편")

    # Q3
    a = answers["q3"]
    if a == "감동 스토리":
        scores["드라마"] += 2
        scores["로맨스"] += 1
        reasons.append("감정선/스토리를 중시")
    elif a == "시각적 영상미":
        scores["SF"] += 2
        scores["판타지"] += 2
        reasons.append("화려한 비주얼과 세계관을 선호")
    elif a == "깊은 메시지":
        scores["드라마"] += 2
        scores["SF"] += 1
        reasons.append("생각할 거리를 주는 작품을 선호")
    elif a == "웃는 재미":
        scores["코미디"] += 3
        reasons.append("웃음과 텐션을 중요하게 생각")

    # Q4
    a = answers["q4"]
    if a == "계획적":
        scores["드라마"] += 1
        scores["SF"] += 1
        reasons.append("차근차근 전개되는 흐름을 선호")
    elif a == "즉흥적":
        scores["코미디"] += 2
        scores["액션"] += 1
        reasons.append("즉흥적이고 가벼운 전개를 선호")
    elif a == "액티비티":
        scores["액션"] += 3
        reasons.append("역동적이고 스피디한 걸 좋아함")
    elif a == "힐링":
        scores["로맨스"] += 2
        scores["판타지"] += 1
        scores["드라마"] += 1
        reasons.append("따뜻한 분위기의 작품이 잘 맞음")

    # Q5
    a = answers["q5"]
    if a == "듣는 역할":
        scores["드라마"] += 2
        scores["로맨스"] += 1
        reasons.append("공감 능력이 높은 편")
    elif a == "주도하기":
        scores["액션"] += 2
        scores["SF"] += 1
        reasons.append("주도적으로 이끄는 타입")
    elif a == "분위기 메이커":
        scores["코미디"] += 2
        reasons.append("분위기를 밝게 만드는 타입")
    elif a == "필요할 때 나타남":
        scores["SF"] += 2
        scores["판타지"] += 1
        reasons.append("쿨하게 핵심만 챙기는 타입")

    # Pick top genre (tie-break by predefined order)
    order = ["액션", "코미디", "드라마", "SF", "로맨스", "판타지"]
    top_score = max(scores.values())
    candidates = [g for g, s in scores.items() if s == top_score]
    genre_name = next(g for g in order if g in candidates)
    genre_id = GENRES[genre_name]

    # Make short recommendation reason
    # Use up to 2-3 reason bullets merged
    short = " / ".join(reasons[:3]) if reasons else "당신의 선택 패턴을 기반으로 추천했어요."
    reason = f"**{genre_name}** 장르를 추천하는 이유: {short}"

    return genre_name, genre_id, reason, scores


@st.cache_data(show_spinner=False, ttl=600)
def fetch_popular_movies_by_genre(api_key: str, genre_id: int) -> List[dict]:
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "page": 1,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])


def movie_reason(genre_name: str, user_reason: str, movie: dict) -> str:
    """
    간단한 추천 이유 텍스트
    """
    title = movie.get("title") or movie.get("name") or "이 작품"
    vote = movie.get("vote_average", 0)

    # 아주 짧게: 장르 적합 + 평점/인기도 언급
    if vote and vote >= 7.5:
        return f"{title}은(는) 당신에게 맞는 **{genre_name}** 감성을 잘 담고 있고, 평점도 높아 몰입하기 좋아요."
    return f"{title}은(는) 당신이 선호한 분위기와 가까운 **{genre_name}** 계열이라 가볍게 시작하기 좋아요."


# -----------------------------
# UI
# -----------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문 5개로 당신의 성향을 파악해, 어울리는 영화 장르와 인기 영화를 추천해드려요!")

with st.sidebar:
    st.header("🔑 TMDB 설정")
    api_key = st.text_input("TMDB API Key", type="password", help="TMDB에서 발급받은 API Key를 입력하세요.")
    st.caption("키는 저장되지 않으며, 이 세션에서만 사용돼요.")

st.divider()

q1 = st.radio(
    "1. 주말에 가장 하고 싶은 것은?",
    ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    index=None,
)
q2 = st.radio(
    "2. 스트레스 받으면?",
    ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    index=None,
)
q3 = st.radio(
    "3. 영화에서 중요한 것은?",
    ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    index=None,
)
q4 = st.radio(
    "4. 여행 스타일?",
    ["계획적", "즉흥적", "액티비티", "힐링"],
    index=None,
)
q5 = st.radio(
    "5. 친구 사이에서 나는?",
    ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    index=None,
)

st.divider()

if st.button("결과 보기", type="primary"):
    answers = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}

    if any(v is None for v in answers.values()):
        st.warning("모든 질문에 답변해 주세요!")
        st.stop()

    if not api_key.strip():
        st.error("사이드바에 TMDB API Key를 입력해 주세요!")
        st.stop()

    with st.spinner("분석 중..."):
        genre_name, genre_id, user_reason, scores = analyze_answers(answers)

        # Fetch movies
        try:
            results = fetch_popular_movies_by_genre(api_key.strip(), genre_id)
        except requests.HTTPError as e:
            st.error("TMDB 요청에 실패했어요. API Key가 올바른지 확인해 주세요.")
            st.caption(f"오류: {e}")
            st.stop()
        
