# scenario.py

def classify_user(user):
    if user["is_foreigner"]:
        return "외국인 신입생"
    elif user["want_new_device"]:
        return "기기 교체 희망 신입생"
    else:
        return "경제적 자립 신입생"
