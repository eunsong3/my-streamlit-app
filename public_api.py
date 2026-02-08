# public_api.py

import requests
import xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://openapi.epost.go.kr"
PATH = "/postal/retrieveAlddlChargeService/retrieveAlddlChargeService/getAlddlChargeList"

def fetch_mobile_plans(service_key, rows=50):
    url = BASE_URL + PATH

    params = {
        "ServiceKey": service_key,  # ✅ Encoding Key 필수
        "numOfRows": rows,
        "pageNo": 1
    }

    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, params=params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError("우체국 알뜰폰 API 연결 실패") from e

    root = ET.fromstring(response.content)
    plans = []

    for item in root.findall(".//AlddlCharge"):
        price = item.findtext("chargeAmount", "0")
        data_mb = item.findtext("dataAmount", "0")

        if not price.isdigit() or not data_mb.isdigit():
            continue

        plans.append({
            "carrier": item.findtext("telecomName"),
            "name": item.findtext("chargeName"),
            "price": int(price),
            "data_gb": int(data_mb) / 1024,
            "device_support": "unlocked"
        })

    if not plans:
        raise RuntimeError("API 응답은 받았으나 요금제 데이터가 없습니다")

    return plans
