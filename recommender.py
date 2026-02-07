# recommender.py

from data import PLANS

def recommend_plans(user):
    scored_plans = []

    for plan in PLANS:
        score = 0

        # 예산
        if plan["price"] <= user["budget"]:
            score += 3

        # 데이터
        if plan["data_gb"] >= user["data_usage"]:
            score += 3

        # 단말 유형
        if plan["device_support"] == user["device_type"]:
            score += 2

        # OTT 혜택
        for ott in user["ott_apps"]:
            if ott in plan["ott_free"]:
                score += 1

        scored_plans.append((score, plan))

    scored_plans.sort(key=lambda x: x[0], reverse=True)
    return [plan for score, plan in scored_plans[:3]]
