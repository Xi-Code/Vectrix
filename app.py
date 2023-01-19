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
    '''
    This function handles the webhook for the WhatsApp API
    '''
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
            # Check if the messages element is present
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                # Check if the message is a text message
                if 'text' in data['entry'][0]['changes'][0]['value']['messages'][0]:
                    # Check if the message is not empty
                    if data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] != '':
                        # Process the question
                        answer, conversation = ProcessQuestion(data)
                        print('Printing conversation: \n')
                        print(conversation)
                        SendMessage(answer)
        except Exception as e:
            print(e)
            return "Unable to process request", 500

        return 'OK', 200

@app.route('/update', methods=['GET', 'POST'])
def update_settings():
    '''
    This function creates a form to update the chat context and configures the WhatsApp API
    '''
    if request.method == 'POST':
        sender_phone_number = request.form['sender_phone_number']
        company_name = request.form['company_name']
        company_business_type = request.form['company_business_type']
        data = {'sender_phone_number': sender_phone_number,
                'company_name': company_name,
                'company_business_type': company_business_type
                }
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)
        return 'Form submitted successfully!'
    else:
        data=load_data()   
    return render_template('update_settings.html',data=data)

if __name__ == '__main__':
    app.run(debug=True) 
