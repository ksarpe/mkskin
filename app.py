CURRENT_VERSION = '1.0.0'
# import os
# os.environ["KCFG_KIVY_LOG_LEVEL"] = "critical"
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from agregations.orders import get_orders
from agregations.bills import get_ad_payments
from tokens.tokens import fetch_tokens
from helpers.updater import check_for_updates
from helpers.checker import check_folders


class App(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        check_folders()
        check_for_updates(CURRENT_VERSION)
        self.BASE_OAUTH_URL = "https://allegro.pl/auth/oauth"
        self.API_BASE_URL = "https://api.allegro.pl"
        self.ACCESS_TOKEN, self.REFRESH_TOKEN = fetch_tokens(self.BASE_OAUTH_URL, self.API_BASE_URL)
    
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        header = Label(
            text="Pomocnik Allegro", font_size=24, size_hint=(1, 0.2)
        )
        layout.add_widget(header)


        btn_payments = Button(
            text="Pobierz płatności reklamowe",
            size_hint=(1, 0.1),
            on_press=self.generate_ad_billing_report,
        )
        layout.add_widget(btn_payments)

        btn_orders_layout = BoxLayout(size_hint=(1, 0.1))
        self.textinput_orders = TextInput(text='', multiline=False, hint_text="1", size_hint=(0.1, 1))
        btn_orders = Button(
            text="Pobierz zamówienia z ostatnich X dni",
            size_hint=(0.9, 1),
            on_press=self.generate_buyer_report,
            padding=10
        )
        btn_orders_layout.add_widget(self.textinput_orders)
        btn_orders_layout.add_widget(btn_orders)
        layout.add_widget(btn_orders_layout)

        btn_orders2_layout = BoxLayout(size_hint=(1, 0.1))
        self.textinput_orders_year = TextInput(text='', multiline=False, hint_text="2025", size_hint=(0.1, 1))
        self.textinput_orders_month = TextInput(text='', multiline=False, hint_text="3", size_hint=(0.1, 1))
        btn_orders2 = Button(
            text="Pobierz zamówienia z danego roku i numeru miesiąca)",
            size_hint=(0.9, 1),
            on_press=self.generate_buyer_report_monthly,
            padding=10
        )
        btn_orders2_layout.add_widget(self.textinput_orders_year)
        btn_orders2_layout.add_widget(self.textinput_orders_month)
        btn_orders2_layout.add_widget(btn_orders2)
        layout.add_widget(btn_orders2_layout)

        self.output_label = Label(
            text="Kliknij przycisk, aby wygenerować raport.", size_hint=(1, 0.6)
        )
        layout.add_widget(self.output_label)

        return layout
    
    def generate_ad_billing_report(self, instance):
        get_ad_payments(self.ACCESS_TOKEN, self.API_BASE_URL)
        self.output_label.text = "Pomyślnie zapisano kwotę z reklam do pliku ad_payments.txt."

    def generate_buyer_report(self, instance):
        text = self.textinput_orders.text.strip()
        if not text.isdigit():
            self.output_label.text = "Nie podałeś z ilu dni mają być zamówienia."
            return
        
        orders_from_day = int(text)
        try:
            self.output_label.text = "Generowanie raportów, proszę czekaj..."
            get_orders(self.ACCESS_TOKEN, self.API_BASE_URL, orders_from_day)
            self.output_label.text = f"Pomyślnie wygenerowano zamówienia z {orders_from_day} dni w pliku orders.xlsx."
        except Exception as e:
            self.output_label.text = f"Błąd podczas pobierania zamówień: {e}"

    def generate_buyer_report_monthly(self, instance):
        text = self.textinput_orders_year.text.strip()
        text2 = self.textinput_orders_month.text.strip()
        if not text.isdigit() or not text2.isdigit():
            self.output_label.text = "Nie podałeś roku i miesiąca."
            return
        
        orders_year = int(text)
        orders_month = int(text2)
        try:
            self.output_label.text = "Generowanie raportów, proszę czekaj..."
            get_orders(self.ACCESS_TOKEN, self.API_BASE_URL, year=orders_year, month=orders_month)
            self.output_label.text = f"Pomyślnie wygenerowano zamówienia z {orders_year}/{orders_month} dni w pliku orders.xlsx."
        except Exception as e:
            self.output_label.text = f"Błąd podczas pobierania zamówień: {e}"

if __name__ == "__main__":
    App().run()
