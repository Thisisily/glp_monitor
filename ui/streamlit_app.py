import json
import streamlit as st
from utils.config_loader import load_config
from utils.web3_utils import setup_web3, load_contract
from utils.monitor import get_total_assets, get_glp_supply, get_user_glp_balance, calculate_prices

def main():
    st.title("GLP Holdings Monitor")

    # Load configuration
    config = load_config()

    # Load the ABI
    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)

    # Setup Web3 connections
    eth_web3 = setup_web3(config['eth_provider_url'])
    avax_web3 = setup_web3(config['avax_provider_url'])

    eth_glp_contract = load_contract(eth_web3, config['eth_glp_contract_address'], glp_abi)
    avax_glp_contract = load_contract(avax_web3, config['avax_glp_contract_address'], glp_abi)

    # Ask the user for their wallet address
    user_address = st.text_input("Enter your wallet address:")

    if user_address:
        # Display GLP information
        eth_total_assets = get_total_assets(eth_glp_contract)
        eth_glp_supply = get_glp_supply(eth_glp_contract)
        eth_user_balance = get_user_glp_balance(eth_glp_contract, user_address)
        eth_mint_price, eth_redemption_price = calculate_prices(eth_total_assets, eth_glp_supply)

        avax_total_assets = get_total_assets(avax_glp_contract)
        avax_glp_supply = get_glp_supply(avax_glp_contract)
        avax_user_balance = get_user_glp_balance(avax_glp_contract, user_address)
        avax_mint_price, avax_redemption_price = calculate_prices(avax_total_assets, avax_glp_supply)

        st.subheader("Ethereum GLP Holdings")
        st.write(f"User Balance: {eth_user_balance}")
        st.write(f"Mint Price: {eth_mint_price}")
        st.write(f"Redemption Price: {eth_redemption_price}")

        st.subheader("Avalanche GLP Holdings")
        st.write(f"User Balance: {avax_user_balance}")
        st.write(f"Mint Price: {avax_mint_price}")
        st.write(f"Redemption Price: {avax_redemption_price}")

if __name__ == "__main__":
    main()
