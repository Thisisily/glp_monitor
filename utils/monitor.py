import logging
import time

def get_total_assets(contract):
    """
    Fetch the total assets in the GLP index.

    Args:
        contract (Contract): The GLP contract instance.

    Returns:
        int: The total assets in the GLP index.
    """
    try:
        return contract.functions.totalAssets().call()
    except Exception as e:
        logging.error(f"Error fetching total assets: {e}")
        return 0

def get_glp_supply(contract):
    """
    Fetch the total supply of GLP.

    Args:
        contract (Contract): The GLP contract instance.

    Returns:
        int: The total supply of GLP.
    """
    try:
        return contract.functions.totalSupply().call()
    except Exception as e:
        logging.error(f"Error fetching GLP supply: {e}")
        return 0

def get_user_glp_balance(contract, user_address):
    """
    Fetch the GLP balance of a user.

    Args:
        contract (Contract): The GLP contract instance.
        user_address (str): The address of the user.

    Returns:
        int: The GLP balance of the user.
    """
    try:
        return contract.functions.balanceOf(user_address).call()
    except Exception as e:
        logging.error(f"Error fetching user GLP balance for {user_address}: {e}")
        return 0

def calculate_prices(total_assets, glp_supply):
    """
    Calculate the minting and redemption prices of GLP.

    Args:
        total_assets (int): The total worth of assets in the GLP index.
        glp_supply (int): The total supply of GLP.

    Returns:
        tuple: The minting price and redemption price of GLP.
    """
    if glp_supply == 0:
        return 0, 0
    mint_price = total_assets / glp_supply
    redemption_price = total_assets / glp_supply
    return mint_price, redemption_price

def monitor_glp(config, interval=60):
    """
    Monitor the user's GLP holdings, rewards, and fees.

    Args:
        config (dict): The configuration dictionary.
        interval (int, optional): The time interval (in seconds) to refresh the data. Defaults to 60.
    """
    from .web3_utils import setup_web3, load_contract
    import json

    eth_web3 = setup_web3(config['eth_provider_url'])
    avax_web3 = setup_web3(config['avax_provider_url'])

    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)

    eth_glp_contract = load_contract(eth_web3, config['eth_glp_contract_address'], glp_abi)
    avax_glp_contract = load_contract(avax_web3, config['avax_glp_contract_address'], glp_abi)

    while True:
        for user_address in config['user_addresses']:
            try:
                # Fetch data from Ethereum GLP contract
                eth_total_assets = get_total_assets(eth_glp_contract)
                eth_glp_supply = get_glp_supply(eth_glp_contract)
                eth_user_balance = get_user_glp_balance(eth_glp_contract, user_address)
                
                # Fetch data from Avalanche GLP contract
                avax_total_assets = get_total_assets(avax_glp_contract)
                avax_glp_supply = get_glp_supply(avax_glp_contract)
                avax_user_balance = get_user_glp_balance(avax_glp_contract, user_address)
                
                # Calculate prices for minting and redemption
                eth_mint_price, eth_redemption_price = calculate_prices(eth_total_assets, eth_glp_supply)
                avax_mint_price, avax_redemption_price = calculate_prices(avax_total_assets, avax_glp_supply)
                
                # Calculate user's rewards (for simplicity, assuming rewards are proportional to balance)
                eth_user_rewards = eth_user_balance * eth_mint_price
                avax_user_rewards = avax_user_balance * avax_mint_price
                
                # Log user's holdings, rewards, and fees
                logging.info(f"ETH GLP - User: {user_address}, Balance: {eth_user_balance}, Rewards: {eth_user_rewards}, Fees: {eth_user_rewards * 0.01}")
                logging.info(f"AVAX GLP - User: {user_address}, Balance: {avax_user_balance}, Rewards: {avax_user_rewards}, Fees: {avax_user_rewards * 0.01}")

            except Exception as e:
                logging.error(f"Error during monitoring for user {user_address}: {e}")
        
        # Wait for the specified interval before fetching the data again
        time.sleep(interval)
