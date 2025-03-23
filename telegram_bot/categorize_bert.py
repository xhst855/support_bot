import requests

BERT_API_URL = "http://bert_service:8000/predict"  # адрес сервиса внутри docker-compose

def categorize_message(text):
    try:
        response = requests.post(BERT_API_URL, json={"text": text})
        response.raise_for_status()
        data = response.json()
        return data.get("category", "Uncategorized")
    except Exception as e:
        print(f"Error contacting BERT service: {e}")
        return "Uncategorized"
