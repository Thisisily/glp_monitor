import logging
import json
from utils.config_loader import load_config
from utils.monitor import monitor_glp

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Load configuration
    config = load_config()

    # Ask the user for their wallet address if not provided in config
    if not config['user_addresses']:
        user_address = input("Please enter your wallet address: ")
        config['user_addresses'].append(user_address)

    # Load the ABI
    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)
        config['glp_abi'] = glp_abi

    # Start monitoring the user's GLP holdings, rewards, and fees
    monitor_glp(config)

if __name__ == "__main__":
    main()
