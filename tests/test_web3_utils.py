import unittest
from web3 import Web3
from utils.web3_utils import setup_web3, load_contract

class TestWeb3Utils(unittest.TestCase):
    def test_setup_web3(self):
        web3 = setup_web3('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID')
        self.assertIsInstance(web3, Web3)

    def test_load_contract(self):
        web3 = setup_web3('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID')
        abi = [...]  # Use a simplified ABI for testing
        contract_address = '0x0000000000000000000000000000000000000000'
        contract = load_contract(web3, contract_address, abi)
        self.assertIsNotNone(contract)

if __name__ == '__main__':
    unittest.main()
