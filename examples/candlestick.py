import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kalshi_client.client import KalshiClient
from kalshi_client.utils import load_private_key_from_file
from kalshi_client.technical import *
import time

if __name__ == "__main__":

    key_id = "your key id"

    # Load private key from a file
    exchange_client = KalshiClient(key_id=key_id, private_key=load_private_key_from_file("private_key.txt"))

    current_timestamp = int(time.time())
    seconds_in_14_days = 14 * 24 * 60 * 60
    timestamp_14_days_ago = current_timestamp - seconds_in_14_days

    # The interval must be in minutes
    # In this example, I use an interval of 1 day
    interval = 1440

    # Candlesticks requires both market and series tickers
    market_ticker = 'KXOSCARACTO-25-AB'
    event_ticker = exchange_client.get_market(market_ticker)['market']['event_ticker']
    series_ticker = exchange_client.get_event(event_ticker)['event']['series_ticker']
    
    candlesticks = exchange_client.get_market_candlesticks(market_ticker, series_ticker, 
                                                timestamp_14_days_ago, 
                                                current_timestamp, interval)['candlesticks']
    
    # Prints prices from the last 15 days
    print([i['price']['close'] for i in candlesticks])

    # Print indicators
    print(calculate_ema(candlesticks))
    print(calculate_macd(candlesticks))
    print(calculate_rsi(candlesticks))
    print(calculate_stochastic_oscillator(candlesticks))


    