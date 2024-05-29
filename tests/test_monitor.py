import unittest
from unittest.mock import MagicMock
from utils.monitor import get_total_assets, get_glp_supply, get_user_glp_balance, calculate_prices

class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.mock_contract = MagicMock()

    def test_get_total_assets(self):
        self.mock_contract.functions.totalAssets.return_value.call.return_value = 1000000
        total_assets = get_total_assets(self.mock_contract)
        self.assertEqual(total_assets, 1000000)

    def test_get_glp_supply(self):
        self.mock_contract.functions.totalSupply.return_value.call.return_value = 5000
        glp_supply = get_glp_supply(self.mock_contract)
        self.assertEqual(glp_supply, 5000)

    def test_get_user_glp_balance(self):
        self.mock_contract.functions.balanceOf.return_value.call.return_value = 100
        user_balance = get_user_glp_balance(self.mock_contract, '0xYourEthereumAddress')
        self.assertEqual(user_balance, 100)

    def test_calculate_prices(self):
        total_assets = 1000000
        glp_supply = 5000
        mint_price, redemption_price = calculate_prices(total_assets, glp_supply)
        self.assertEqual(mint_price, 200)
        self.assertEqual(redemption_price, 200)

if __name__ == '__main__':
    unittest.main()
