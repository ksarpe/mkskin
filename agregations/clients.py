import requests
import datetime

def check_existing_clients(ACCESS_TOKEN, BASE_API_URL, buyer_login):
    url = f"{BASE_API_URL}/order/checkout-forms"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    params = {
        "limit": 25,
        "buyer.login": buyer_login,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data['totalCount'] > 1:
            return "TAK"
        return "NIE"
        
        
    except requests.exceptions.RequestException as e:
        print(f"Błąd przy pobieraniu statystyk sprzedaży: {e}")
    except KeyError as e:
        print(f"Błąd w strukturze danych: {e}")