# data_calculator.py

def estimate_monthly_data(hours_per_day, apps, heavy_download):
    data = 0

    if hours_per_day < 1:
        data += 3
    elif hours_per_day < 3:
        data += 7
    elif hours_per_day < 5:
        data += 15
    else:
        data += 25

    if "YouTube" in apps:
        data += 10
    if "Netflix" in apps:
        data += 15
    if "Instagram" in apps:
        data += 5

    if heavy_download:
        data += 10

    return data
