import json
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from kalshi_client.connector import Connector


class KalshiClient(Connector):
    def __init__(self, key_id: str, private_key: rsa.RSAPrivateKey, 
                 exchange_api_base: str = 'https://api.elections.kalshi.com/trade-api/v2',
                 rate_limit: int = 10):
        super().__init__(
            exchange_api_base,
            key_id,
            private_key,
            rate_limit
        )
        """
        Initializes the KalshiClient.

        Args:
            key_id (str): The key id for the client.
            private_key (rsa.RSAPrivateKey): The private key for the client.
            exchange_api_base (str, optional): The base URL for the Kalshi API. Defaults to 'https://api.elections.kalshi.com/trade-api/v2'.
            rate_limit (int, optional): The rate limit for the client (per second). Defaults to 10.
        """
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
        """
        Gets the markets based on the specified query parameters.

        Args:
            limit (Optional[int], optional): Specifies the number of results to return per page. Must be between 1 and 1000. Defaults to 100.
            cursor (Optional[str], optional): A pagination pointer to the next page of records. If provided, the API will return the next page containing the number of records specified in the `limit` parameter. If not provided, the API will return the first page of the results for the query. Note: The `cursor` does not store filters. Therefore, any filters (e.g., `event_ticker`, `series_ticker`, `max_close_ts`, `min_close_ts`, or `status`) passed in the original query must be passed again. Defaults to None.
            event_ticker (Optional[str], optional): Filters markets by the specified event ticker. Defaults to None.
            series_ticker (Optional[str], optional): Filters markets by the specified series ticker. Defaults to None.
            max_close_ts (Optional[int], optional): Filters markets with a close timestamp less than or equal to the specified timestamp. Defaults to None.
            min_close_ts (Optional[int], optional): Filters markets with a close timestamp greater than or equal to the specified timestamp. Defaults to None.
            status (Optional[str], optional): Filters markets by their status. Valid values include: `unopened`, `open`, `closed`, `settled`. Defaults to None.
            tickers (Optional[str], optional): Filters markets by the specified tickers, as a comma separated list. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved markets and associated metadata
        """
        return self.get(self.markets_url + self.query_generation(locals()))

    def get_events(self,
                        limit:Optional[int]=None,
                        cursor:Optional[str]=None,
                        series_ticker:Optional[str]=None,
                        status:Optional[str]=None,
                        with_nested_markets:Optional[bool]=None,
                        ):
        """
        Gets the events based on the specified query parameters.

        Args:
            limit (Optional[int], optional): Specifies the number of results to return per page. Must be between 1 and 1000. Defaults to 100.
            cursor (Optional[str], optional): A pagination pointer to the next page of records. If provided, the API will return the next page containing the number of records specified in the `limit` parameter. If not provided, the API will return the first page of the results for the query. Note: The `cursor` does not store filters. Therefore, any filters (e.g., `series_ticker` or `status`) passed in the original query must be passed again. Defaults to None.
            series_ticker (Optional[str], optional): Filters events by the specified series ticker. Defaults to None.
            status (Optional[str], optional): Filters events by their status. Valid values include: `unopened`, `open`, `closed`, `settled`. Defaults to None.
            with_nested_markets (Optional[bool], optional): If `True`, retrieves nested markets within the event. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved events and associated metadata
        """
        return self.get(self.events_url + self.query_generation(locals()))

    def get_market_url(self, 
                        ticker:str):
        """
        Get the URL for a specific market based on its ticker.
        
        Args:
            ticker (str): The market ticker.
        
        Returns:
            str: The URL for the specified market.
        """
        return self.markets_url+'/'+ticker

    def get_market(self, 
                    ticker:str):
        market_url = self.get_market_url(ticker=ticker)
        dictr = self.get(market_url)
        return dictr

    def get_event(self, 
                    event_ticker: str,
                    with_nested_markets: Optional[bool] = None):
        """
        Get the event based on the event ticker.

        Args:
            event_ticker (str): The event ticker.
            with_nested_markets (Optional[bool], optional): If `True`, retrieves nested markets within the event. Defaults to None.
        
        Returns:
            dict: A dictionary containing the retrieved event and associated metadata
        """
        if with_nested_markets is not None:
            return self.get(f'{self.events_url}/{event_ticker}?with_nested_markets={with_nested_markets}')
        return self.get(f'{self.events_url}/{event_ticker}')

    def get_series(self, 
                    series_ticker:str):
        dictr = self.get(self.series_url + '/' + series_ticker)
        return dictr

    def get_market_candlesticks(self, 
                                ticker: str,
                                series_ticker: str,
                                start_ts: int,
                                end_ts: int,
                                period_interval: int):
        """
        Get the candlesticks for a specific market based on the specified query parameters.

        Args:
            ticker (str): The market ticker.
            series_ticker (str): The series ticker.
            start_ts (int): The start timestamp in unix seconds.
            end_ts (int): The end timestamp in unix seconds.
            period_interval (int): Specifies the length of each candlestick period, in minutes. Must be one minute, one hour, or one day.
        
        Returns:
            dict: A dictionary containing the retrieved candlesticks and associated metadata.
        """
        params = {
            'start_ts': start_ts,
            'end_ts': end_ts,
            'period_interval': period_interval
        }
        query_string = self.query_generation(params)
        url = f'/series/{series_ticker}/markets/{ticker}/candlesticks{query_string}'
        return self.get(url)

    def get_orderbook(self, 
                        ticker:str,
                        depth:Optional[int]=None,
                        ):
        """
        Get the orderbook for a specific market based on the specified query parameters.
        
        Args:
            ticker (str): The market ticker.
            depth (Optional[int], optional): Depth specifies the maximum number of orderbook price levels you want to see for either side. Only the highest (most relevant) price level are kept.
        
        Returns:
            dict: A dictionary containing the retrieved orderbook and associated metadata
        """
        relevant_params = {k: v for k, v in locals().items() if k != 'ticker'}                            
        query_string = self.query_generation(params = relevant_params)
        market_url = self.get_market_url(ticker)
        return self.get(market_url + "/orderbook" + query_string)

    def get_trades(self,
                    ticker:Optional[str]=None,
                    limit:Optional[int]=None,
                    cursor:Optional[str]=None,
                    max_ts:Optional[int]=None,
                    min_ts:Optional[int]=None,
                    ):
        
        query_string = self.query_generation(locals())
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