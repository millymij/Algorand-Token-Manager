import vonage
import json
import os
import logging
from flask import jsonify


# API keys saved in environment variables
api_key = os.getenv('VONAGE_API_KEY')
api_secret = os.getenv('VONAGE_API_SECRET')
if not api_key or not api_secret:
    raise ValueError("API key or secret is not set in the environment variables.")
client = vonage.Client(key=api_key, secret=api_secret)


'''
    Send SMS text.
'''
def send_sms_text(sender_number, receiver_number, text):
    try:
        response = client.sms.send_message({
        "from": sender_number,
        "to": receiver_number,
        "text": text,
        })

        # success reponse
        if response["messages"][0]["status"] == "0":
            logging.info('SMS sent successfully!')
            print('SMS sent successfully!')
            return True

        # error response
        else:
            error_text = response["messages"][0].get("error-text", "An error occurred.")
            print(f"SMS sending failed.")
            logging.error(f"SMS sending failed with status {response['messages'][0].get('status')}: {error_text}")
            return False
    
    except Exception as e:
        print(f"An error occurred while sending SMS: {str(e)}")
        logging.exception(f"An error occurred while sending SMS: {str(e)}")
        return False


''' 
    Receive SMS text.
'''
def receive_sms_text(request):
    if request.is_json:
        data = request.get_json()
        print(data)
    else:
        data = dict(request.form) or dict(request.args)
        print(data)
    try:
        # writing sms data in a json file
        with open('tmp/received_sms_data.json', 'w') as f:
            json.dump(data, f)
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500



    
