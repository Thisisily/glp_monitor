import json
import streamlit as st
from utils.config_loader import load_config
from utils.web3_utils import setup_web3, load_contract
from utils.monitor import get_total_supply, get_user_glp_balance, calculate_prices_via_api, get_glp_transactions
from datetime import datetime
import pandas as pd

def main():
    st.set_page_config(page_title="GLP Holdings Monitor", layout="centered")

    # Custom header
    st.markdown("""
    <style>
    .header {
        font-size: 50px;
        font-weight: bold;
        color: #FF6347;
        text-align: center;
        padding: 20px 0;
    }
    .subheader {
        font-size: 30px;
        font-weight: bold;
        color: #4682B4;
    }
    .metric-label {
        font-size: 20px;
        font-weight: bold;
        color: #4682B4;
    }
    .metric-value {
        font-size: 20px;
        color: #000000;
    }
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header">GLP Holdings Monitor</div>', unsafe_allow_html=True)

    # Load configuration
    config = load_config()
    api_key = config['api_key']  # Ensure your API key is in the config file

    # Load the ABI
    with open('contracts/glp_abi.json', 'r') as abi_file:
        glp_abi = json.load(abi_file)

    # Setup Web3 connections
    arb_web3 = setup_web3(config['arb_provider_url'])
    avax_web3 = setup_web3(config['avax_provider_url'])

    arb_glp_contract = load_contract(arb_web3, config['arb_glp_contract_address'], glp_abi)
    avax_glp_contract = load_contract(avax_web3, config['avax_glp_contract_address'], glp_abi)

    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Ask the user for their wallet address
    user_address = st.text_input("Enter your wallet address:")

    if user_address:
        tabs = st.tabs(["Arbitrum GLP", "Avalanche GLP", "GLP Value", "Token Composition"])

        with tabs[0]:
            st.markdown('<div class="subheader">Arbitrum GLP Holdings</div>', unsafe_allow_html=True)
            arb_glp_supply = get_total_supply(arb_glp_contract)
            arb_user_balance = get_user_glp_balance(arb_glp_contract, user_address)
            arb_mint_price, arb_redemption_price = calculate_prices_via_api(config['arb_glp_contract_address'], api_key, network='arbitrum')

            st.metric(label="Total Supply", value=f"{arb_glp_supply:.2f} GLP")
            st.metric(label="User Balance", value=f"{arb_user_balance:.2f} GLP")
            st.metric(label="Mint Price", value=f"{arb_mint_price:.2f} USD")
            st.metric(label="Redemption Price", value=f"{arb_redemption_price:.2f} USD")

            st.markdown('<div class="subheader">Arbitrum GLP Transactions</div>', unsafe_allow_html=True)
            arb_transactions = get_glp_transactions(config['arb_glp_contract_address'], user_address, api_key, network='arbitrum')
            if arb_transactions:
                df_arb = pd.DataFrame(arb_transactions)
                df_arb['timeStamp'] = pd.to_datetime(df_arb['timeStamp'], unit='s')
                df_arb['value'] = df_arb['value'].astype(float) / 10**18
                df_arb = df_arb.rename(columns={'hash': 'Transaction Hash', 'from': 'From', 'to': 'To', 'value': 'Value (GLP)', 'timeStamp': 'Date'})
                st.dataframe(df_arb[['Transaction Hash', 'From', 'To', 'Value (GLP)', 'Date']])

        with tabs[1]:
            st.markdown('<div class="subheader">Avalanche GLP Holdings</div>', unsafe_allow_html=True)
            avax_glp_supply = get_total_supply(avax_glp_contract)
            avax_user_balance = get_user_glp_balance(avax_glp_contract, user_address)
            avax_mint_price, avax_redemption_price = calculate_prices_via_api(config['avax_glp_contract_address'], api_key, network='avalanche')

            st.metric(label="Total Supply", value=f"{avax_glp_supply:.2f} GLP")
            st.metric(label="User Balance", value=f"{avax_user_balance:.2f} GLP")
            st.metric(label="Mint Price", value=f"{avax_mint_price:.2f} USD")
            st.metric(label="Redemption Price", value=f"{avax_redemption_price:.2f} USD")

            st.markdown('<div class="subheader">Avalanche GLP Transactions</div>', unsafe_allow_html=True)
            avax_transactions = get_glp_transactions(config['avax_glp_contract_address'], user_address, api_key, network='avalanche')
            if avax_transactions:
                df_avax = pd.DataFrame(avax_transactions)
                df_avax['timeStamp'] = pd.to_datetime(df_avax['timeStamp'], unit='s')
                df_avax['value'] = df_avax['value'].astype(float) / 10**18
                df_avax = df_avax.rename(columns={'hash': 'Transaction Hash', 'from': 'From', 'to': 'To', 'value': 'Value (GLP)', 'timeStamp': 'Date'})
                st.dataframe(df_avax[['Transaction Hash', 'From', 'To', 'Value (GLP)', 'Date']])

        with tabs[2]:
            st.markdown('<div class="subheader">GLP Value</div>', unsafe_allow_html=True)
            glp_value = avax_user_balance * avax_mint_price  # Example for value calculation
            st.metric(label="Total GLP Value", value=f"{glp_value:.2f} USD")

        with tabs[3]:
            st.markdown('<div class="subheader">Token Composition</div>', unsafe_allow_html=True)
            token_composition = {
                "ETH": "50%",
                "BTC": "25%",
                "USDC": "25%"
            }
            for token, percentage in token_composition.items():
                st.write(f"**{token}:** {percentage}")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
