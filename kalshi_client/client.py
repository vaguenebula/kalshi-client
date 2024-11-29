import requests
import json
from datetime import datetime
from typing import Any, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import time 
import base64


class KalshiClient:
    """A simple client that allows utils to call authenticated Kalshi API endpoints."""
    def __init__(
        self,
        host: str,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        user_id: Optional[str] = None,
    ):
        """Initializes the client and logs in the specified user.
        Raises an HttpError if the user could not be authenticated.
        """
        self.host = host 
        self.key_id: str = key_id
        self.user_id = user_id
        self.private_key: rsa.RSAPrivateKey = private_key
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json",
                                     "KALSHI-ACCESS-KEY": self.key_id,})
        self.last_api_call = datetime.now()

    """Built in rate-limiter. We STRONGLY encourage you to keep 
    some sort of rate limiting, just in case there is a bug in your 
    code. Feel free to adjust the threshold"""
    def rate_limit(self) -> None:

        # Define the time threshold in seconds
        THRESHOLD_IN_SECONDS = 0.1

        # Check if the time since the last API call is below the threshold
        elapsed_time = (datetime.now() - self.last_api_call).total_seconds()
        if elapsed_time < THRESHOLD_IN_SECONDS:
            time.sleep(THRESHOLD_IN_SECONDS - elapsed_time)

        # Update the last API call timestamp
        self.last_api_call = datetime.now()


    def post(self, path: str, body: dict) -> Any:
        """POSTs to an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results.
        """
        self.rate_limit()

        response = self.session.post(
            self.host + path, data=body, headers=self.request_headers("POST", path)
        )
        self.raise_if_bad_response(response)
        return response.json()

    def get(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """GETs from an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results."""
        self.rate_limit()
        
        response = self.session.get(
            self.host + path, headers=self.request_headers("GET", path), params=params
        )
        self.raise_if_bad_response(response)
        return response.json()

    def delete(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """Posts from an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results."""
        self.rate_limit()
        
        response = self.session.delete(
            self.host + path, headers=self.request_headers("DELETE", path), params=params
        )
        self.raise_if_bad_response(response)
        return response.json()

    def request_headers(self, method: str, path: str) -> Dict[str, Any]:
        # Generate the current timestamp in milliseconds
        timestampt_str = str(int(datetime.now().timestamp() * 1000))

        # Extract the path without query parameters
        clean_path = path.split('?', 1)[0]

        # Construct the message string for signing
        msg_string = f"{timestampt_str}{method}/trade-api/v2{clean_path}"

        # Sign the message string
        signature = self.sign_pss_text(msg_string)

        # Build headers dictionary
        headers = {
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestampt_str,
        }
        return headers

    
    def sign_pss_text(self, text: str) -> str:
        # Before signing, we need to hash our message.
        # The hash is what we actually sign.
        # Convert the text to bytes
        message = text.encode('utf-8')
        try:
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

    def raise_if_bad_response(self, response: requests.Response) -> None:
        if response.status_code not in range(200, 299):
            if response.status_code == 404:
                raise HttpError(response.reason, response.status_code, tip='Check ticker used for call if one was provided')
            elif response.status_code == 400:
                raise HttpError(response.reason, response.status_code, tip='One or more of the parameters could be wrong')
            else:
                raise HttpError(response.reason, response.status_code)
            
    def query_generation(self, params:dict) -> str:
        """
        Generate a URL query string from a dictionary of parameters.

        Args:
            params (dict): Dictionary of parameters where keys are strings and values
                        are either strings or values convertible to strings.

        Returns:
            str: A properly formatted query string, or an empty string if no parameters are provided.
        """
        query = '&'.join(f'{str(k)}={str(v)}' for k, v in params.items() if v)
        return f'?{query}' if query else ''

class HttpError(Exception):
    """Represents an HTTP error with reason and status code."""
    def __init__(self, reason: str, status: int, tip: str = None):
        super().__init__(reason)
        self.reason = reason
        self.status = status
        self.tip = tip

    def __str__(self) -> str:
        return f'\n\nHttpError({self.status} {self.reason})\nTip: {self.tip}\n'

class ExchangeClient(KalshiClient):
    def __init__(self, key_id: str, private_key: rsa.RSAPrivateKey, 
                 exchange_api_base: str = 'https://api.elections.kalshi.com/trade-api/v2'):
        super().__init__(
            exchange_api_base,
            key_id,
            private_key,
        )
        self.key_id = key_id
        self.private_key = private_key
        self.exchange_url = "/exchange"
        self.markets_url = "/markets"
        self.events_url = "/events"
        self.series_url = "/series"
        self.portfolio_url = "/portfolio"

    def logout(self,):
        result = self.post("/logout")
        return result

    def get_exchange_status(self,):
        result = self.get(self.exchange_url + "/status")
        return result

    # market endpoints!

    def get_markets(self,
                        limit:Optional[int]=None,
                        cursor:Optional[str]=None,
                        event_ticker:Optional[str]=None,
                        series_ticker:Optional[str]=None,
                        max_close_ts:Optional[int]=None,
                        min_close_ts:Optional[int]=None,
                        status:Optional[str]=None,
                        tickers:Optional[str]=None,
                            ):
        return self.get(self.markets_url + self.query_generation(locals()))

    def get_events(self,
                        limit:Optional[int]=None,
                        cursor:Optional[str]=None,
                        series_ticker:Optional[str]=None,
                        status:Optional[str]=None,
                        ):
        return self.get(self.events_url + self.query_generation(locals()))

    def get_market_url(self, 
                        ticker:str):
        return self.markets_url+'/'+ticker

    def get_market(self, 
                    ticker:str):
        market_url = self.get_market_url(ticker=ticker)
        dictr = self.get(market_url)
        return dictr

    def get_event(self, 
                    event_ticker: str):
        return self.get(f'{self.events_url}/{event_ticker}')

    def get_series(self, 
                    series_ticker:str):
        dictr = self.get(self.series_url + '/' + series_ticker)
        return dictr

    def get_market_history(self, 
                            ticker:str,
                            limit:Optional[int]=None,
                            cursor:Optional[str]=None,
                            max_ts:Optional[int]=None,
                            min_ts:Optional[int]=None,
                            ):
        relevant_params = {k: v for k, v in locals().items() if k != 'ticker'}                            
        query_string = self.query_generation(params = relevant_params)
        market_url = self.get_market_url(ticker = ticker)
        return self.get(market_url + '/history' + query_string)

    def get_orderbook(self, 
                        ticker:str,
                        depth:Optional[int]=None,
                        ):
        relevant_params = {k: v for k, v in locals().items() if k != 'ticker'}                            
        query_string = self.query_generation(params = relevant_params)
        market_url = self.get_market_url(ticker)
        dictr = self.get(market_url + "/orderbook" + query_string)
        return dictr

    def get_trades(self,
                    ticker:Optional[str]=None,
                    limit:Optional[int]=None,
                    cursor:Optional[str]=None,
                    max_ts:Optional[int]=None,
                    min_ts:Optional[int]=None,
                    ):
        query_string = self.query_generation(params={k: v for k,v in locals().items()})
        if ticker:
            if len(query_string):
                query_string += '&'
            else:
                query_string += '?'
            query_string += "ticker=" + ticker
            
        trades_url = self.markets_url + '/trades'
        dictr = self.get(trades_url + query_string)
        return dictr

    # portfolio endpoints!

    def get_balance(self,):
        return self.get(self.portfolio_url + '/balance')

    def create_order(self,
                 ticker: str,
                 client_order_id: str,
                 side: str,
                 action: str,
                 count: int,
                 type: str,
                 yes_price: Optional[int] = None,
                 no_price: Optional[int] = None,
                 expiration_ts: Optional[int] = None,
                 sell_position_floor: Optional[int] = None,
                 buy_max_cost: Optional[int] = None,
                 ):
        """
        Creates an order with the specified parameters.

        Args
        -----------
        ticker : str
            Required. The ticker of the market where the order will be placed.
            
        client_order_id : str
            Required. Unique identifier for the client order. Use str(uuid4())

        side : str
            Required. Specifies the side of the trade. Accepts either 'yes' or 'no'.
            
        action : str
            Required. Indicates whether the order is a 'buy' or 'sell'.
            
        count : int
            Required. Number of contracts to be bought or sold.
            
        type : str
            Required. Specifies the type of order. Accepts either 'market' or 'limit'.
            For limit orders, one of `yes_price` or `no_price` must be provided.
            
        yes_price : Optional[int]
            Optional. Price (in cents) for the Yes side of the trade. Exactly one of 
            `yes_price` or `no_price` must be provided. If both are provided, the request 
            will return a 400 error.

        no_price : Optional[int]
            Optional. Price (in cents) for the No side of the trade. Exactly one of 
            `yes_price` or `no_price` must be provided. If both are provided, the request 
            will return a 400 error.

        expiration_ts : Optional[int]
            Optional. Expiration time of the order in Unix timestamp (seconds). 
            - If not provided, the order will remain active until explicitly cancelled 
            (Good 'Till Cancelled - GTC).
            - If set in the past, the order will attempt to fill partially or completely, 
            with the remaining unfilled quantity cancelled (Immediate-or-Cancel - IOC).
            - If set in the future, the remaining unfilled quantity will expire at the 
            specified time.
            
        sell_position_floor : Optional[int]
            Optional. If set to 0, prevents flipping the position for a market order.

        buy_max_cost : Optional[int]
            Optional. Maximum cost (in cents) allowed for a market buy order. 
            Only applicable if `type='market'` and `action='buy'`.

        Returns
        --------
        dict
            Response from the API containing the details of the created order.
        """
        relevant_params = {k: v for k, v in locals().items() if k != 'self' and v}
        order_json = json.dumps(relevant_params)
        orders_url = self.portfolio_url + '/orders'
        result = self.post(path=orders_url, body=order_json)
        return result


    def batch_create_orders(self, 
                                orders:list
        ):
        orders_json = json.dumps({'orders': orders})
        batched_orders_url = self.portfolio_url + '/orders/batched'
        result = self.post(path = batched_orders_url, body = orders_json)
        return result

    def decrease_order(self, 
                        order_id:str,
                        reduce_by:int,
                        ):
        order_url = self.portfolio_url + '/orders/' + order_id
        decrease_json = json.dumps({'reduce_by': reduce_by})
        result = self.post(path = order_url + '/decrease', body = decrease_json)
        return result

    def cancel_order(self,
                        order_id:str
                        ):
        order_url = self.portfolio_url + '/orders/' + order_id
        result = self.delete(path = order_url)
        return result

    def batch_cancel_orders(self, 
                                order_ids:list
        ):
        order_ids_json = json.dumps({"ids":order_ids})
        batched_orders_url = self.portfolio_url + '/orders/batched'
        result = self.delete(path = batched_orders_url, body = order_ids_json)
        return result

    def get_fills(self,
                        ticker:Optional[str]=None,
                        order_id:Optional[str]=None,
                        min_ts:Optional[int]=None,
                        max_ts:Optional[int]=None,
                        limit:Optional[int]=None,
                        cursor:Optional[str]=None):

        fills_url = self.portfolio_url + '/fills'
        query_string = self.query_generation(params={k: v for k,v in locals().items()})
        dictr = self.get(fills_url + query_string)
        return dictr
    
    def get_orders(self,
                        ticker:Optional[str]=None,
                        event_ticker:Optional[str]=None,
                        min_ts:Optional[int]=None,
                        max_ts:Optional[int]=None,
                        limit:Optional[int]=None,
                        cursor:Optional[str]=None
                        ):
        orders_url = self.portfolio_url + '/orders'
        query_string = self.query_generation(params={k: v for k,v in locals().items()})
        dictr = self.get(orders_url + query_string)
        return dictr
    
    def get_order(self,
                    order_id:str):
        orders_url = self.portfolio_url + '/orders'
        dictr = self.get(orders_url + '/' +  order_id)
        return dictr
    
    def get_positions(self,
                  limit: Optional[int] = None,
                  cursor: Optional[str] = None,
                  settlement_status: Optional[str] = None,
                  ticker: Optional[str] = None,
                  event_ticker: Optional[str] = None,
                  count_filter: Optional[str] = None):
        """
        Retrieve a list of positions based on the specified query parameters.

        Args
        ----------
        limit : Optional[int], default=None
            Specifies the number of results to return per page. Must be between 1 and 1000.
            Defaults to 100 if not provided.

        cursor : Optional[str], default=None
            A pagination pointer to the next page of records. 
            - If provided, the API will return the next page containing the number of records specified in the `limit` parameter.
            - If not provided, the API will return the first page of the results for the query.
            Note: The `cursor` does not store filters. Therefore, any filters (e.g., `settlement_status`, `ticker`, or `event_ticker`) passed in the original query must be passed again.

        settlement_status : Optional[str], default=None
            Filters positions based on their settlement status. Valid values include:
            - `all`: Retrieve all settlement statuses.
            - `settled`: Retrieve only settled positions.
            - `unsettled`: Retrieve only unsettled positions.
            Defaults to `unsettled`.

        ticker : Optional[str], default=None
            Filters positions by the specified ticker.

        event_ticker : Optional[str], default=None
            Filters positions by the specified event ticker.

        count_filter : Optional[str], default=None
            Restricts positions to those where any of the specified fields have non-zero values. 
            Accepts a comma-separated list of the following fields:
            - `position`: Filters positions with non-zero position values.
            - `total_traded`: Filters positions with non-zero total traded values.
            - `resting_order_count`: Filters positions with non-zero resting order count.

        Returns
        -------
        dict
            A dictionary containing the retrieved positions and associated metadata.
        """
        positions_url = self.portfolio_url + '/positions'
        query_string = self.query_generation(params={k: v for k, v in locals().items()})
        dictr = self.get(positions_url + query_string)
        return dictr


    def get_portfolio_settlements(self,
                                    limit:Optional[int]=None,
                                    cursor:Optional[str]=None,):

        positions_url = self.portfolio_url + '/settlements'
        query_string = self.query_generation(params={k: v for k,v in locals().items()})
        dictr = self.get(positions_url + query_string)
        return dictr