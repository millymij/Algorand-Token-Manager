from algosdk import account, mnemonic
from algosdk.transaction import LogicSigAccount, LogicSigTransaction, PaymentTxn, wait_for_confirmation
from algosdk.v2client import algod
import base64
import json
import base64
import hashlib
import ast
import sms_utils



# Instantiate client: connect to the local Algorand node in docker's container.
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)



# If users dont have an Algorand account, they can create one.

def generate_account():
    try: 
        new_private_key, new_address = account.generate_account()
        new_mnemonic = mnemonic.from_private_key(new_private_key)

        account_info = {
            'address': new_address,
            'private_key': new_private_key,
            'mnemonic': new_mnemonic
        }

        print(f"\nNewly generated account address: {new_address}")
        print(f"\nNewly generated account private key: {new_private_key}")
        print(f"\nNewly generated account mnemonic: {new_mnemonic}")

        return account_info
    
    except Exception as e:
        print(f"An error occurred while generating the account: {e}")

        return None


# If user already has an Algorand account,
# fetch info about that existing account

def fetch_info(account_address):
    try:
        account_info = algod_client.account_info(account_address)
        balance = account_info.get('amount') / 1e6

        print(f"\nAccount balance for {account_address}: {balance} Algos")
        print(f"\nInfo: {account_info}")

        return account_info
    
    except Exception as e:
        print(f"An error occurred while generating the account: {e}")

        return None


# Construct and execute a simple transaction. This function has been developed for testing purposes.

def construct_simple_transaction(sender, receiver, amount, note, private_key, params=None, mnemonics=None):

    # Set transaction arguments
    if params is None:
        params = algod_client.suggested_params()

    # Ensure that either private_key or mnemonics is provided
    if not private_key and not mnemonics:
        raise ValueError("Either private_key or mnemonics must be provided.")
    
    if private_key:
        # Use the private_key for the transaction
        pass
    else:
        # Convert mnemonics to private_key
        private_key = mnemonic.to_private_key(mnemonics)

    # create unsigned transaction
    unsigned_txn = PaymentTxn(sender, params, receiver, amount, None, note)
    # sign transaction with private key
    signed_txn = unsigned_txn.sign(private_key)

    # fetch accounts information before transaction
    print(f"\n\n#### Before the transaction #### \n")
    fetch_info(sender)
    fetch_info(receiver)

    # send transaction to the network
    txid = algod_client.send_transaction(signed_txn)
    print("Successfully sent transaction with ID: {}".format(txid))

    # wait confirmation
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
        print("\nTransaction confirmed in round {}".format(confirmed_txn.get('confirmed-round'))) 

        # fetch accounts information after transaction
        print(f"\n\n#### After the transaction #### \n")
        fetch_info(sender)
        fetch_info(receiver)
    except Exception as e:
        print(e)


# Create delegated logic signature from TEAL contract
    
def create_lsig(teal_source):

    # Compile TEAL program: returns a dictionary with 
    # the 'hash' = address of the program and 'result' = base64 representation of the TEAL contract
    compiled_response = algod_client.compile(teal_source)
    print(f"\n\nCompiled response: ", compiled_response)

    # Decode result of compiled response from base64 to bytes
    program_bytes = base64.b64decode(compiled_response['result'])
    print(f"\n\nProgram in Bytes: {program_bytes}")

    # Create logic sig account from the program bytes to prepare the account for delegation
    lsig = LogicSigAccount(program_bytes)

    return lsig


# Sign LogiSignature object with user's private key

def sign_lsig(lsig, private_key):
    lsig.sign(private_key)
    print("\n\nLogic Signature Signed Correctly!")
    return lsig


# Encode lsig object to SMS text string

def lsig_to_sms_text(lsig):

    # lsig fields as ordered dictionary
    dict = lsig.dictify()
    print("\n\nDictified Lsig ")
    print(dict)

    # Encode ditionary fields to b64 urlsafe, then decode to convert this to a UTF-8 string.
    dict["lsig"]['l'] = base64.urlsafe_b64encode(dict["lsig"]['l']).decode()
    dict["lsig"]['sig'] = base64.urlsafe_b64encode(dict["lsig"]['sig']).decode()
    dict["sigkey"] = base64.urlsafe_b64encode(dict["sigkey"]).decode()
    print("\n\nDecoded bytes Dict: {}".format(dict))

    # Create JSON string
    dictStr= json.dumps(dict)
    print("\n\nDictStr JSON: {}".format(dictStr))

    # Make JSON string a UTF-8 encoded bytes object
    encoded = dictStr.encode()
    print("\n\nDictBytes: {}".format(encoded))

    # Encode bytes object from UTF-8 to base64, to get a string
    b64 = base64.urlsafe_b64encode(encoded)
    print("\n\nB64 Encoded DictStr: {}".format(b64))

    # Base64-encoded bytes object to string
    strEncoded = b64.decode()
    print("\n\nFinal DATA ENCODED in text string: {}".format(strEncoded))
    return strEncoded


# Decode SMS text string to lsig object

def sms_text_to_lsig(strEncoded):
    # Decode from Base64 URL Safe String to bytes object
    decoded_bytes = base64.urlsafe_b64decode(strEncoded).decode()
    print("\n\n Decoded Lsig: {}".format(decoded_bytes))    

    # String to dictionary
    dic = ast.literal_eval(decoded_bytes)
    print("\n\n To Dictionary: {}".format(dic))

    # Decode encoded dictionary values
    dic["lsig"]["l"] = base64.urlsafe_b64decode(dic["lsig"]["l"])
    dic["lsig"]["sig"] = base64.urlsafe_b64decode(dic["lsig"]["sig"])
    dic["sigkey"] = base64.urlsafe_b64decode(dic["sigkey"])
    print("\n\nlsig After decoding: {}".format(dic))

    # Final Lsig
    finalLsig = LogicSigAccount.undictify(dic)
    #print("\n\n Finallsig OBJECT after decoding: {}".format(finalLsig))
    print(f"\n\nFINAL DATA DECODED in LogicSigAccount object: {finalLsig}")
    return finalLsig


# Create a transaction with lsig attached

def construct_lsig_transaction(senders_address, receivers_address, amount, logicSig, token):
    try:
        status = algod_client.status()
        print("Node status:", status)
    except Exception as e:
        print("An error occurred checking node status:", e)

    if status and 'lastRound' in status and 'catchupTime' in status:
        if status['catchupTime'] == 0:
            print("Node is fully synced.")
        else:
            print("Node is catching up, not fully synced.")
    else:
        print("Unable to determine node sync status.")
 

    # get suggested parameters
    params = algod_client.suggested_params()
    
    # set transaction rounds in which transactions with the same lease will be rejected
    current_round = algod_client.status().get('last-round')
    first_valid_round = current_round + 1
    last_valid_round = first_valid_round + 1000 
    lease = generate_lease(token)

    # create transaction
    txn = PaymentTxn(senders_address, params, receivers_address, amount, lease=lease)

    # sign transaction with LogicSig
    signed_txn = LogicSigTransaction(txn, logicSig)

    # send transaction to the network
    txid = algod_client.send_transaction(signed_txn)
    print("Successfully sent transaction with txID: {}".format(txid))

    # wait confirmation
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
        print("\nTransaction confirmed in round {}".format(confirmed_txn.get('confirmed-round')))
           # fetch accounts information after transaction
        print(f"\n\n#### After the transaction #### \n")
        fetch_info(senders_address)
        fetch_info(receivers_address) 
    except Exception as e:
        print(e)


# Send lsig via SMS to mobile phone

def send_SMS(sender_number, receiver_number, text):
    success = sms_utils.send_sms_text(sender_number, receiver_number, text)
    if success:
        print("The message was successfully sent.")
        return success
    else:
        print("Failed to send the message.")


# Retrieve SMS data from the file where the info was saved

def get_data_from_file():
    with open('tmp/received_sms_data.json', 'r') as f:
        data = json.load(f)
        message_text = data.get('text', '')
        sender_number = data.get('from', '')
        receiver_number = data.get('to', '')
        timestamp = data.get('timestamp', '')

    return message_text, sender_number, receiver_number, timestamp


# Serialize: convert from LogicSig object to dictionary

def serialize_logic_sig(lsig):
    lsig_dict = lsig.dictify()
    lsig_dict["lsig"]['l'] = base64.urlsafe_b64encode(lsig_dict["lsig"]['l']).decode()
    lsig_dict["lsig"]['sig'] = base64.urlsafe_b64encode(lsig_dict["lsig"]['sig']).decode() if lsig_dict["lsig"]['sig'] else ''
    lsig_dict["sigkey"] = base64.urlsafe_b64encode(lsig_dict["sigkey"]).decode() if lsig_dict["sigkey"] else ''
    
    dict_str = json.dumps(lsig_dict)
    encoded = dict_str.encode()
    b64_encoded = base64.urlsafe_b64encode(encoded).decode()

    return b64_encoded


# Deserialize: convert from dictionary to LogicSig object

def deserialize_logic_sig(encoded_str):
    decoded_bytes = base64.urlsafe_b64decode(encoded_str.encode())
    decoded_str = decoded_bytes.decode()
    lsig_dict = json.loads(decoded_str)

    # decoding the base64 fields back to their original binary format
    lsig_dict["lsig"]['l'] = base64.urlsafe_b64decode(lsig_dict["lsig"]['l'])
    lsig_dict["lsig"]['sig'] = base64.urlsafe_b64decode(lsig_dict["lsig"]['sig']) if lsig_dict["lsig"]['sig'] else None
    lsig_dict["sigkey"] = base64.urlsafe_b64decode(lsig_dict["sigkey"]) if lsig_dict["sigkey"] else None

    return LogicSigAccount.undictify(lsig_dict)


# Read .teal contract to extract the value under the condition 'Amount'

def extract_txn_amount_from_teal(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if 'txn Amount' in line:
                amount_line = next(file, '').strip()
                parts = amount_line.split()
                if len(parts) > 1 and parts[0] == 'int':
                    try:
                        return int(parts[1])
                    except ValueError:
                        continue
    return None


# Check matching between account's private key and account's address

def check_private_key_against_address(account_address, private_key):
    expected_address = account.address_from_private_key(private_key)
    if account_address == expected_address:
        return True
    else:
        return False


# Generate a lease by hashing the input, the encoded token.

def generate_lease(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    # lease will be 32-byte hash value
    lease = hash_object.digest()  
    return lease