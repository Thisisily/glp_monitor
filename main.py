import logging
import json
from utils.config_loader import load_config
from utils.monitor import monitor_glp
from web3 import Web3

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_address(address):
    """
    Validate Ethereum address.

    Args:
        address (str): The Ethereum address to validate.

    Returns:
        bool: True if the address is valid, False otherwise.
    """
    return Web3.isAddress(address)

def main():
    # Load configuration
    config = load_config()

    # Ask the user for their wallet address if not provided in config
    if not config['user_addresses']:
        user_address = input("Please enter your wallet address: ")
        if not validate_address(user_address):
            raise ValueError("Invalid wallet address provided.")
        config['user_addresses'].append(user_address)

    # Load the ABI
    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)
        config['glp_abi'] = glp_abi

    # Start monitoring the user's GLP holdings, rewards, and fees
    monitor_glp(config)

if __name__ == "__main__":
    main()
