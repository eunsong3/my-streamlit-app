# recommender.py

def recommend_plans(user, plans):
    scored = []

    for plan in plans:
        score = 0

        if plan["price"] <= user["budget"]:
            score += 5
        if plan["data_gb"] >= user["data_usage"]:
            score += 5
        if plan["device_support"] == user["device_type"]:
            score += 2

        scored.append((score, plan))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
