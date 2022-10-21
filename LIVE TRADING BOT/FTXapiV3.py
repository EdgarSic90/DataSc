import time
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac
import requests
import pandas as pd


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _post_no_parse(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request_no_parse('POST', path, json=params)

    def _get_no_parse(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request_no_parse('GET', path, params=params)

    def _request_no_parse(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return response

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def list_futures(self) -> List[dict]:
        return self._get('futures')

    def list_markets(self) -> List[dict]:
        return self._get('markets')

    def get_market_data(self, market: str, interval: str = '15m'):
        if interval[len(interval) - 1] == "s":
            multiplier = 1
            interval = int(interval.replace("s", ''))
        elif interval[len(interval) - 1] == "m":
            multiplier = 60
            interval = int(interval.replace("m", ''))
        elif interval[len(interval) - 1] == "h":
            multiplier = 60 * 60
            interval = int(interval.replace("h", ''))
        elif interval[len(interval) - 1] == "d":
            multiplier = 60 * 60 * 24
            interval = int(interval.replace("d", ''))
        else:
            multiplier = 1
        resolution = interval * multiplier
        return self._get_no_parse(f'markets/{market}/candles', {
            'resolution': resolution
        })

    def get_historical_prices(
        self, market: str, resolution: int = 300, start_time: float = None,
        end_time: float = None
        ) -> List[dict]:
        return self._get(f'markets/{market}/candles', {
            'resolution': resolution,
            'start_time': start_time,
            'end_time': end_time
        })

    def parse_ftx_response(self, ftxjson : dict) -> pd.DataFrame():
        df = pd.DataFrame.from_dict(ftxjson['result'])
        return df.set_index('startTime')

    def get_binance_data(self, market:str, interval:str) -> any :
        binanceendpoint = f"https://api.binance.com/api/v3/klines?symbol={market}&interval={interval}"
        return requests.get(binanceendpoint)

    def parse_binance_response(self, binancejson : dict) -> pd.DataFrame():
        df = pd.DataFrame(data=binancejson)
        df = df.drop([6,7,8,9,10,11],axis = 1)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df['time']=(pd.to_datetime(df['time'],unit='ms'))
        df = df.set_index(df['time'])
        return df

    def get_okex_data(self, market : str, interval : str):
        okex_endpoint = f"https://www.okx.com/api/v5/market/candles?instId={market}&bar={interval}"
        return requests.get(okex_endpoint)

    def parse_okex_reponse(self, okexjson : dict) -> pd.DataFrame():
        df = pd.DataFrame.from_dict(okexjson['data'])
        df = df.drop(6, axis = 1)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df['time']=(pd.to_datetime(df['time'],unit='ms'))
        df = df.set_index(df['time'])
        return df.set_index('time')

    def get_orderbook(self, market: str, depth: int = None) -> dict:
        return self._get(f'markets/{market}/orderbook', {'depth': depth})

    def get_trades(self, market: str) -> dict:
        return self._get(f'markets/{market}/trades')

    def get_account_info(self) -> dict:
        return self._get(f'account')

    def get_open_orders(self, market: str = None) -> List[dict]:
        return self._get(f'orders', {'market': market})

    def get_order_history(self, market: str = None, side: str = None, order_type: str = None, start_time: float = None,
                          end_time: float = None) -> List[dict]:
        return self._get(f'orders/history',
                         {'market': market, 'side': side, 'orderType': order_type, 'start_time': start_time,
                          'end_time': end_time})

    def get_conditional_order_history(self, market: str = None, side: str = None, type: str = None,
                                      order_type: str = None, start_time: float = None, end_time: float = None) -> List[
        dict]:
        return self._get(f'conditional_orders/history',
                         {'market': market, 'side': side, 'type': type, 'orderType': order_type,
                          'start_time': start_time, 'end_time': end_time})

    def modify_order(
            self, existing_order_id: Optional[str] = None,
            existing_client_order_id: Optional[str] = None, price: Optional[float] = None,
            size: Optional[float] = None, client_order_id: Optional[str] = None,
    ) -> dict:
        assert (existing_order_id is None) ^ (existing_client_order_id is None), \
            'Must supply exactly one ID for the order to modify'
        assert (price is None) or (size is None), 'Must modify price or size of order'
        path = f'orders/{existing_order_id}/modify' if existing_order_id is not None else \
            f'orders/by_client_id/{existing_client_order_id}/modify'
        return self._post(path, {
            **({'size': size} if size is not None else {}),
            **({'price': price} if price is not None else {}),
            **({'clientId': client_order_id} if client_order_id is not None else {}),
        })

    def get_conditional_orders(self, market: str = None) -> List[dict]:
        return self._get(f'conditional_orders', {'market': market})

    def place_order(self, market: str, side: str, price: float, size: float, type: str = 'limit',
                    reduce_only: bool = False, ioc: bool = False, post_only: bool = False,
                    client_id: str = None) -> dict:
        return self._post_no_parse('orders', {'market': market,
                                     'side': side,
                                     'price': price,
                                     'size': size,
                                     'type': type,
                                     'reduceOnly': reduce_only,
                                     'ioc': ioc,
                                     'postOnly': post_only,
                                     'clientId': client_id,
                                     })

    def place_conditional_order(
            self, market: str, side: str, size: float, type: str = 'stop',
            limit_price: float = None, reduce_only: bool = False, cancel: bool = True,
            trigger_price: float = None, trail_value: float = None
    ) -> dict:
        """
        To send a Stop Market order, set type='stop' and supply a trigger_price
        To send a Stop Limit order, also supply a limit_price
        To send a Take Profit Market order, set type='trailing_stop' and supply a trigger_price
        To send a Trailing Stop order, set type='trailing_stop' and supply a trail_value
        """
        assert type in ('stop', 'take_profit', 'trailing_stop')
        assert type not in ('stop', 'take_profit') or trigger_price is not None, \
            'Need trigger prices for stop losses and take profits'
        assert type not in ('trailing_stop',) or (trigger_price is None and trail_value is not None), \
            'Trailing stops need a trail value and cannot take a trigger price'

        return self._post('conditional_orders',
                            {'market': market, 'side': side, 'triggerPrice': trigger_price,
                            'size': size, 'reduceOnly': reduce_only, 'type': type,
                            'cancelLimitOnTrigger': cancel, 'orderPrice': limit_price, 'trailValue': trail_value})

    def cancel_order(self, order_id: str) -> dict:
        return self._delete(f'orders/{order_id}')

    def cancel_trigger_order(self, order_id: str) -> dict:
        return self._delete(f'conditional_orders/{order_id}')

    def cancel_orders(self, market_name: str = None, conditional_orders: bool = False,
                      limit_orders: bool = False) -> dict:
        return self._delete(f'orders', {'market': market_name,
                                        'conditionalOrdersOnly': conditional_orders,
                                        'limitOrdersOnly': limit_orders,
                                        })

    def get_fills(self) -> List[dict]:
        return self._get(f'fills')

    def get_balances(self) -> List[dict]:
        return self._get('wallet/balances')

    def get_deposit_address(self, ticker: str) -> dict:
        return self._get(f'wallet/deposit_address/{ticker}')

    def get_positions(self, show_avg_price: bool = False) -> List[dict]:
        return self._get('positions', {'showAvgPrice': show_avg_price})

    def get_position(self, name: str, show_avg_price: bool = False) -> dict:
        return next(filter(lambda x: x['future'] == name, self.get_positions(show_avg_price)), None)
    
    def get_position_details(self, ticker : str) -> dict:
        d = self.get_position(name = ticker)
        r = {}
        if d == None:
            r['pctPnl'] = 0
            r['size'] = 0
            r['side']  = 'none'
            r['entryPrice'] = 0
        else:
            if d['size'] == 0.0:
                r['pctPnl'] = 0
                r['size'] = 0
                r['side']  = 'none'
                r['entryPrice'] = 0
            else:
                r['pctPnl'] = (d['recentPnl']/d['cost']) * 100
                r['size'] = d['size']
                r['side']  = d['side']
                r['entryPrice'] = d['entryPrice']
        return r

    def check_stoploss(self, ticker: str) -> str:
        check = self.get_conditional_orders(ticker)
        if check != []:
            return check[0]['id']
        else:
            return ""

    def check_position(self, ticker : str):
        check = self.get_position(ticker)
        if check == None:
            return 0,0
        else:
            size = check['size']
            side = check['side']
            entryprice = check['entryPrice']
            if size == 0:
                return 0,0
            else:
                if side == "sell":
                    return -1,entryprice
                else:
                    return 1,entryprice

    def get_all_open_positions(self) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(self.get_positions())
        return df.apply(lambda row: row[df['size'] != 0])

    def close_all_open_positions(self) -> None:
        df = self.get_all_open_positions()
        resultant_action = {'buy' : 'sell', 'sell' : 'buy'} # hash table, if the current side is sell, resultant action is buy and vice versa
        for i in range(len(df)):
            ticker = df['future'].iloc[i]
            position_size = df['size'].iloc[i]
            position_side = df['side'].iloc[i]
            print(ticker, position_side, position_size)
            action = resultant_action[position_side]
            resp = self.place_order(market=ticker, side=action, price=None,
                                    size=float(position_size), type='market')
            if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                print(f"Failed to close position {ticker} of size {position_size}, currently on {position_side}")
            else:
                print(f"Successfully close {ticker} of size {position_size}")
        return