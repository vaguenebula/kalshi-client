# kalshi-client
An unofficial python client for the Kalshi API. 

This package fixes some of the outdated code that was provided by Kalshi in their API documentation. This project aims to facilitate usage of the API through documentation and readability. 

## Changes
- Removed old endpoints and added new ones
- Added parameters that weren't in original code
- Added documentation and made code readable
- Use requests session for static parts of headers

## Installation

```bash
pip install kalshi-client
```

## Usage

Below is an example of how to use `kalshi-client` to print your balance on Kalshi

```python
from kalshi_client.client import ExchangeClient
from kalshi_client.utils import load_private_key_from_file

if __name__ == "__main__":

    # You can get your api keys from https://kalshi.com/account/profile
    # It will ask you to save the RSA private key as text file
    # The key id is the one that is visible that you can copy paste

    key_id = "your key id"
    exchange_client = ExchangeClient(key_id=key_id, private_key=load_private_key_from_file("private_key.txt"))

    print(exchange_client.get_balance())
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Credits
- Starter code from Kalshi API docs: https://trading-api.readme.io/reference/get-started-on-kalshi

## License

This project is licensed under the MIT License.

## Disclaimer

By using this client, you agree to Kalshi's [Developer Agreement](https://kalshi.com/developer-agreement).

*Note: This client is an unofficial implementation and is not affiliated with Kalshi.* 
