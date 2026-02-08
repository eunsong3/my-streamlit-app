# recommender.py

def recommend_plans(user, plans):
    scored = []

    for p in plans:
        score = 0
        if p["price"] <= user["budget"]:
            score += 5
        if p["data_gb"] >= user["data_usage"]:
            score += 5

        if user["scenario"] == "외국인 유학생" and p["price"] < 35000:
            score += 2
        if user["scenario"] == "경제적 자립 준비 학생" and p["price"] < 30000:
            score += 3
        if user["scenario"] == "기기 교체 희망 학생" and p["data_gb"] >= 30:
            score += 2

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
