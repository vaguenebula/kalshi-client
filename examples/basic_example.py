import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kalshi_client.client import KalshiClient
from kalshi_client.utils import load_private_key_from_file


if __name__ == "__main__":

    # You can get your api keys from https://kalshi.com/account/profile
    # It will ask you to save the RSA private key as text file
    # The key id is the one that is visible that you can copy paste

    key_id = "your key id"

    # Load private key from a file
    kalshi_client = KalshiClient(key_id=key_id, private_key=load_private_key_from_file("private_key.txt"))

    # Gets 50 open events
    events = kalshi_client.get_events(limit=50, status='open', with_nested_markets=True)['events']

    # Prints all of the market tickers in events
    for event in events:
        markets = event['markets']
        for market in markets:
            print(market['ticker'])