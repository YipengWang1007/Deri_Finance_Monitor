from datetime import datetime, timedelta
import requests
import json

TICKER_API_URL = "https://api.bittrex.com/api/v1.1/public/getticker?market="

def get_latest_crypto_price(crypto):
    url = TICKER_API_URL + crypto
    j = requests.get(url)
    data = json.loads(j.text)
    price = data["result"]["Ask"]
    print(price)
    return price

if __name__ == "__main__":
    get_latest_crypto_price("USD-BTC")
    get_latest_crypto_price("USD-ETH")
    