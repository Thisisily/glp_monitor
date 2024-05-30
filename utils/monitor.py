import logging
import time
from .constants import DECIMALS
import logging
import requests
from datetime import datetime

def get_historical_mint_prices(web3, contract, start_block=0, end_block=None, step=2048):
    """
    Fetch historical mint prices in paginated batches.

    Args:
        web3 (Web3): The Web3 instance.
        contract (Contract): The GLP contract instance.
        start_block (int): The block number to start fetching logs from.
        end_block (int): The block number to end fetching logs at.
        step (int): The number of blocks to fetch in each batch.

    Returns:
        list: A list of historical mint prices.
    """
    historical_prices = []

    event_signature = web3.keccak(text="Mint(address,uint256)").hex()
    if end_block is None:
        end_block = web3.eth.get_block('latest')['number']

    current_block = start_block

    while current_block <= end_block:
        to_block = min(current_block + step, end_block)
        try:
            logs = web3.eth.get_logs({
                "fromBlock": current_block,
                "toBlock": to_block,
                "address": contract.address,
                "topics": [event_signature]
            })

            for log in logs:
                price = int(log['data'], 16) / (10 ** 18)  # Adjust based on actual token decimals
                historical_prices.append(price)

        except ValueError as e:
            logging.error(f"Error fetching logs from blocks {current_block} to {to_block}: {e}")
            break  # Exit if there's an error

        current_block = to_block + 1

    return historical_prices


    return historical_prices

def calculate_prices(web3, contract):
    """
    Calculate the minting and redemption prices of GLP.

    Args:
        web3 (Web3): The Web3 instance.
        contract (Contract): The GLP contract instance.

    Returns:
        tuple: The average minting price and current redemption price of GLP.
    """
    historical_prices = get_historical_mint_prices(web3, contract)
    average_mint_price = sum(historical_prices) / len(historical_prices) if historical_prices else 1
    current_redemption_price = 1  # Replace with actual logic to fetch current redemption price

    return average_mint_price, current_redemption_price

def get_historical_mint_prices_via_api(contract_address, api_key, network='arbitrum'):
    """
    Fetch historical mint prices using the blockchain explorer API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The API key for the blockchain explorer.
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        list: A list of historical mint prices.
    """
    historical_prices = []
    base_url = {
        'arbitrum': 'https://api.arbiscan.io/api',
        'avalanche': 'https://api.snowtrace.io/api'
    }.get(network)

    if not base_url:
        raise ValueError(f"Unsupported network: {network}")

    params = {
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': '0',
        'toBlock': 'latest',
        'address': contract_address,
        'topic0': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',  # Transfer event topic
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == '1':
        for log in data['result']:
            price = int(log['data'], 16) / (10 ** DECIMALS)  # Adjust based on actual token decimals
            historical_prices.append(price)
    else:
        logging.error(f"Error fetching logs: {data['message']}")

    return historical_prices

def calculate_prices_via_api(contract_address, api_key, network='arbitrum'):
    """
    Calculate the minting and redemption prices of GLP using API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The API key for the blockchain explorer.
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        tuple: The average minting price and current redemption price of GLP.
    """
    historical_prices = get_historical_mint_prices_via_api(contract_address, api_key, network)
    average_mint_price = sum(historical_prices) / len(historical_prices) if historical_prices else 1

    # Placeholder logic for current redemption price
    current_redemption_price = get_current_redemption_price_via_api(contract_address, api_key, network)

    return average_mint_price, current_redemption_price

def get_current_redemption_price_via_api(contract_address, api_key, network='arbitrum'):
    """
    Fetch the current redemption price using the blockchain explorer API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The API key for the blockchain explorer.
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        float: The current redemption price of GLP.
    """
    # Implement logic to fetch current redemption price
    # Placeholder: fetch latest price data or use existing method to calculate
    current_redemption_price = 1  # Placeholder value
    return current_redemption_price

def get_total_supply(contract):
    """
    Fetch the total supply of GLP.

    Args:
        contract (Contract): The GLP contract instance.

    Returns:
        float: The total supply of GLP.
    """
    try:
        return contract.functions.totalSupply().call() / (10 ** DECIMALS)
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
        float: The GLP balance of the user.
    """
    try:
        return contract.functions.balanceOf(user_address).call() / (10 ** DECIMALS)
    except Exception as e:
        logging.error(f"Error fetching user GLP balance for {user_address}: {e}")
        return 0

def get_glp_transactions(contract_address, user_address, api_key, network='arbitrum'):
    """
    Fetch all GLP-related transactions for a given user.

    Args:
        contract_address (str): The contract address.
        user_address (str): The user's address.
        api_key (str): The API key for the blockchain explorer.
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        list: A list of transactions involving the user.
    """
    transactions = []
    base_url = {
        'arbitrum': 'https://api.arbiscan.io/api',
        'avalanche': 'https://api.snowtrace.io/api'
    }.get(network)

    if not base_url:
        raise ValueError(f"Unsupported network: {network}")

    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': user_address,
        'contractaddress': contract_address,
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == '1':
        for tx in data['result']:
            tx['human_readable_date'] = datetime.utcfromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
            tx['methodId'] = tx.get('methodId', 'N/A')  # Provide a default value if methodId is missing
            transactions.append(tx)
    else:
        logging.error(f"Error fetching transactions: {data['message']}")

    return transactions

def monitor_glp(config, interval=60):
    """
    Monitor the user's GLP holdings, rewards, and fees.

    Args:
        config (dict): The configuration dictionary.
        interval (int, optional): The time interval (in seconds) to refresh the data. Defaults to 60.
    """
    from .web3_utils import setup_web3, load_contract
    import json

    arb_web3 = setup_web3(config['arb_provider_url'])
    avax_web3 = setup_web3(config['avax_provider_url'])

    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)

    arb_glp_contract = load_contract(arb_web3, config['arb_glp_contract_address'], glp_abi)
    avax_glp_contract = load_contract(avax_web3, config['avax_glp_contract_address'], glp_abi)

    while True:
        for user_address in config['user_addresses']:
            try:
                # Fetch data from Arbitrum GLP contract
                arb_glp_supply = get_total_supply(arb_glp_contract)
                arb_user_balance = get_user_glp_balance(arb_glp_contract, user_address)
                
                # Fetch data from Avalanche GLP contract
                avax_glp_supply = get_total_supply(avax_glp_contract)
                avax_user_balance = get_user_glp_balance(avax_glp_contract, user_address)
                
                # Calculate prices for minting and redemption
                arb_mint_price, arb_redemption_price = calculate_prices(arb_glp_supply)
                avax_mint_price, avax_redemption_price = calculate_prices(avax_glp_supply)
                
                # Calculate user's rewards (for simplicity, assuming rewards are proportional to balance)
                arb_user_rewards = arb_user_balance * arb_mint_price
                avax_user_rewards = avax_user_balance * avax_mint_price
                
                # Log user's holdings, rewards, and fees
                logging.info(f"ARB GLP - User: {user_address}, Balance: {arb_user_balance}, Rewards: {arb_user_rewards}, Fees: {arb_user_rewards * 0.01}")
                logging.info(f"AVAX GLP - User: {user_address}, Balance: {avax_user_balance}, Rewards: {avax_user_rewards}, Fees: {avax_user_rewards * 0.01}")

            except Exception as e:
                logging.error(f"Error during monitoring for user {user_address}: {e}")
        
        # Wait for the specified interval before fetching the data again
        time.sleep(interval)
