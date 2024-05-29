from web3 import Web3

def setup_web3(provider_url):
    """
    Set up a Web3 connection to a blockchain node.

    Args:
        provider_url (str): The URL of the blockchain node.

    Returns:
        Web3: A Web3 instance connected to the specified node.
    """
    return Web3(Web3.HTTPProvider(provider_url))

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
