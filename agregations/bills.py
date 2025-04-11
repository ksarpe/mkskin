import requests
import datetime

def get_ad_payments(ACCESS_TOKEN, BASE_API_URL):
  #TODO: dni nawet jak nie mmamy reklam
  url = f"{BASE_API_URL}/billing/billing-entries"

  today = datetime.datetime.now()
  start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
  days_passed = (today - start_of_month).days  # Dodajemy 1, aby uwzględnić dzisiejszy dzień
  limit = days_passed
  
  headers = {
      "Authorization": f"Bearer {ACCESS_TOKEN}",
      "Accept": "application/vnd.allegro.public.v1+json"
  }
  params = {
      "type.id": "NSP",
      "limit": limit,
  }

  try:
      with open("result/ad_payments.txt", "w") as f:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for entry in reversed(data.get('billingEntries', [])):
          amount = entry['value']['amount']
          date = entry['occurredAt'][:10]
          f.write(date + ": ")
          f.write((amount.replace('.',',').replace('-','')) + "\n")

  except requests.exceptions.RequestException as e:
      print(f"Błąd przy pobieraniu statystyk sprzedaży: {e}")
  except KeyError as e:
      print(f"Błąd w strukturze danych: {e}")

  print("Pomyślnie zapisano kwotę z reklam do pliku ad_payments.txt.")

    
