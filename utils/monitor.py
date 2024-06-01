import logging
import time
from .constants import ARBITRUM_TOKEN_ADDRESS_MAP, AVALANCHE_TOKEN_ADDRESS_MAP, DECIMALS
import logging
import requests
from datetime import datetime

def get_token_prices():
    """
    Fetch the current prices of tokens using Chainlink or an external API like CoinGecko.
    
    Returns:
        dict: A dictionary of token prices with token symbols as keys and prices as values.
    """
    token_ids = {
        "USDCe": "usd-coin",
        "MIM": "magic-internet-money",
        "USDT": "tether",
        "UNI": "uniswap",
        "LINK": "chainlink",
        "DAI": "dai",
        "USDC": "usd-coin",
        "ETH": "ethereum",
        "BTC": "bitcoin",
        "FRAX": "frax"
    }

    coingecko_api_url = "https://api.coingecko.com/api/v3/simple/price"
    response = requests.get(coingecko_api_url, params={"ids": ",".join(token_ids.values()), "vs_currencies": "usd"})
    data = response.json()

    token_prices = {symbol: data[token_id]["usd"] for symbol, token_id in token_ids.items()}
    
    # Adjust stablecoin prices
    stablecoins = ["USDCe", "USDT", "DAI", "USDC", "MIM", "FRAX"]
    for stablecoin in stablecoins:
        token_prices[stablecoin] = (token_prices[stablecoin] + 1) / 2

    return token_prices

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
                price = int(log['data'], 16) / (10 ** DECIMALS)  # Adjust based on actual token decimals
                historical_prices.append(price)

        except ValueError as e:
            logging.error(f"Error fetching logs from blocks {current_block} to {to_block}: {e}")
            break  # Exit if there's an error

        current_block = to_block + 1

    return historical_prices

def calculate_average_mint_price(transactions):
    """
    Calculate the average mint price of GLP from the user's transactions.

    Args:
        transactions (list): A list of GLP transactions.

    Returns:
        float: The weighted average mint price.
    """
    total_glp = 0
    total_cost = 0

    for tx in transactions:
        if tx['methodId'] == 'mint':
            glp_amount = float(tx['value']) / (10 ** DECIMALS)  # Adjust for GLP decimals
            glp_price = float(tx['value']) / glp_amount  # Assuming 'value' is in USD (this may need adjustment)
            total_glp += glp_amount
            total_cost += glp_price * glp_amount

    average_mint_price = total_cost / total_glp if total_glp else 0
    return average_mint_price

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

def get_historical_mint_prices_via_api(contract_address, api_key, network='arbitrum', user_address=None):
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
            if user_address and user_address.lower() not in (log['topics'][1], log['topics'][2]):
                continue
            amount = int(log['data'], 16) / (10 ** DECIMALS)
            price = int(log['data'], 16) / (10 ** DECIMALS)
            historical_prices.append({
                'blockNumber': int(log['blockNumber'], 16),
                'price': price,
                'amount': amount,
                'timeStamp': int(log['timeStamp'], 16)
            })
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


def get_token_composition_scraping(network='arbitrum'):
    """
    Fetch the latest token composition from the GMX stats dashboard using the API.

    Args:
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        dict: A dictionary of token composition with token symbols and their weights.
    """
    api_urls = {
        'arbitrum': "https://subgraph.satsuma-prod.com/3b2ced13c8d9/gmx/gmx-arbitrum-stats/api",
        'avalanche': "https://subgraph.satsuma-prod.com/3b2ced13c8d9/gmx/gmx-avalanche-stats/api"
    }

    api_url = api_urls.get(network)
    if not api_url:
        raise ValueError(f"Unsupported network: {network}")

    query = """
    {
      tokenStats(first: 1000, skip: 0, orderBy: timestamp, orderDirection: desc, where: {period: daily}) {
        poolAmountUsd
        timestamp
        token
      }
    }
    """
    
    response = requests.post(api_url, json={'query': query})
    
    if response.status_code == 200:
        data = response.json().get('data', {}).get('tokenStats', [])
        token_composition = {}
        for item in data:
            token = item['token']
            pool_amount_usd = float(item['poolAmountUsd'])
            if token in token_composition:
                token_composition[token] += pool_amount_usd
            else:
                token_composition[token] = pool_amount_usd
        
        # Normalize the composition weights
        total_amount = sum(token_composition.values())
        for token in token_composition:
            token_composition[token] /= total_amount

        return token_composition
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return {}

def get_open_positions(network='arbitrum'):
    """
    Fetch the current open long and short positions from the GMX dashboard or API.
    
    Args:
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        dict: A dictionary of net open positions with token symbols as keys and net positions as values.
    """
    # Example fetching from GMX API or dashboard
    # This is a placeholder implementation
    open_positions = {
        "ETH": 1000,  # Positive value indicates net long position
        "BTC": -500,  # Negative value indicates net short position
        # Add more tokens as necessary
    }
    return open_positions

def adjust_token_weights(token_composition, open_positions):
    """
    Adjust token weights based on the net open positions.

    Args:
        token_composition (dict): The original token composition from the GLP pool.
        open_positions (dict): The net open positions from the GMX platform.

    Returns:
        dict: A dictionary of adjusted token weights.
    """
    adjusted_weights = token_composition.copy()
    for token, weight in token_composition.items():
        net_position = open_positions.get(token, 0)
        if net_position > 0:
            adjusted_weights[token] = weight * (1 + net_position / 10000)  # Example adjustment
        elif net_position < 0:
            adjusted_weights[token] = weight * (1 - abs(net_position) / 10000)
    return adjusted_weights

def calculate_wallet_exposure(glp_balance, network='arbitrum'):
    """
    Calculate the user's exposure to underlying tokens based on their GLP balance.

    Args:
        glp_balance (float): The user's GLP balance.
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        dict: A dictionary of token exposure with token symbols and their USD values.
    """
    # Fetch the token composition for the specified network
    token_composition = get_token_composition_scraping(network)
    
    # Fetch the current prices of tokens
    token_prices = get_token_prices()

    # Fetch the current open positions
    open_positions = get_open_positions(network)

    # Adjust the token weights based on net open positions
    adjusted_token_composition = adjust_token_weights(token_composition, open_positions)

    # Select the appropriate token address map
    token_address_map = ARBITRUM_TOKEN_ADDRESS_MAP if network == 'arbitrum' else AVALANCHE_TOKEN_ADDRESS_MAP

    # Calculate the exposure for each token
    token_exposure = {}
    for token, weight in adjusted_token_composition.items():
        token_price = token_prices.get(token, 1)  # Default to 1 if token price is not found
        token_name = token_address_map.get(token, token)
        token_exposure[token_name] = glp_balance * weight * token_price

    return token_exposure


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


def fetch_glp_data(network='arbitrum'):
    """
    Fetch GLP AUM and supply from the subgraph API.

    Args:
        network (str): The network to query ('arbitrum' or 'avalanche').

    Returns:
        dict: A dictionary with AUM, supply, and price.
    """
    api_urls = {
        'arbitrum': 'https://subgraph.satsuma-prod.com/3b2ced13c8d9/gmx/gmx-arbitrum-stats/api',
        'avalanche': 'https://subgraph.satsuma-prod.com/3b2ced13c8d9/gmx/gmx-avalanche-stats/api'
    }

    query = """
    {
      glpStats(orderBy: id, orderDirection: desc, first: 1) {
        aumInUsdg
        glpSupply
      }
    }
    """
    
    response = requests.post(api_urls[network], json={'query': query})
    data = response.json().get('data', {}).get('glpStats', [])[0]

    aum_in_usdg = float(data['aumInUsdg'])
    glp_supply = float(data['glpSupply'])
    price = aum_in_usdg / glp_supply if glp_supply else 0

    return {
        'aum_in_usdg': aum_in_usdg,
        'glp_supply': glp_supply,
        'price': price
    }


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
