# GLP Holdings Monitor

![image](https://github.com/Thisisily/glp_monitor/assets/44399258/7e0619ae-a3ad-44f0-b452-654b43c12935)

GLP Holdings Monitor is a Python-based tool designed to monitor a user's GLP (GLP Liquidity Provider) holdings, rewards, and fees across the Arbitrum and Avalanche networks. This tool provides a comprehensive overview of GLP balances, historical mint prices, token composition, and GLP transactions for a given wallet address.

## Features

- **Wallet Monitoring**: Monitor the GLP holdings, rewards, and fees for a specified wallet address.
- **Mint and Redemption Prices**: Calculate and display the average mint price and the current redemption price.
- **Transaction History**: Fetch and display all GLP-related transactions for the user's wallet.
- **Token Composition**: Visualize the composition of tokens in the GLP pool.
- **Streamlit UI**: Interactive and user-friendly interface using Streamlit.

## Prerequisites

- Python 3.6 or higher
- An Infura project ID for Web3 connectivity
- API keys for Arbiscan and Snowtrace

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/glp_holdings_monitor.git
   cd glp_holdings_monitor
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Configuration**:
   - Copy the `config.example.yml` to `config.yml` and fill in your API keys and other details.

   ```yaml
   api_key: 'YOUR_API_KEY'
   arb_provider_url: 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
   avax_provider_url: 'https://api.avax.network/ext/bc/C/rpc'
   arb_glp_contract_address: '0x1aDDD80E6039594eE970E5872D247bf0414C8903'
   avax_glp_contract_address: '0x9e295B5B976a184B14aD8cd72413aD846C299660'
   ```

5. **Download Contract ABI**:
   - Place the GLP contract ABI file in the `contracts` directory and name it `glp_abi.json`.

## Usage

### Streamlit Application

To run the Streamlit application, execute the following command:

```bash
streamlit run streamlit_app.py
```

### Command Line Monitoring

To monitor GLP holdings via the command line:

```bash
python monitor.py
```

## File Structure

```
glp_holdings_monitor/
│
├── contracts/
│   └── glp_abi.json          # ABI for the GLP contract
│
├── data/
│   └── ...                   # Directory for storing any data files
│
├── utils/
│   ├── __init__.py
│   ├── config_loader.py      # Functions to load configuration
│   ├── constants.py          # Constants such as token address maps and decimals
│   ├── monitor.py            # Core monitoring functions
│   └── web3_utils.py         # Web3 utility functions
│
├── .gitignore
├── config.example.yml        # Example configuration file
├── monitor.py                # Command-line monitoring script
├── requirements.txt          # Python dependencies
└── streamlit_app.py          # Streamlit application
```

## Configuration

The configuration file `config.yml` should contain the following entries:

```yaml
api_key: 'YOUR_API_KEY'
arb_provider_url: 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
avax_provider_url: 'https://api.avax.network/ext/bc/C/rpc'
arb_glp_contract_address: '0x1aDDD80E6039594eE970E5872D247bf0414C8903'
avax_glp_contract_address: '0x9e295B5B976a184B14aD8cd72413aD846C299660'
```

## Key Functions

### `monitor.py`

- **get_token_prices**: Fetches current prices of tokens using CoinGecko API.
- **get_historical_mint_prices_via_api**: Retrieves historical mint prices using the blockchain explorer API.
- **get_user_mint_transactions**: Fetches historical mint transactions for a user.
- **calculate_average_mint_price**: Calculates the average mint price based on user transactions.
- **get_current_redemption_price_via_api**: Fetches the current redemption price.
- **fetch_glp_data**: Retrieves GLP AUM and supply data from the subgraph API.
- **get_total_supply**: Fetches the total supply of GLP.
- **get_user_glp_balance**: Fetches the GLP balance of a user.
- **get_glp_transactions**: Fetches all GLP-related transactions for a given user.

### `streamlit_app.py`

- **main**: Main function to run the Streamlit application.
- **plot_token_composition**: Plots the token composition as a pie chart.

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE.

## Contact

For any inquiries or support, please open an issue on GitHub.
