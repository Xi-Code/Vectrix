# Imports
from flask import Flask, request
from gpt_processor import ProcessQuestion
from send_message import SendMessage

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run()
