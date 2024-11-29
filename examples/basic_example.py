import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kalshi_client.client import ExchangeClient
from kalshi_client.utils import load_private_key_from_file


if __name__ == "__main__":

    # You can get your api keys from https://kalshi.com/account/profile
    # It will ask you to save the RSA private key as text file
    # The key id is the one that is visible that you can copy paste

    key_id = "your key id"

    # Load private key from a file
    exchange_client = ExchangeClient(key_id=key_id, private_key=load_private_key_from_file("private_key.txt"))

    # Gets 5 open events
    events = exchange_client.get_events(limit=5, status='open')['events']

    # Prints all of the market tickers in events
    for event in events:
        markets = exchange_client.get_event(event['event_ticker'])['markets']
        for market in markets:
            print(market['ticker'])