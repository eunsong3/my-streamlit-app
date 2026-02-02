import streamlit as st

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="centered")

st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문 5개로 당신의 성향을 파악해, 어울리는 영화 타입을 찾아볼게요!")
st.caption("※ 결과 분석/추천은 다음 시간에 API로 연동할 예정입니다 🙂")

st.divider()

# 1) 주말에 가장 하고 싶은 것은?
q1 = st.radio(
    "1. 주말에 가장 하고 싶은 것은?",
    ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    index=None,
)

# 2) 스트레스 받으면?
q2 = st.radio(
    "2. 스트레스 받으면?",
    ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    index=None,
)

# 3) 영화에서 중요한 것은?
q3 = st.radio(
    "3. 영화에서 중요한 것은?",
    ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    index=None,
)

# 4) 여행 스타일?
q4 = st.radio(
    "4. 여행 스타일?",
    ["계획적", "즉흥적", "액티비티", "힐링"],
    index=None,
)

# 5) 친구 사이에서 나는?
q5 = st.radio(
    "5. 친구 사이에서 나는?",
    ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    index=None,
)

st.divider()

# 결과 보기 버튼
if st.button("결과 보기", type="primary"):
    answers = [q1, q2, q3, q4, q5]
    if any(a is None for a in answers):
        st.warning("모든 질문에 답변해 주세요!")
    else:
        st.info("분석 중...")
