import requests
import json
import configparser

# Read config file
config = configparser.ConfigParser()
config.read('keys/config.ini')

def SendMessage(message):
    url = "https://graph.facebook.com/v15.0/116414838004688/messages"

    headers = {
    "Authorization": "Bearer " + config['API_KEYS']['whatsapp'],
    "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": "32479467536",
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
            }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(response.status_code)
    else:
        print(response.status_code)
