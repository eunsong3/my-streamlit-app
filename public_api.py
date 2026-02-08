# public_api.py

import requests
import xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "http://openapi.epost.go.kr"
PATH = "/postal/retrieveAlddlChargeService/retrieveAlddlChargeService/getAlddlChargeList"

def fetch_mobile_plans(service_key, rows=30):
    url = BASE_URL + PATH

    params = {
        "ServiceKey": service_key,   # 반드시 URL Encode된 키
        "numOfRows": rows,
        "pageNo": 1
    }

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1.5)
    session.mount("http://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, params=params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise RuntimeError("공공데이터 서버 연결 실패")

    root = ET.fromstring(response.content)

    # 명세서 기준: alddlCharge (소문자)
    items = root.findall(".//alddlCharge")

    plans = []
    for item in items:
        price = item.findtext("chargeAmount", "0")
        data_mb = item.findtext("dataAmount", "0")

        if not price.isdigit() or not data_mb.isdigit():
            continue

        plans.append({
            "name": item.findtext("chargeName"),
            "price": int(price),
            "data_gb": int(data_mb) / 1024,
            "device_support": "unlocked"
        })

    if not plans:
        raise RuntimeError("요금제 데이터가 없습니다 (응답은 성공)")

    return plans
