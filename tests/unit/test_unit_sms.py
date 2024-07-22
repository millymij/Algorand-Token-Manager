import unittest
from unittest.mock import patch
import sys
import os


# adjust path at runtime since src and test are in separate folders 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'src')))
import sms_utils


class testUnitSms(unittest.TestCase):
    # check how the method interprets (mocked) api calls.
    # patching dependencies
    @patch('sms_utils.client.sms.send_message')
    @patch('sms_utils.logging')
    def test_send_sms_success(self, mock_logging, mock_send_message):
        # assume mock status response :0 = success
        mock_response = { "messages": [{"status": "0"}]}
        mock_send_message.return_value = mock_response
        result = sms_utils.send_sms_text("123456", "111111", "Lorem ipsum")
        self.assertTrue(result)
        # check method was actually called and logging the message correctly.
        mock_logging.info.assert_called_once_with('SMS sent successfully!')


    # error handling mocked failure response from api
    @patch('sms_utils.client.sms.send_message')
    @patch('sms_utils.logging')
    def test_send_sms_failure(self, mock_logging, mock_send_message):
        # assume mock status response :1 = failure
        mock_response = {"messages": [{"status": "1", "error-text": "Network Error"}]}
        mock_send_message.return_value = mock_response
        result = sms_utils.send_sms_text('123456', '111111', 'Lorem ipsum')
        self.assertFalse(result)
        mock_logging.info('An error occurred while sending SMS')


# NOTE: receive_sms() tested in integration testing.


if __name__ == '__main__':
    unittest.main()
