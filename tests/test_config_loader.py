import unittest
from utils.config_loader import load_config

class TestConfigLoader(unittest.TestCase):
    def test_load_config(self):
        config = load_config('config.yaml')
        self.assertIn('eth_provider_url', config)
        self.assertIn('avax_provider_url', config)
        self.assertIn('eth_glp_contract_address', config)
        self.assertIn('avax_glp_contract_address', config)
        self.assertIn('user_addresses', config)

if __name__ == '__main__':
    unittest.main()
