# data_calculator.py

def calculate_monthly_data(hours_per_week, apps, downloads):
    base = 0.3
    weights = {
        "SNS/메신저": 1.0,
        "유튜브/넷플릭스": 2.5,
        "게임": 2.0,
        "지도/검색": 0.8
    }

    weekly = hours_per_week * base
    weekly *= sum(weights[a] for a in apps) / len(apps)

    if downloads:
        weekly += 3

    return round(weekly * 4, 1)
