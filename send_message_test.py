import requests
import json

url = "https://graph.facebook.com/v15.0/116414838004688/messages"

headers = {
    "Authorization": "Bearer EAAMgG69CWckBAEXtsEKs2bVKi4oKHGyC4PEmqVbJ5HaIF0XmzgZBZBSgVJkfb3ZASEsoU96PKZABOCtMgsXs0JiK20L1I7DHFAkVsZAznxk1k8GrQZCIqoVwLCqcaDn55rZAZCvOrjg82bNLahzNJMLfpZBPZBh03IeADZA7JGgdiEPrz6ZCVZBTOdlFg2ZBLmnctQ65PDcayQ9BW4UbsQXLKgC2lfplZAqZCjY1bnIZD",
    "Content-Type": "application/json"
}

data = {
    "messaging_product": "whatsapp",
    "to": "32479467536",
    "type": "text",
      "text": {
        "preview_url": False,
        "body": "Ik heb je bericht ontvangen. Ik zal je zo snel mogelijk antwoorden."
        }
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    print("Message sent successfully.")
else:
    print("Error sending message. Status code:", response.status_code)
