import requests
import logging
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)  
import time

from tokens.secrets import CLIENT_IDS, CLIENT_SECRETS

CLIENT_ID = CLIENT_IDS
CLIENT_SECRET = CLIENT_SECRETS

def get_device_code(BASE_OAUTH_URL):
    """
    1. Pobiera 'device_code', 'user_code', 'verification_uri' i 'verification_uri_complete'
       od Allegro z wykorzystaniem tzw. 'Device Flow'.
       Zwraca słownik (dict) z odpowiedzią.
    """
    url = f"{BASE_OAUTH_URL}/device"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET)  # BasicAuth
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd przy pobieraniu device_code: {e}")
        return None


def get_access_token(device_code, BASE_OAUTH_URL):

    url = f"{BASE_OAUTH_URL}/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code
    }

    while True:
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(CLIENT_ID, CLIENT_SECRET)  # BasicAuth
            )

            if response.status_code == 200:
                token_data = response.json()
                ACCESS_TOKEN = token_data["access_token"]
                REFRESH_TOKEN = token_data.get("refresh_token", None)
                #Write tokens to file
                with open("tokens/tokens.txt", "w") as f:
                    f.write(ACCESS_TOKEN + "\n")
                    f.write(REFRESH_TOKEN + "\n")
                print("Pomyślnie zapisano ACCESS_TOKEN i REFRESH_TOKEN.")
                return True
            else:
                error_json = response.json()
                error_code = error_json.get("error")
                
                if error_code == "authorization_pending":
                    # Urządzenie czeka na potwierdzenie użytkownika. Jeszcze nie kliknięto "Zezwól".
                    print("Czekam na potwierdzenie w przeglądarce (authorization_pending)...")
                    time.sleep(5)  # Poczekaj 5 sekund i spróbuj ponownie
                elif error_code == "slow_down":
                    # Allegro mówi, żeby zmniejszyć częstotliwość pytań
                    print("Zbyt częste zapytania (slow_down). Czekam 10 sekund...")
                    time.sleep(10)
                else:
                    # Np. "access_denied", "expired_token" itp.
                    print(f"Błąd przy pobieraniu tokenu: {error_json}")
                    return False

        except requests.exceptions.RequestException as e:
            print(f"Błąd sieciowy przy pobieraniu tokenu: {e}")
            return False


def refresh_access_token(BASE_OAUTH_URL):

    with open("tokens/tokens.txt", "r") as f:
        #read first line of the file and save to variable
        f.readline()  # Skip the first line
        refresh_token = f.readline().strip()
        print("wczytano REFRESH_TOKEN z pliku, przechodzę do odświeżenia ACCESS_TOKEN")

    url = f"{BASE_OAUTH_URL}/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET)  # BasicAuth
        )
        response.raise_for_status()

        token_data = response.json()
        ACCESS_TOKEN = token_data["access_token"]
        REFRESH_TOKEN = token_data.get("refresh_token", None)
        with open("tokens/tokens.txt", "w") as f:
                    f.write(ACCESS_TOKEN + "\n")
                    f.write(REFRESH_TOKEN)
        print("Pomyślnie odświeżono ACCESS_TOKEN.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Nie udało się odświeżyć tokenu: {e}")
        return False
    

def fetch_tokens(BASE_OAUTH_URL, API_BASE_URL):
    with open("tokens/tokens.txt", "r") as f:
        #read first line of the file and save to variable
        ACCESS_TOKEN = f.readline().strip()
        REFRESH_TOKEN = f.readline().strip()

        if ACCESS_TOKEN == "":
            #If there is no access token we have to get one and save it to the file
            device_data = get_device_code(BASE_OAUTH_URL)
            if not device_data:
                print("Nie udało się pobrać device_code.")
                return

            print("\n==== AUTORYZACJA DEVICE FLOW ====")
            print(f"1) Otwórz w przeglądarce adres:   {device_data['verification_uri_complete']}")
            print(f"2) W razie potrzeby wpisz kod:    {device_data['user_code']}")
            print("3) Zezwól aplikacji na dostęp, a następnie wróć tutaj.\n")

            # Próbujemy wymienić device_code na access_token
            success = get_access_token(device_data["device_code"], BASE_OAUTH_URL)
            if not success:
                print("Nie udało się uzyskać ACCESS_TOKEN!")
                return
            ACCESS_TOKEN = f.readline().strip()
            REFRESH_TOKEN = f.readline().strip()
        
        else:
            #CHECK IF TOKENS ARE OKAY
            url = f"{API_BASE_URL}/order/checkout-forms"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Accept": "application/vnd.allegro.public.v1+json"
            }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Token jest prawdopodobnie przedawniony! error: {e}")
                print(f"Odświeżam token...")
                response = refresh_access_token(BASE_OAUTH_URL)
                if not response:
                    return
                with open("tokens/tokens.txt", "r") as f2:
                    ACCESS_TOKEN = f2.readline().strip()
                    REFRESH_TOKEN = f2.readline().strip()
                print("Odświeżono oba tokeny.")              

    
        print("Wczytano ACCESS_TOKEN i REFRESH_TOKEN z pliku.")
    return ACCESS_TOKEN, REFRESH_TOKEN
    