import os
from pathlib import Path
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher



class ActionSendHTMLForm(Action):
    def name(self) -> Text:
        return "action_send_html_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # HTML form content
        # Read the content of the HTML file
        with open("contact_support.html", "r") as file:
            form_html = file.read()

        # Send the HTML form as a message
        dispatcher.utter_message(text="Sure! Please fill out the form below:")
        dispatcher.utter_message(text=form_html)

        return []

class ValidateContactUsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_contact_us_form"

    def validate_name(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        if value is not None:
            return {"name": value}
        else:
            return {"requested_slot": "name"}

    def validate_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        if value is not None:
            return {"email": value}
        else:
            return {"requested_slot": "email"}

    def validate_number(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        if value is not None:
            return {"number": value}
        else:
            return {"requested_slot": "number"}

    def validate_confirm_details(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        intent_name = tracker.get_intent_of_latest_message()
        if value is not None:
            if intent_name in ["affirm", "deny"]:
                return {"confirm_details": intent_name}
        else:
            return {"requested_slot": "confirm_details"}


class ActionSubmitContactForm(Action):
    def name(self) -> Text:
        return "action_submit_contact_us_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        confirm_details = tracker.get_slot("confirm_details")
        name = tracker.get_slot("name")
        email = tracker.get_slot("email")
        number = tracker.get_slot("number")
        message = tracker.get_slot("message")
        if confirm_details == "affirm":
            this_path = Path(os.path.realpath(__file__))
            user_content = get_html_data(f"{this_path.parent}/utils/user_mail.html")
            send_email("Thank you for contacting us", email, user_content)
            admin_content = get_html_data(f"{this_path.parent}/utils/admin_mail.html")
            admin_content.format(
                name=name,
                email=email,
                number= number,
                message=message
            )
            is_mail_sent = send_email(f"{email.split('@')[0]} contacted us!", "your@gmail.com", admin_content)
            if is_mail_sent:
                dispatcher.utter_message(template="utter_mail_success")
            else:
                dispatcher.utter_message("Sorry, I wasn't able to send mail. Please try again later.")
        else:
            dispatcher.utter_message(template="utter_mail_canceled")
        return []

class ActionStoreName(Action):
    def name(self) -> Text:
        return "action_store_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract first name and last name from the user's message
        first_name = tracker.latest_message.get("entities", {}).get("first_name")
        last_name = tracker.latest_message.get("entities", {}).get("last_name")

        # Set the slots with the extracted values
        return [SlotSet("first_name", first_name), SlotSet("last_name", last_name)]
    

class ActionStoreUserInfo(Action):
    def name(self) -> Text:
        return "action_store_user_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract user information from slots
        name = tracker.get_slot("name")
        username = tracker.get_slot("username")
        
        # Store the user information in the SQLite database
        conn = sqlite3.connect('user_info.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT)")
        cursor.execute("INSERT INTO users (name, username) VALUES (?, ?)", (name, username))
        conn.commit()
        conn.close()

        # Provide confirmation to the user
        dispatcher.utter_message("Your information has been successfully stored. Thank you!")

        return []    


# class ActionRegister(Action):
#     def name(self) -> Text:
#         return "action_register"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
#         register_category = tracker.get_slot("register_category")
        
#         if register_category == "Learner" :
#             dispatcher.utter_message(text="These are the requirements for students:\n"
#                                            "1. A certified copy of an ID document\n"
#                                            "2. A certified copy of a Grade 11 final report or Matric mid-year report\n"
#                                            "3. Proof of acceptance at a university, university of technology, or TVET college for 2024")
#         elif register_category == "Assessor":
#             dispatcher.utter_message(text="People wishing to be registered as assessors with the MQA should:\n"
#                                            "1. Be found competent by an ETDPSETA accredited training provider, and\n"
#                                            "2. Be a subject matter expert (either through experience minimum of 2 years and qualification/s) in a mining and minerals related field in which they wish to assess")
#         elif register_category == "Moderator":
#             dispatcher.utter_message(text="People wishing to be registered as moderators with the MQA should:\n"
#                                            "1. Be MQA registered assessors; and\n"
#                                            "2. Be found competent as moderators by an ETDPSETA accredited training provider")
#         else:
#             dispatcher.utter_message(text="Invalid registration category.")
        
#         return []
