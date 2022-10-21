import talib
import pandas as pd
import numpy as np
from binance import Client
import datetime
from assetClass import asset

# ===================== Getting the data from Binance Client =====================
def get_binance_data(ticker : str, timeframe : str, period : int) -> pd.DataFrame:
    yes = Client()
    day = datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(days=period))
    res = yes.get_historical_klines(symbol = ticker, interval = timeframe, start_str=str(day))
    df = pd.DataFrame(data=res)
    df = df.drop([6,7,8,9,10,11],axis = 1)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    z = ['open', 'high', 'low', 'close', 'volume']
    for i in z:
        df[i] = pd.to_numeric(df[i], downcast="float")
    df['time']=(pd.to_datetime(df['time'],unit='ms'))
    df = df.set_index(df['time'])
    return df

def apply_indicators(df : pd.DataFrame) -> pd.DataFrame:
    df['5MA'] = df['close'].rolling(5).mean()
    df['7MA'] = df['close'].rolling(7).mean()
    return df.dropna()

def get_results(history : list, name : str) -> dict:
    hist = pd.DataFrame.from_dict(history)
    wins = 0
    for i in hist['pnl']:
        if i > 0:
            wins += 1
    return {"name" : name, "cumulative" : hist.pnl.sum(), "winrate": wins/len(hist)}
# ===================== Backtest starts here =====================


tickers = ["ETHUSDT", "AVAXUSDT"]
timeframes = ["15m", "30m", "1h"]
for t in timeframes: # iterating through timeframes
    for n in tickers: # iterating through tickers
        df = get_binance_data(ticker = n, timeframe = t, period = 30)
        df = apply_indicators(df)
        agent = asset(name = f"{n}{t}", amount = 1000/float(df.close[0]))
        history = []
        for i in range(len(df)):
            for _ in range(2):
                long = df['5MA'][i] > df['7MA'][i]
                short = df['7MA'][i] > df['5MA'][i]

                if long and agent.inNoPosition():
                    agent.openLongPosition(openPrice=df['close'][i], openTime=df.index[i])

                if short and agent.inLongPosition():
                    res = agent.closePosition(closeprice=df['close'][i])
                    history.append({"time" : df.index[i], "type" : "long", "pnl" : res, "size" : agent.amount})

                if short and agent.inNoPosition():
                    agent.openShortPosition(openPrice=df['close'][i], openTime=df.index[i])

                if long and agent.inShortPosition():
                    res = agent.closePosition(closeprice=df['close'][i])
                    history.append({"time" : df.index[i], "type" : "short", "pnl" : res, "size" : agent.amount})
        trades = pd.DataFrame.from_dict(history)
        #print(trades)
        print(get_results(history, f"{n}{t}"))