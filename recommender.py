# recommender.py

from data import PLANS

def recommend_plans(user):
    scored = []

    for plan in PLANS:
        score = 0
        if plan["price"] <= user["budget"]:
            score += 3
        if plan["data_gb"] >= user["data_usage"]:
            score += 3
        if plan["device_support"] == user["device_type"]:
            score += 2
        scored.append((score, plan))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
