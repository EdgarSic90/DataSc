import talib
import pandas as pd
def getIndicatorIndexed(df : pd.DataFrame):
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