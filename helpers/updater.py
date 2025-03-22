import requests
import os

def check_for_updates(current_version):
  try:
      response = requests.get("https://raw.githubusercontent.com/ksarpe/mkskin/master/version.json")
      response.raise_for_status()
      data = response.json()

      server_version = data["version"]

      if server_version > current_version:
          print(f"Dostępna nowa wersja: {server_version}")
          download_update(data["download_url"])
      else:
          print("Aplikacja jest aktualna.")
  except Exception as e:
      print(f"Błąd podczas sprawdzania aktualizacji: {e}")

def download_update(download_url):
    print("Pobieranie aktualizacji...")
    response = requests.get(download_url, stream=True)
    update_path = "mkskin.exe"
    
    with open(update_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print("Aktualizacja pobrana. Uruchamianie instalatora...")
    os.system(f'start {update_path}')