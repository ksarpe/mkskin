import requests
import datetime
import pandas as pd
import os

from agregations.utils.deliveries import delivery_methods
from agregations.clients import check_existing_clients

def get_orders(ACCESS_TOKEN, API_BASE_URL, days_amount):

    url = f"{API_BASE_URL}/order/checkout-forms"
    date = datetime.datetime.now() - datetime.timedelta(days=days_amount)
    date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    orders = []

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    params = {
        "limit": 100,
        "lineItems.boughtAt.gte": date,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for event in data.get('checkoutForms', []):
            date = event["payment"]["finishedAt"]
            date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            date = date + datetime.timedelta(hours=1)
            formatted_date = date.strftime("%d %H:%M")
            if event["delivery"]["method"]["id"] not in delivery_methods.keys():
                delivery = event["delivery"]["method"]["id"], formatted_date
            else:
                delivery = delivery_methods[event["delivery"]["method"]["id"]] #event["delivery"]["method"]["id"]
            invoice = "TRUE" if event["invoice"]["required"] else "FALSE"
            existing_client = check_existing_clients(ACCESS_TOKEN, API_BASE_URL, event["buyer"]["login"])
            phone_number = event["buyer"]["phoneNumber"][3:]
            price = event["summary"]["totalToPay"]["amount"] #TODO: change in the future to get all items from the cart
            quantity = check_quantity(price)
            smart = "TAK" if event["delivery"]["smart"] else "NIE"
            deliveryCost = event["delivery"]["cost"]["amount"] if float(event["delivery"]["cost"]["amount"]) > 0 else ""

            orders.append({
            "Data": formatted_date,
            "Platforma": "Allegro",
            "Dostawa": delivery,
            "Faktura?": invoice,
            "Istniejący klient?": existing_client,
            "NR Telefonu": phone_number,
            "Ilość": quantity,
            "Cena": price.replace(".", ","),
            "Smart?": smart,
            "X": "",
            "Y": "",
            "Z": "",
            "Koszt Dostawy": deliveryCost,
            })
        
    except requests.exceptions.RequestException as e:
        print(f"Błąd przy pobieraniu statystyk sprzedaży: {e}")
    except KeyError as e:
        print(f"Błąd w strukturze danych: {e}")
    
    df = pd.DataFrame(orders[::-1])
    df.to_excel("result/orders.xlsx", index=False)
    print("Zapisano zamówienia do pliku orders.xlsx")
    print("Otwieram plik...")
    os.startfile("E:\\xampp\\htdocs\\allegroapp\\result\\orders.xlsx")


def check_quantity(price):
    price = float(price)
    if price < 100.0:
        return 1
    elif price < 170.0:
        return 2
    elif price < 260.0:
        return 3
    elif price < 350.0:
        return 4
    elif price < 400.0:
        return 5
    