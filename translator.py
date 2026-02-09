import requests

def translate(text, target_lang, api_key):
    if not api_key or target_lang == "KO":
        return text
    res = requests.post(
        "https://api-free.deepl.com/v2/translate",
        headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
        data={"text": text, "target_lang": target_lang}
    )
    return res.json()["translations"][0]["text"]
