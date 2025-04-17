import sqlite3
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime


class ActionCheckTableAvailability(Action):

    def name(self) -> Text:
        return "action_check_table_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer la date
        date = tracker.get_slot("date")

        #Pas de date, on met aujourd'hui (ce midi / ce soir)
        if not date:
            date = datetime.datetime.now().strftime("%x")

        # Connexion à la base de données SQLite
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()

                # Compter les réservations pour cette date
                cursor.execute("SELECT COUNT(*) FROM Reservation WHERE date = ?", (date,))
                result = cursor.fetchone()
                current_reservations = result[0] if result else 0

                MAX_TABLES = 2

                if current_reservations < MAX_TABLES:
                    dispatcher.utter_message(text=f"Oui ! Il y a encore des tables disponibles le {date}.")
                    return [SlotSet("table_dispo", True)]
                else:
                    dispatcher.utter_message(text=f"Désolé, toutes les tables sont déjà réservées pour le {date}.")
                    return [SlotSet("table_dispo", False)]

        except sqlite3.Error as e:
            dispatcher.utter_message(text="Il y a eu un problème avec la base de données pour action action_check_table_availability. Essayez plus tard.")
            return [SlotSet("table_dispo", False)]


class ActionReserveTable(Action):

    def name(self) -> Text:
        return "action_reservation_table"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer des données
        name = tracker.get_slot("name")
        date = tracker.get_slot("date")
        phone = tracker.get_slot("phone")
        comment = tracker.get_slot("comment")
        nb_person = tracker.get_slot("nb_person")

        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()

                # Compter les réservations pour cette date
                reservation_data = (name, comment, nb_person, date, phone)

                # Exécution de l'insert
                cursor.execute("""
                    INSERT INTO Reservation ( name, comment, person_nb, date, phone)
                    VALUES (?, ?, ?, ?, ?)
                """, reservation_data)

                # Sauvegarde (commit) et fermeture
                conn.commit()

                cursor.execute("SELECT id FROM Reservation WHERE date = ? AND name = ?", (date, name))
                result = cursor.fetchone()
                current_reservations = result[0] if result else 0

                dispatcher.utter_message(text=f"Votre réservation au nom de {name} est bien enregistrée le {date}. Votre numéro de réservation est le {current_reservations}")
                return []



        except sqlite3.Error as e:
            dispatcher.utter_message(text="Il y a eu un problème avec la base de données pour action action_reservation_table. Essayez plus tard.")
            return []

class ActionTodayMenu(Action):

    def name(self) -> Text:
        return "action_today_menu"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()

                # Exécution de l'insert
                cursor.execute("""
                    SELECT 
  (SELECT name FROM Plat WHERE type = 'Entrée' ORDER BY RANDOM() LIMIT 1) AS entree,
  (SELECT name FROM Plat WHERE type = 'Plat' ORDER BY RANDOM() LIMIT 1) AS plat,
  (SELECT name FROM Plat WHERE type = 'Dessert' ORDER BY RANDOM() LIMIT 1) AS dessert;
                """)


                result = cursor.fetchone()
                entree = result[0]
                plat = result[1]
                dessert = result[2]

                dispatcher.utter_message(text=f"""Voici le menu du jour: 
                Entrée {entree}
                Plat {plat}
                Dessert {dessert}
""")
                return []



        except sqlite3.Error as e:
            dispatcher.utter_message(text="Il y a eu un problème avec la base de données pour action action_reservation_table. Essayez plus tard.")
            return []          