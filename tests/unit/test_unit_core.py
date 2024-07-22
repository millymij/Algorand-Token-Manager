import unittest
import base64
import json
from unittest.mock import patch, MagicMock
import sys
import os


# adjust path at runtime since src and test are in separate folders 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'src')))
import core


class test_unit_core(unittest.TestCase):

#============== Test generate account, success and failure test cases ===========
   
    # Mock external dependencies for account and menmonic
    @patch('core.account.generate_account')
    @patch('core.mnemonic.from_private_key')
    def test_generate_account_success(self, mock_from_private_key, mock_generate_account):
        mock_private_key = "mock_private_key"
        mock_address = "mock_address"
        mock_mnemonic = "mock_mnemonic"
        
        # create mock return values of generate_account() and of from_private_key()
        mock_generate_account.return_value = (mock_private_key, mock_address)
        mock_from_private_key.return_value = mock_mnemonic
        
        account_info = core.generate_account()
        self.assertIsNotNone(account_info)
        self.assertEqual(account_info['address'], mock_address)
        self.assertEqual(account_info['private_key'], mock_private_key)
        self.assertEqual(account_info['mnemonic'], mock_mnemonic)


    # Mock an exception in account generation
    @patch('core.account.generate_account')
    def test_generate_account_failure(self, mock_generate_account):
        # mock will raise an exception
        mock_generate_account.side_effect = Exception("Mocked exception")
        result = core.generate_account()
        # check 'None' result due to exception
        self.assertIsNone(result)


#============== Test fetch info account ===========

    @patch('core.algod_client')
    def test_fetch_info(self, mock_client):
        # set mock account data
        account_address = 'test_address'
        expected_account_info = {'amount': 1000000}
        mock_client.account_info.return_value = expected_account_info
        account_info = core.fetch_info(account_address)
        self.assertEqual(account_info, expected_account_info)


#============== Test encoding of lsig to sms and back ===========

    
    def test_lsig_to_sms_text(self):
        # simulate dictify method from LogicSigAccount obj
        mock_lsig = MagicMock()
        mock_lsig.dictify.return_value = {
            'lsig': {
                'l': b'sample logic',
                'sig': b'sample signature',
            },
            'sigkey': b'sample sigkey'
        }
        # use mocked object in the function
        result = core.lsig_to_sms_text(mock_lsig)
        # mock result
        expected_dict = {
            'lsig': {
                'l': base64.urlsafe_b64encode(b'sample logic').decode(),
                'sig': base64.urlsafe_b64encode(b'sample signature').decode(),
            },
            'sigkey': base64.urlsafe_b64encode(b'sample sigkey').decode()
        }
        expected_json_str = json.dumps(expected_dict)
        expected_encoded_str = base64.urlsafe_b64encode(expected_json_str.encode()).decode()
        self.assertEqual(result, expected_encoded_str)



    @patch('core.LogicSigAccount.undictify')
    def test_sms_text_to_lsig(self, mock_undictify):
        sample_lsig_dict = {
            'lsig': {
                'l': base64.urlsafe_b64encode(b'sample logic').decode(),
                'sig': base64.urlsafe_b64encode(b'sample signature').decode(),
            },
            'sigkey': base64.urlsafe_b64encode(b'sample sigkey').decode()
        }

        # convert dictionary to JSON string, then encode to bytes
        encoded_json_str = base64.urlsafe_b64encode(json.dumps(sample_lsig_dict).encode()).decode()

        # setup the mock LogicSigAccount object, This will be returned by undictify
        mock_lsig_account = MagicMock(spec=core.LogicSigAccount)
        mock_undictify.return_value = mock_lsig_account
        result = core.sms_text_to_lsig(encoded_json_str)

        # assert that the result is the mock a LogicSigAccount object.
        # since we're emulating the object with placeholders, the correct result represeting a LogicSigAccount object will have this format:
        # <MagicMock name='undictify()' spec='LogicSigAccount' id='44123...'>
        self.assertEqual(result, mock_lsig_account)



if __name__ == '__main__':
    unittest.main()

