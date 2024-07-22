
import unittest
import pytest
from unittest.mock import patch
from server import app_sms


@pytest.fixture
def sms_client():
    with app_sms.test_client() as sms_client:
        yield sms_client

# NOTE: send_sms() tested in unit testing.

#============ Test request handling in SMS receiving. Testing integration with Flask app, while mocking writing in file. ==========

def test_receive_sms_with_json(sms_client):
    sms_data = {'text': 'Hi!', 'from': '7711111222'}
    # mock opening of the file, such that we're not actually writing in the file
    with patch("builtins.open", new_callable=unittest.mock.mock_open) as mock_file:
        # write in a mock file, and specify what the mocked file return value should be
        file = mock_file.return_value.__enter__.return_value

        # mock writing in the file
        with patch("json.dump") as mock_json_dump:
            response = sms_client.post('/webhooks/inbound', json=sms_data)
            # check the call to open file
            mock_file.assert_called_once_with('tmp/received_sms_data.json', 'w')
            # check the call to json dump with the correct arguments to the correct file            
            mock_json_dump.assert_called_once_with(sms_data, file)
            assert response.status_code == 200
            assert response.json['status'] == 'success'