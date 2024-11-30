from uuid import uuid4
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kalshi_client.client import KalshiClient
from kalshi_client.utils import load_private_key_from_file


if __name__ == "__main__":

    key_id = "your key id"
    kalshi_client = KalshiClient(key_id=key_id, private_key=load_private_key_from_file("private_key.txt"))

    # Create a market order
    kalshi_client.create_order(ticker='TICKER GOES HERE', client_order_id=str(uuid4()), 
                                 action='buy', side='yes', count=100, type='market')
