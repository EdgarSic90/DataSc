from FTXapiV3 import FtxClient
from assetClass import asset

# ltc = asset(name="AVAX-PERP", tp=1, sl=1)
ftx = FtxClient(api_key="",
            api_secret="")
# resp = ftx.get_market_data(market="BTC-PERP", interval="5m")
# for i in resp.json():
#     print(i)
# print(resp.json()['success'])
# r = ftx.get_position_details(ticker = ltc.name)
# print(r['size'], r['entryPrice'])
# ltc.set_initial_position(size = r['size'], side = r['side'], entry_price = r['entryPrice'])
# ltc.describe()
ltc = asset(name='LTC-PERP', tp = 2.2, sl=-1.1)

matic = asset(name='MATIC-PERP', tp = 2.2, sl=-1.1)

atom = asset(name='ATOM-PERP', tp = 2.2, sl=-1.1)

# =================================Place Assets in Array to loop through=================================

tickers = [ltc ,matic ,atom] #'''[avax, eth, ada, sol, snx ,ftt ,flow ,btc ,xrp ,algo ,'''
for i in range(len(tickers)):
    r = ftx.get_position_details(ticker = tickers[i].name)
    print(r['size'], r['entryPrice'])
    tickers[i].set_initial_position(size = r['size'], side = r['side'], entry_price = r['entryPrice'])

for i in tickers:
    i.describe()
