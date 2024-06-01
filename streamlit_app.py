import asyncio
import streamlit as st

from utils.constants import ARBITRUM_TOKEN_ADDRESS_MAP, AVALANCHE_TOKEN_ADDRESS_MAP, DECIMALS

# Create and set an event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Now we can import web3 and other modules
from utils.config_loader import load_config
from utils.web3_utils import setup_web3, load_contract
from utils.monitor import calculate_average_mint_price, fetch_glp_data, get_total_supply, get_user_glp_balance, calculate_prices_via_api, get_glp_transactions, get_token_composition_scraping, calculate_wallet_exposure
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json

def plot_token_composition(token_composition, network_name, token_address_map):
    token_address_map = {k.lower(): v for k, v in token_address_map.items()}
    
    tokens = [token_address_map.get(token, token) for token in token_composition.keys()]
    weights = [weight * 100 for weight in token_composition.values()]

    fig, ax = plt.subplots(figsize=(6, 4))  # Increased the figure size here
    wedges, texts, autotexts = ax.pie(weights, labels=tokens, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"{network_name.capitalize()} Token Composition")
    
    # Adding legend outside the pie chart
    ax.legend(wedges, tokens, title="Tokens", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Styling the text
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=10)

    st.pyplot(fig)

    st.markdown("### Token Composition Details")
    for token, weight in token_composition.items():
        st.markdown(f"**{token_address_map.get(token, token)}:** {weight * 100:.2f}%")

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
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        padding: 10px 0;
    }
    .metric {
        flex: 1;
        min-width: 200px;
        max-width: 300px;
        margin: 10px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric label {
        font-size: 18px;
        font-weight: bold;
        color: #555;
    }
    .metric span {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    .main-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
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
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        arb_user_balance = get_user_glp_balance(arb_glp_contract, user_address)
        avax_user_balance = get_user_glp_balance(avax_glp_contract, user_address)

        # Fetch GLP data
        arb_glp_data = fetch_glp_data('arbitrum')
        avax_glp_data = fetch_glp_data('avalanche')

        arb_aum_in_usdg = arb_glp_data['aum_in_usdg'] / (10 ** DECIMALS)
        avax_aum_in_usdg = avax_glp_data['aum_in_usdg'] / (10 ** DECIMALS)
        arb_glp_supply = arb_glp_data['glp_supply'] / (10 ** DECIMALS)
        avax_glp_supply = avax_glp_data['glp_supply'] / (10 ** DECIMALS)
        arb_glp_price = arb_glp_data['price']
        avax_glp_price = avax_glp_data['price']

        # Summary Section
        st.markdown('<div class="subheader">Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric">
                <label>Wallet Address</label>
                <span>{user_address}</span>
            </div>
            <div class="metric">
                <label>Arbitrum GLP Balance</label>
                <span>{arb_user_balance:.2f} GLP</span>
            </div>
            <div class="metric">
                <label>Arbitrum GLP Value</label>
                <span>{arb_user_balance * arb_glp_price:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Avalanche GLP Balance</label>
                <span>{avax_user_balance:.2f} GLP</span>
            </div>
            <div class="metric">
                <label>Avalanche GLP Value</label>
                <span>{avax_user_balance * avax_glp_price:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Total GLP Value</label>
                <span>{arb_user_balance * arb_glp_price + avax_user_balance * avax_glp_price:.2f} USD</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric">
                <label>Arbitrum GLP Price</label>
                <span>{arb_glp_price:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Arbitrum Market Cap</label>
                <span>{arb_aum_in_usdg:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Arbitrum Total Supply</label>
                <span>{arb_glp_supply:.2f} GLP</span>
            </div>
            <div class="metric">
                <label>Avalanche GLP Price</label>
                <span>{avax_glp_price:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Avalanche Market Cap</label>
                <span>{avax_aum_in_usdg:.2f} USD</span>
            </div>
            <div class="metric">
                <label>Avalanche Total Supply</label>
                <span>{avax_glp_supply:.2f} GLP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # st.write(f"Your wallet address: **{user_address}**")
        # st.write(f"On Arbitrum, you hold **{arb_user_balance:.2f} GLP** valued at approximately **{arb_user_balance * arb_glp_price:.2f} USD**.")
        # st.write(f"On Avalanche, you hold **{avax_user_balance:.2f} GLP** valued at approximately **{avax_user_balance * avax_glp_price:.2f} USD**.")
        # st.write(f"Current GLP stats:")
        # st.write(f"Arbitrum - Price: **{arb_glp_price:.2f} USD**, Market Cap: **{arb_aum_in_usdg:.2f} USD**, Supply: **{arb_glp_supply:.2f} GLP**")
        # st.write(f"Avalanche - Price: **{avax_glp_price:.2f} USD**, Market Cap: **{avax_aum_in_usdg:.2f} USD**, Supply: **{avax_glp_supply:.2f} GLP**")


        tabs = st.tabs(["Arbitrum GLP", "Avalanche GLP", "GLP Value", "Token Composition"])
        with tabs[0]:
            st.markdown('<div class="subheader">Arbitrum GLP Holdings</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)  # Define the columns layout
            with col1:
                st.markdown(f'<div class="metric"><label>Total Supply</label><span>{arb_glp_supply:.2f} GLP</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric"><label>User Balance</label><span>{arb_user_balance:.2f} GLP</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric"><label>Mint Price</label><span>{arb_glp_price:.2f} USD</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric"><label>Market Cap</label><span>{arb_aum_in_usdg:.2f} USD</span></div>', unsafe_allow_html=True)

            st.markdown('<div class="subheader">Arbitrum GLP Transactions</div>', unsafe_allow_html=True)
            arb_transactions = get_glp_transactions(config['arb_glp_contract_address'], user_address, api_key, network='arbitrum')
            if arb_transactions:
                df_arb = pd.DataFrame(arb_transactions)
                df_arb['timeStamp'] = pd.to_datetime(df_arb['timeStamp'], unit='s')
                df_arb['value'] = df_arb['value'].astype(float) / 10**18
                df_arb = df_arb.rename(columns=({'hash': 'Transaction Hash', 'from': 'From', 'to': 'To', 'value': 'Value (GLP)', 'timeStamp': 'Date'}))
                st.dataframe(df_arb[['Transaction Hash', 'From', 'To', 'Value (GLP)', 'Date']])

            # Display user's exposure to underlying tokens
            st.markdown('<div class="subheader">Arbitrum GLP Token Exposure</div>', unsafe_allow_html=True)
            arb_exposure = calculate_wallet_exposure(arb_user_balance, network='arbitrum')
            for token, exposure in arb_exposure.items():
                st.write(f"**{token}:** {exposure:.2f} USD")

        with tabs[1]:
            st.markdown('<div class="subheader">Avalanche GLP Holdings</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)  # Define the columns layout
            with col1:
                st.markdown(f'<div class="metric"><label>Total Supply</label><span>{avax_glp_supply:.2f} GLP</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric"><label>User Balance</label><span>{avax_user_balance:.2f} GLP</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric"><label>Mint Price</label><span>{avax_glp_price:.2f} USD</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric"><label>Market Cap</label><span>{avax_aum_in_usdg:.2f} USD</span></div>', unsafe_allow_html=True)

            st.markdown('<div class="subheader">Avalanche GLP Transactions</div>', unsafe_allow_html=True)
            avax_transactions = get_glp_transactions(config['avax_glp_contract_address'], user_address, api_key, network='avalanche')
            if avax_transactions:
                df_avax = pd.DataFrame(avax_transactions)
                df_avax['timeStamp'] = pd.to_datetime(df_avax['timeStamp'], unit='s')
                df_avax['value'] = df_avax['value'].astype(float) / 10**18
                df_avax = df_avax.rename(columns=({'hash': 'Transaction Hash', 'from': 'From', 'to': 'To', 'value': 'Value (GLP)', 'timeStamp': 'Date'}))
                st.dataframe(df_avax[['Transaction Hash', 'From', 'To', 'Value (GLP)', 'Date']])

            # Display user's exposure to underlying tokens
            st.markdown('<div class="subheader">Avalanche GLP Token Exposure</div>', unsafe_allow_html=True)
            avax_exposure = calculate_wallet_exposure(avax_user_balance, network='avalanche')
            for token, exposure in avax_exposure.items():
                st.write(f"**{token}:** {exposure:.2f} USD")

        with tabs[2]:
            st.markdown('<div class="subheader">GLP Value</div>', unsafe_allow_html=True)
            arb_glp_value = arb_user_balance * arb_glp_price  # Updated calculation using arb_glp_price
            avax_glp_value = avax_user_balance * avax_glp_price  # Updated calculation using avax_glp_price
            total_glp_value = arb_glp_value + avax_glp_value

            # Calculate average mint price
            avg_arb_mint_price = calculate_average_mint_price(arb_transactions)
            avg_avax_mint_price = calculate_average_mint_price(avax_transactions)

            # Calculate PnL
            arb_pnl = (arb_glp_price - avg_arb_mint_price) * arb_user_balance
            avax_pnl = (avax_glp_price - avg_avax_mint_price) * avax_user_balance
            total_pnl = arb_pnl + avax_pnl

            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Arbitrum GLP Value</label><span>{arb_glp_value:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Avalanche GLP Value</label><span>{avax_glp_value:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Total GLP Value</label><span>{total_glp_value:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Average Arbitrum Mint Price</label><span>{avg_arb_mint_price:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Average Avalanche Mint Price</label><span>{avg_avax_mint_price:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric"><label>Total PnL</label><span>{total_pnl:.2f} USD</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[3]:
            st.markdown('<div class="subheader">Token Composition</div>', unsafe_allow_html=True)
            arb_token_composition = get_token_composition_scraping(network='arbitrum')
            avax_token_composition = get_token_composition_scraping(network='avalanche')
            
            st.markdown('<div class="subheader">Arbitrum Token Composition</div>', unsafe_allow_html=True)
            plot_token_composition(arb_token_composition, 'Arbitrum', ARBITRUM_TOKEN_ADDRESS_MAP)
            
            st.markdown('<div class="subheader">Avalanche Token Composition</div>', unsafe_allow_html=True)
            plot_token_composition(avax_token_composition, 'Avalanche', AVALANCHE_TOKEN_ADDRESS_MAP)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

