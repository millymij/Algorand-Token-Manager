import json
import pytest
import requests
import responses


# For some of the most important functions of server.py, testing whether the requests are made to the correct routes and
# checking the handling of the HTTP responses.

# NOTE: For the tests to be executed, server.py needs to be running.

# feed the test with application's URL
@pytest.fixture
def api_url():
    return "http://localhost:5000"


#======== Test success and exception cases of generate account ==========

def test_generate_account(api_url):
        response = requests.post(f"{api_url}/generate_account")
        assert response.status_code == 200
        # check correct writing in file
        data = response.json()
        assert 'new_account_address' in data


# intercept POST request and return a predefined error response
@responses.activate
def test_generate_account_exception(api_url):
    responses.add(
        responses.POST,
        f"{api_url}/generate_account",
        json={'error': 'Failed to generate account', 'success': False},
        status=500
    )
    response = requests.post(f"{api_url}/generate_account")
    assert response.status_code == 500
    assert response.json()['error'] == 'Failed to generate account'
    assert response.json()['success'] is False


# #======== Test success, error and exception cases of generate logic signature ==========


def test_generate_logic_signature_success(api_url):
    file_path = 'smart_contracts/my_teal.teal'
    with open(file_path, 'rb') as f:
        # set file for mocked upload
        files = {'file': (file_path, f, 'text/test')}
        response = requests.post(f"{api_url}/generate_logic_signature", files=files)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['message'] == 'Logic Signature generated successfully!'
    assert response_data['success'] is True



# intercept POST request and return a predefined error response for invalid teal code
@responses.activate
def test_generate_logic_signature_error(api_url):
    responses.add(
        responses.POST,
        f"{api_url}/generate_logic_signature",
        body=json.dumps({'message': 'Failed to generate Logic Signature due to invalid TEAL code.', 'success': False}),
        status=500
    )
    files = {'file': ('contract123.teal', 'lorem ipsum', 'text/test')}
    response = requests.post(f"{api_url}/generate_logic_signature", files)
    assert response.status_code == 500
    assert response.json()['message'] == 'Failed to generate Logic Signature due to invalid TEAL code.'
    assert response.json()['success'] is False



# intercept POST request and return a predefined error response for unexpected error
@responses.activate
def test_generate_logic_signature_exception(api_url):
    responses.add(
        responses.POST,
        f"{api_url}/generate_logic_signature",
        body=json.dumps({'message': 'Unexpected error', 'success': False}),
        status=500
    )
    file_path = 'smart_contracts/my_teal.teal'
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'text/test')}
        response = requests.post(f"{api_url}/generate_logic_signature", files=files)
    assert response.status_code == 500
    assert response.json()['message'] == 'Unexpected error'
    assert response.json()['success'] is False



#======== Test success, error and exception cases of create transaction ==========



# simulate transaction sent to the Algorand network
@responses.activate
def test_create_transaction_success(api_url):
    responses.add(
        responses.POST,
        f"{api_url}/create_transaction",
        body=json.dumps({'message': 'Transaction successfully created.', 'success': True}),
        status=200,
        content_type='application/json',
    )
    transaction_data = {
        'sender_address': 'TESTaddrsender',
        'receiver_address': 'TESTaddrreceiver',
        'amount': 10000
    }
    response = requests.post(f"{api_url}/create_transaction", json=transaction_data)
    assert response.status_code == 200
    assert response.json()['success'] is True


# creating a transaction missing field 'receiver'
def test_create_transaction_no_field(api_url):
    response = requests.post(f"{api_url}/create_transaction", json={
        'sender_address': 'TESTaddrsender',
        'amount': 1000
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'All fields must be provided.'
    assert response.json()['success'] is False


# creating a transaction without lsig
def test_create_transaction_no_lsig(api_url):
    response = requests.post(f"{api_url}/create_transaction", json={
        'sender_address': 'TESTaddrsender',
        'receiver_address': 'TESTaddrreceiver',
        'amount': 10000
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'Decoded LogicSig not found.'
    assert response.json()['success'] is False



# #======== Test success and exception cases of sms sending, mocking network interactions with Vonage API service. ==========


# check that the requests are made to the right URL
@responses.activate
def test_send_sms_success(api_url):
    # mocked response for Vonage API calls
    sms_service_url = f"{api_url}/send_sms"
    responses.add(
        responses.POST,
        sms_service_url,
        json={'message': 'Both messages were successfully sent.', 'success': True},
        status=200
    )
    response = requests.post(sms_service_url, json={
        'receiver_number': '11111',
        'text': 'xxx'
    })
    # check that request is going to the correct url.    
    # get the first call from mocked calls
    call = responses.calls[0]
    request = call.request
    # get the request url
    request_url = request.url
    assert request_url == sms_service_url
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['success'] is True
    assert response_data['message'] == 'Both messages were successfully sent.'


# mock api failure scenario
@responses.activate
def test_send_sms_exception(api_url):
    sms_service_url = f"{api_url}/send_sms"
    responses.add(
        responses.POST,
        sms_service_url,
        json={'message': 'Network Error', 'success': False},
        status=500
    )
    response = requests.post(sms_service_url, json={
        'receiver_number': '11111',
        'text': 'xxx'
    })
    assert response.status_code == 500
    response_data = response.json()
    assert response_data['success'] is False
    assert response_data['message'] == 'Network Error'