from flask import Flask, request

app = Flask(__name__)

@app.route('/whatsapp', methods=['GET'])
def handle_verification():
    mode = request.args.get('hub.mode')
    challenge = request.args.get('hub.challenge')
    verify_token = request.args.get('hub.verify_token')
    if mode == 'subscribe' and verify_token == 'vitothecat':
        return challenge
    else:
        return 'Verification token mismatch', 403


# Launch the Flask dev server
if __name__ == '__main__':
    app.run()

