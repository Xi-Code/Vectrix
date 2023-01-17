# Imports
from flask import Flask, request, render_template, redirect, url_for
from gpt_processor import ProcessQuestion
from send_message import SendMessage
import json

app = Flask(__name__)

def load_data():
    try:
        with open("data.json", "r") as json_file:
            data = json.load(json_file)
            return data
    except:
        return None


@app.route('/whatsapp', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')
        if mode == 'subscribe' and verify_token == 'vitothecat':
            return challenge
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        data = request.get_json()
        try:
            answer, conversation = ProcessQuestion(data)
            print('Printing conversation: \n')
            print(conversation)
            SendMessage(answer)
        except Exception as e:
            print(e)
            return "OK", 200

        return 'OK', 200

@app.route('/update', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        chat_context = request.form['chat_context']
        sender_phone_number = request.form['sender_phone_number']
        data = {'chat_context': chat_context, 'sender_phone_number': sender_phone_number}
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)
        return 'Form submitted successfully!'
    else:
        data=load_data()   
    return render_template('update_settings.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)
