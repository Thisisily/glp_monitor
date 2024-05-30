from web3 import Web3
from web3.middleware import geth_poa_middleware

def setup_web3(provider_url):
    """
    Setup Web3 instance with the given provider URL.

    Args:
        provider_url (str): The URL of the provider.

    Returns:
        Web3: An instance of Web3.
    """
    web3 = Web3(Web3.HTTPProvider(provider_url))
    
    # Add middleware for Proof of Authority networks
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return web3

def load_contract(web3_instance, contract_address, abi):
    """
    Load a smart contract instance.

    Args:
        web3_instance (Web3): A Web3 instance connected to the blockchain.
        contract_address (str): The address of the contract.
        abi (list): The ABI of the contract.

    Returns:
        Contract: A Web3 contract instance.
    """
    return web3_instance.eth.contract(address=contract_address, abi=abi)
