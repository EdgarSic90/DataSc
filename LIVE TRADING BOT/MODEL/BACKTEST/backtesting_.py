import talib
import pandas as pd
import numpy as np
from binance import Client
import datetime
from assetClass import asset
import pickle

mlp = pickle.load(open('mlp.sav', 'rb'))

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
    df['volMa2'] = df['volume'].ewm(4).mean()
    df['volMa3'] = df['volume'].ewm(5).mean()
    df = df.dropna()
    df['volFeature'] = (df['volMa2'] - df['volMa3'])/df['volMa2']

    # defining MA
    df['ewm3'] = df['close'].ewm(3).mean()
    df['5ma'] = df['ewm3'].rolling(5).mean()
    df['20ma'] = df['ewm3'].rolling(20).mean()
    df = df.dropna()

    # use this
    df['5maFeature'] = (df['5ma'] - df['ewm3'])/df['ewm3']
    df['20maFeature'] = (df['20ma'] - df['ewm3'])/df['ewm3']

    # Bollinger Bands and Standard Deviation Percentaged
    df['std'] = df['close'].rolling(20).std()
    df['std1'] = df['close'].rolling(40).std()
    df['upper'] = df['20ma'] + 2*df['std']
    df['lower'] = df['20ma'] - 2*df['std']
    df['disFromLower'] = df['close'] - df['lower']
    df['gap'] = df['upper'] - df['lower']
    df = df.dropna()
    df['stdpct'] = (df['std'] - df['ewm3'])/df['ewm3']
    df['bbFeature'] = df['disFromLower']/df['gap']

    # talib indicators
    df['rsi'] = talib.RSI(df['ewm3'], timeperiod=14)/100
    df['rocp'] = talib.ROCP(df['ewm3'], timeperiod=10)
    return df.dropna()

def get_results(hist : pd.DataFrame, name : str, losses : list) -> dict:
    wins = (hist['pnl'] > 0).sum()
    longs = (hist['type'] == "long").sum()
    shorts = (hist['type'] == "short").sum()
    avg = round(hist['pnl'].mean(), 4)
    biggest_win = round(hist['pnl'].max(), 4)
    biggest_loss = round(hist['pnl'].min(), 4)
    winmean = round(hist.loc[hist['pnl'] > 0]['pnl'].mean(), 4)
    losemean = round(hist.loc[hist['pnl'] < 0]['pnl'].mean(), 4)
    cumulative = round((hist['pnl'] * hist['size'] * hist['openprice']).sum(), 4)
    return  {"name" : name, "cumulative USD returns" : cumulative,
             "pure percentage gain" : round(hist.pnl.sum(), 4) ,"winrate": round(wins/len(hist), 4),
             "number of trades" : len(hist.pnl), "longs": longs, "shorts": shorts,
             "average" : avg, "biggest win" : biggest_win, "biggest loss" : biggest_loss,
             "winmean": winmean, "losemean" : losemean, "expentancy" : round(winmean/abs(losemean), 4),
             "Consecutive loss" : max(losses)}

def plot_history(ohlc : pd.DataFrame, history : pd.DataFrame = None, metrics : dict = {}, label : str = "", starting_budget : float = 0) -> None:
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # create your figure object
    fig = make_subplots(rows=4, cols=1, row_heights=[0.1, 0.4, 0.4, 0.1],
                        subplot_titles=("Expected Return Metrics", "Historical Trades", "Cumulative PNL"))

    # label your figure
    fig.update_layout(height = 2000, title_text = f'Plot of {label} historical trades')
    fig.update_xaxes(rangeslider_visible=False)

    # add traces like ohlc, psar
    fig.add_trace(go.Candlestick(x = ohlc.index, open = ohlc.open, high = ohlc.high, low = ohlc.low, close = ohlc.close), row = 2, col = 1)
    # fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['PSAR'], mode = "markers", line=dict(color="#000000"), opacity=0.8), row = 2, col = 1)

    #showing metrics
    if metrics != {}:
        h = []
        v = []
        for i in metrics:
            h.append(i)
            v.append(metrics[f'{i}'])

        fig.add_trace(go.Table(header=dict(values=h), cells=dict(values=v)))

    #adding rectangles
    if history.empty != True:
        for i in range(len(history)):
            if history.type[i] == "short":
                color = "red"
            else:
                color = "green"
            fig.add_shape(type="rect",
                    x0=history.closetime[i], y0=history.openprice[i], x1=history.closetime[i], y1=history.closeprice[i],
                    line=dict(color=color, width=2,),fillcolor=color,opacity=0.2,)
    #show cumulative portfolio

    portfolio = (history['pnl'] * history['size'] * history['openprice']).cumsum() + starting_budget
    fig.add_trace(go.Scatter(x=history.closetime, y=portfolio), row = 3, col = 1)
    fig.show()
    return



# ===================== Backtest starts here =====================

if __name__ == "__main__":
    tickers = ["GMTUSDT", "AVAXUSDT", "ALGOUSDT", "ATOMUSDT", "MATICUSDT", "ATOMUSDT", "CHZUSDT", "APEUSDT"]#, "XMRUSDT", "SUSHIUSDT"]
    timeframes = ["5m"]#, "30m", "1h"]
    summary = pd.DataFrame()
    STARTING_BUDGET = 30
    for t in timeframes: # iterating through timeframes
        for n in tickers: # iterating through tickers
            df = get_binance_data(ticker = n, timeframe = t, period = 80)
            df = apply_indicators(df)
            agent = asset(name = f"{n}{t}", amount = STARTING_BUDGET/float(df.close[0]))
            agent.set_tp_sl(4.5, -1.5)
            history = []
            losses_history = []
            for i in range(len(df)):
                for _ in range(2):
                    input = df[['volFeature', '5maFeature', '20maFeature', 'rsi', 'rocp','bbFeature']].iloc[i].values
                    pred = mlp.predict([input])
                    long = pred == 1 #df['GR'][i] > 0 #df['close'][i] > df['PSAR'][i]
                    short = pred == 0 #df['GR'][i] < 0 #df['PSAR'][i] > df['close'][i]
                    current_price = df['close'][i]
                    current_high = df['high'][i]
                    current_low = df['low'][i]

                    if long and agent.inNoPosition():
                        agent.amount = STARTING_BUDGET/current_price
                        agent.openLongPosition(openPrice=df['close'][i], openTime=df.index[i])
                        agent.upper = agent.openPrice* (1 + agent.tp/100)
                        agent.lower = agent.openPrice* (1 + agent.sl/100)

                    if agent.inLongPosition():
                        if current_high > agent.upper or current_low < agent.lower: #current_price > agent.upper or current_price < agent.lower:
                            res = agent.closePosition(closeprice=df['close'][i])
                            if res > 0:
                                k = agent.tp/100
                            else:
                                k = agent.sl/100
                            res = res - abs(res*0.01) #assume commision of 1%
                            history.append( {"closetime" : df.index[i], "opentime" : agent.openTime,
                                            "openprice" : agent.openPrice, "closeprice" : current_price,
                                            "type" : "long", "pnl" : k, "size" : agent.get_tradeable_amount()})
                            if res < 0:
                                # agent.increase_tradeable_amount(2)
                                # agent.increase_tp_sl(1.2)
                                agent.consecutiveLoss += 1
                            else:
                                agent.reset_tp_sl()
                                agent.reset_tradable_amount()
                                losses_history.append(agent.consecutiveLoss)
                                agent.consecutiveLoss = 0

                    if short and agent.inNoPosition():
                        agent.amount = STARTING_BUDGET/current_price
                        agent.openShortPosition(openPrice=df['close'][i], openTime=df.index[i])
                        agent.upper = agent.openPrice* (1 - agent.sl/100)
                        agent.lower = agent.openPrice* (1 - agent.tp/100)

                    if agent.inShortPosition():
                        if current_high > agent.upper or current_low < agent.lower: #current_price < agent.lower or current_price > agent.upper:
                            res = agent.closePosition(closeprice=df['close'][i])
                            res = res - abs(res*0.01) #assume commision of 1%
                            if res > 0:
                                k = agent.tp/100
                            else:
                                k = agent.sl/100
                            history.append( {"closetime" : df.index[i], "opentime" : agent.openTime,
                                            "openprice" : agent.openPrice, "closeprice" : current_price,
                                            "type" : "short", "pnl" : k, "size" : agent.amount})
                            if res < 0:
                                # agent.increase_tradeable_amount(2)
                                # agent.increase_tp_sl(1.2)
                                agent.consecutiveLoss += 1
                            else:
                                agent.reset_tp_sl()
                                agent.reset_tradable_amount()
                                losses_history.append(agent.consecutiveLoss)
                                agent.consecutiveLoss = 0
            trades = pd.DataFrame.from_dict(history)
            print(trades)
            results = get_results(hist = trades, name = f"{n}{t}", losses = losses_history)
            plot_history(ohlc = df, history = trades, metrics = results, label = f"{n}{t}", starting_budget = STARTING_BUDGET)
            summary = summary.append(results, ignore_index=True)
    print(summary)