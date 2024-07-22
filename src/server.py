import json
from multiprocessing import Process
from flask import Flask, render_template, request, session, jsonify
import werkzeug
import core
import sms_utils
import base64
from algosdk.transaction import LogicSigAccount



#================ INITIALISE FLASK APPLICATION & ALGORAND CLIENT ===================


# Initialise flask apps, one for the UI and one for SMS reception
flask_app = Flask('flask_app', template_folder='src/templates', static_folder='src/static')
app_sms = Flask('app_sms')


# Instantiate client and connect to the Algorand node using the below address and API token.
# Modify "Testing" flag when testing, to avoid the app running on ports and blocking the execution.
flask_app.config.update({
    "TESTING": False
})


# Set secret key for Flask session data
with open('config/secret_key', 'rb') as f:
    flask_app.secret_key = f.read()


'''
    Allow only files with .teal extension.
    Used later when uploading a smart contract.
'''
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'teal'


'''
    Render homepage template.
'''
@flask_app.route('/')
def home():
    return render_template('home.html', current_page='home.html')



#================ SEND TOKEN ===================


'''
    Generate a new Algorand account. Then, write its address, private key and mnemonics in 'generated_accounts.txt' file.
'''
@flask_app.route('/generate_account', methods=['GET', 'POST'])
def generate_account():
    try:
        if request.method == 'GET' or request.method == 'POST':
            account_info = core.generate_account()
            new_address = account_info['address']
            new_private_key = account_info['private_key']
            new_mnemonic = account_info['mnemonic']

            accounts_file_path = 'data/generated_accounts.txt'

            # The account information of the newly generated account will be saved in the 'generated_accounts.txt' file.
            with open(accounts_file_path, 'a') as file:
                file.write(f"Address: {new_address}\n")
                file.write(f"Private Key: {new_private_key}\n")
                file.write(f"Mnemonic: {new_mnemonic}\n")
                file.write("----------\n")
            
            return jsonify({'new_account_address': new_address}), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500



'''
    Given an Algorand account address, fetch its information.
'''
@flask_app.route('/fetch_account', methods=['POST'])
def fetch_account():
    account_address = request.form.get('account_to_fetch')

    if not account_address:
        return jsonify({'error': 'Invalid account address provided'}), 400

    try:
        account_info = core.fetch_info(account_address)
        if account_info:

            balance = account_info.get('amount') / 1e6 # balance in microAlgos
            fetched_account_info = f"Address: {account_address}\nBalance: {balance} Algos\nInfo: {account_info}"
            return jsonify({'account_address': account_address, 'fetched_account_info': fetched_account_info}), 200
        
    except Exception as e:
        print(f"Error fetching account info: {str(e)}")
        return jsonify({'error': str(e)}), 500
    


'''
    Generate a LogicSignature from the .teal file uploaded.
    Then, save the LogicSignature into the session data.
'''
@flask_app.route('/generate_logic_signature', methods=['POST'])
def generate_logic_signature():
    try:
        # check the uploading of .teal contract file
        if 'file' not in request.files:
            return jsonify({'message': 'No file part', 'success': False}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'message': 'No selected file or file type not allowed', 'success': False}), 400
        
        # read and decode .teal file in utf-8
        teal_source = file.read().decode('utf-8')
        
        # create the lsig out of the TEAL file
        lsig = core.create_lsig(teal_source)
        if not lsig:
                raise ValueError("Failed to generate Logic Signature due to invalid TEAL code.")

        # convert lsig in a string such that it can be saved in session data.
        # dictify the lsig object to have access to specific parts of it.
        dictifiedLsig = lsig.dictify()
        # extract the logic part of the lsig ('l'), representing the teal program in bytes.
        teal_program_bytes = dictifiedLsig['lsig']['l']
        # encode teal bytes into a base64 bytes object. Then, decode base64 bytes object into a UTF-8 string.
        serialized_lsig = base64.b64encode(teal_program_bytes).decode('utf-8')
        session['lsig'] = serialized_lsig

        return jsonify({'message': 'Logic Signature generated successfully!', 'success': True})
    
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500



'''
    Sign the LogicSignature.
    The LogicSignature will be retrieved from session data, decoded back into an object
    and signed with user's private key input.
'''
@flask_app.route('/sign_lsig', methods=['POST'])
def sign_logic_signature():
    data = request.json
    private_key = data.get('privateKey')
    
    if 'lsig' not in session:
        return jsonify({'message': 'Logic Signature not found.', 'success': False}), 400

    # get lsig string from session
    serialized_lsig = session['lsig']
    # decode in base64
    lsig_logic = base64.b64decode(serialized_lsig)
    # recreate the lsig object
    lsig = core.LogicSigAccount(lsig_logic)
    
    if private_key:
        try:
            # sign lsig
            lsig = core.sign_lsig(lsig, private_key)
            # encode it such that it can be sent via text message
            final_lsig = core.lsig_to_sms_text(lsig)
            
            return jsonify({'message': 'Logic signature signed successfully!', 'success': True, 'final_lsig': final_lsig,}), 200
        
        except Exception as e:
            return jsonify({'message': f'Error signing Logic Signature: {str(e)}', 'success': False}), 500
    else:
        return jsonify({'message': 'No private key provided.', 'success': False}), 400


    
'''
    Upload a file. Check file extension to be .teal.
'''
@flask_app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file', None)
    if file and '.' in file.filename and allowed_file(file.filename):
        filename = werkzeug.utils.secure_filename(file.filename)
        file_path = f'./{filename}'
        file.save(file_path)
        amount = core.extract_txn_amount_from_teal(file_path)
        return jsonify({'amount': amount})
    elif file:
        return jsonify({'error': 'Only .teal files are allowed'}), 400
    else:
            return jsonify({'error': 'No file provided'}), 400
    


'''
    Verify matching between account address and private key.
'''
@flask_app.route('/verify_private_key', methods=['POST'])
def verify_private_key():
    data = request.json
    private_key = data.get('privateKey')
    account_address = data.get('accountAddress')
    if core.check_private_key_against_address(account_address, private_key):
        return jsonify({'isValid': True})
    else:
        return jsonify({'isValid': False})



'''
    Send two SMS from the API's phone number to the number specified by the user.
    The first SMS is an automatic text giving the instructions on how to use the LogicSig text.
    The second SMS contains the LogicSig text itself.
'''
@flask_app.route('/send_sms', methods=['POST'])
def send_sms_endpoint():
    try:
        data = request.json
        sender_number = "Vonage APIs"
        receiver_number = data.get('receiver_number')

        # send first message with a predefined text
        automatic_text = "This message represents your Token. Forward it to redeem it."
        success_predefined = core.send_SMS(sender_number, receiver_number, automatic_text)

        # send second message with the text received from the client (the lsig)
        client_text = data.get('text')
        success_client_text = core.send_SMS(sender_number, receiver_number, client_text)

        # check whether both messages were successfully sent
        if success_predefined and success_client_text:
            return jsonify({'message': 'Both messages were successfully sent.', 'success': True}), 200
        elif success_predefined and not success_client_text:
            return jsonify({'message': 'Only the predefined message was successfully sent.', 'success': False}), 500
        elif not success_predefined and success_client_text:
            return jsonify({'message': 'Only the client message was successfully sent.', 'success': False}), 500
        else:
            return jsonify({'message': 'Failed to send the messages.', 'success': False}), 500
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500



#================ RECEIVE TOKEN ===================


'''
    Receive SMS text. It defines a route to receive SMS messages via a webhook.
    When a message is received, it is saved in a json file.
    
    Arguments format:
    "from": "Vonage APIs",
    "to": "44700000000",
    "text": "Hi!"
    My API virtual number: 447451281414
'''
@app_sms.route('/webhooks/inbound', methods=['POST'])
def receive_sms():
    resp = sms_utils.receive_sms_text(request)
    return resp



'''
    Fetch SMS info from the file where the info were saved. 
'''
@flask_app.route('/fetch_sms_data', methods=['GET'])
def fetch_sms_data():
    session.pop('lsig', None)
    session.pop('decoded_lsig', None)
    message_text, sender_number, receiver_number, timestamp = core.get_data_from_file()
    return jsonify({
        'message_text': message_text,
        'sender_number': sender_number,
        'receiver_number': receiver_number,
        'timestamp': timestamp
    })



'''
    From the SMS received, parse amount limit, address, and token.
'''
def parse_sms_data(text_message):
    lines = text_message.split('\n')
    amount = "Unspecified"
    address = "Unspecified"
    token = "Unspecified"
    for line in lines:
        if 'Amount: ' in line:
            amount = line.split('Amount: ')[1].split(' microAlgos')[0]
        if 'From Address: ' in line:
            address = line.split('From Address: ')[1]
        if 'Your Token: ' in line:
            token = line.split('Your Token: ')[1]
    
    return amount, address, token



'''
    Decode LogicSignature from a SMS text string back into a LogicSig object.
    Fetch the encoded lsig from the file where the received SMS has been saved, 
    then decode it into an object.
'''
@flask_app.route('/decode_lsig', methods=['GET'])
def decode_lsig():
    # read the text message stored in the data.json file
    with open('tmp/received_sms_data.json', 'r') as f:
        data = json.load(f)
        text_message = data.get('text', '')
    
    # parse amount, address and token from received sms
    amount, address, token = parse_sms_data(text_message)
    # save token in session data 
    session['token'] = token
    try:
        # decode from sms text back to lsig object
        lsig_obj = core.sms_text_to_lsig(token)
        if isinstance(lsig_obj, LogicSigAccount):
            # convert it from obj to string to be saved in session
            session['decoded_lsig'] = core.serialize_logic_sig(lsig_obj)
            return jsonify({'message': 'Successful decoding, ready to be used for transaction', 'success': True, 'amount': amount, 'address': address}), 200
        else:
            return jsonify({'message': 'Decoding failed or returned an unexpected object type', 'success': False}), 500
    except Exception as e:
        return jsonify({'message': f'Error during decoding: {str(e)}', 'success': False}), 500



'''
    Create a transaction with the parameters specified by the user and the LogicSig saved in the session.
    The method will also check if the transaction parameters respect the conditions 
    specified in the .teal contract embedded in the lsig.
'''
@flask_app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    senders_address = data.get('sender_address')
    receivers_address = data.get('receiver_address')
    amount = data.get('amount')
    token = session.get('token')

    if not senders_address or not receivers_address or not amount:
        return jsonify({'message': 'All fields must be provided.', 'success': False}), 400

    if 'decoded_lsig' not in session:
        return jsonify({'message': 'Decoded LogicSig not found.', 'success': False}), 400
    logic_sig = session.get('decoded_lsig')
    logic_sig_obj = core.deserialize_logic_sig(logic_sig)

    try:
        if 'decoded_lsig' in session:
            transaction_response = core.construct_lsig_transaction(senders_address, receivers_address, amount, logic_sig_obj, token)
            # send confirmation sms for confirming the successful execution of transaction.
            t, lsig_sender, r, timest = core.get_data_from_file()
            notification_receiver = lsig_sender
            notification_sender = "Vonage APIs"
            text="Your Token has been used to successfully execute a transaction!"

            sms_utils.send_sms_text(notification_sender, notification_receiver, text)
            # after the transaction, remove the decoded_lsig data from the session and from the json file
            erase_token_data('tmp/received_sms_data.json')
            return jsonify({'message': 'Transaction successfully created.', 'success': True})
    
    except Exception as e:
        error_message = str(e)

    # check if transaction conforms to lsig conditions
    if 'rejected by logic' in error_message:
        return jsonify({'message': 'Transaction parameters different from lsig conditions.', 'success': False})
    else:
        # check if user is trying to reuse the token
        if 'overlapping lease' in error_message:
            return jsonify({'message': 'Failed Attempt to Reuse Token', 'success': False}), 400
        
        return jsonify({'message': "An unexpected error occurred. ", 'success': False}), 500
    


'''
    After a transaction has been executed, erease the token from session data and from JSON file. 
'''
def erase_token_data(file_path):
    session.pop('decoded_lsig', None)
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        if 'text' in data:
            data['text'] = ""
        else:
            print("The 'text' key does not exist in the JSON file.")
        # clear token data in json file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    
    except json.JSONDecodeError:
        print("Error decoding JSON. The file may be corrupted or incorrectly formatted.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")



''' 
    Methods to run processes in parallel on port 5000 and port 3000.
'''
def run_app_ui():
    flask_app.run(port=5000)

def run_app_sms():
    app_sms.run(port=3000)


# start Flask apps
if __name__ == '__main__':
    if not flask_app.config["TESTING"]:
            # create processes for each Flask app
            process_ui = Process(target=run_app_ui)
            process_sms = Process(target=run_app_sms)

            # start each process
            process_ui.start()
            process_sms.start()

            try:
                # join processes to the main process
                process_ui.join()
                process_sms.join()
            except KeyboardInterrupt:
                print("   Keyboard interruption. Stopping processes...")
                process_ui.terminate()
                process_sms.terminate()