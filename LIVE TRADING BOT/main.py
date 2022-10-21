import time
from FTXapiV3 import FtxClient
from assetClass import asset
from dataprocessing import getIndicatorIndexed
from telebot import telegramBot
from entry import makeEntry
from datetime import datetime
from time import sleep
import pandas as pd
import pickle

bot = telegramBot(botToken='', chatID='')
USDAMOUNT = 15
logdir = "log.csv"
mlp = pickle.load(open('mlp.sav', 'rb'))

def scan(ticker: asset):
    resp = ftx.get_market_data(market=ticker.name, interval='15m') # Get 15 minute data
    if (resp.status_code in range(200,299)) and (resp.json()['success'] == True):
        df = ftx.parse_ftx_response(resp.json())
        currentPrice = df['close'][-1]
        ticker.determine_tradeable_amount(USDAMOUNT, currentPrice) # this recalibrates the position size if its in no position AND not on a loss streak
        df = getIndicatorIndexed(df)
        input = df[['volFeature', '5maFeature', '20maFeature', 'rsi', 'rocp','bbFeature']].iloc[-1].values
        pred = mlp.predict([input])
        uptrend = (pred == 1)
        downtrend = (pred == 0)

        #============UPTREND, LONG POSITIONS ONLY===================
        if uptrend and ticker.inNoPosition():
                resp = ftx.place_order(market=ticker.name, side='buy', price=None,
                                    size=str(ticker.get_tradeable_amount()), type='market')  # open long
                if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass # in this case, i decided to let the next iteration handle the re-order
                else:
                    ticker.openLongPosition(openPrice=df['close'][-1], openTime=datetime.now())
                    bot.sendText(f"Opened LONG on {ticker.name} for {ticker.tradeamt}")


        #============CONDITIONS TO CLOSE LONG POSITION===================
        if ticker.inLongPosition():
            pnl = ftx.get_position_details(ticker.name)['pctPnl']
            print("current pnl",pnl)
            print(f"""checking short pnl to tp sl:
                        ABSOLUTE PNL: {pnl}
                        SHORT PNL : {(-1)*pnl}
                        LONG WIN CONDITION : {pnl > ticker.tp}
                        LONG LOSE CONDITION : {pnl < ticker.sl}
                        TP LEVEL : {ticker.tp}
                        SL LEVEL : {ticker.sl}""")
            if pnl > ticker.get_tradable_tp():
                resp = ftx.place_order(market=ticker.name, side='sell', price=None,
                                size=float(ticker.get_tradeable_amount()), type='market')  # close long
                if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass
                else:
                    ticker.closePosition()
                    bot.sendText(f"{ticker.name}\nTrade WON\nPNL : {pnl}")
                    makeEntry(logdir, 'long', ticker.name, ticker.openTime, ticker.openPrice, datetime.now(), df['close'][-1], ticker.get_tradeable_amount(), pnl)

            elif pnl < ticker.get_tradable_sl():
                resp = ftx.place_order(market=ticker.name, side='sell', price=None,
                                size=float(ticker.get_tradeable_amount()), type='market')  # close long
                if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass
                else:
                    ticker.closePosition()
                    makeEntry(logdir, 'long', ticker.name, ticker.openTime, ticker.openPrice, datetime.now(), df['close'][-1], ticker.get_tradeable_amount(), pnl)
                    bot.sendText(f"{ticker.name}\nTrade LOST\nPNL : {pnl}")

        #============DOWNTREND, SHORT POSITIONS ONLY===================
        if downtrend and ticker.inNoPosition():
            resp = ftx.place_order(market=ticker.name, side='sell', price=None,
                                size=float(ticker.get_tradeable_amount()), type='market')  # open short
            if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass
            else:
                ticker.openShortPosition(openPrice=df['close'][-1], openTime=datetime.now())
                print(ticker.tp, ticker.sl, currentPrice)
                bot.sendText(f"Opened SHORT on {ticker.name} ofor {ticker.get_tradeable_amount()}")


        #============CONDITIONS TO CLOSE SHORT POSITIONS===================
        if ticker.inShortPosition():
            pnl = ftx.get_position_details(ticker.name)['pctPnl']
            print("current pnl",pnl)
            print(f"""checking short pnl to tp sl:
                        ABSOLUTE PNL: {pnl}
                        SHORT PNL : {(-1)*pnl}
                        SHORT WIN CONDITION : {(-1)*pnl > ticker.tp}
                        SHORT LOSE CONDITION : {(-1)*pnl < ticker.sl}
                        TP LEVEL: {ticker.tp}
                        SL LEVEL : {ticker.sl}""")
            if (-1)*pnl > ticker.get_tradable_tp():
                resp = ftx.place_order(market=ticker.name, side='buy', price=None,
                                size=float(ticker.get_tradeable_amount()), type='market')  # close short
                if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass
                else:
                    ticker.closePosition()
                    bot.sendText(f"{ticker.name}\nTrade WON\nPNL : {(-1)*pnl}")
                    makeEntry(logdir, 'short', ticker.name, ticker.openTime, ticker.openPrice, datetime.now(), df['close'][-1], ticker.get_tradeable_amount(), (-1)*pnl )
            elif (-1)*pnl < ticker.get_tradable_sl():
                print('line 133')
                resp = ftx.place_order(market=ticker.name, side='buy', price=None,
                                size=float(ticker.get_tradeable_amount()), type='market')  # close short
                if resp.status_code not in range(200,299) or resp.json()['success'] != True:
                    pass
                else:
                    ticker.closePosition()
                    makeEntry(logdir, 'short', ticker.name, ticker.openTime, ticker.openPrice, datetime.now(), df['close'][-1], ticker.get_tradeable_amount(), (-1)*pnl)
                    bot.sendText(f"{ticker.name}\nTrade LOST\nPNL : {(-1)*pnl}")
    return ticker


if __name__ == '__main__':

    bot.sendText("Bot initialized!")

    # =================================Initialise FTX Client=================================
    ftx = FtxClient(api_key="",
            api_secret="")

    ltc = asset(name='LTC-PERP', tp = 2.2, sl=-1.1)

    matic = asset(name='MATIC-PERP', tp = 2.2, sl=-1.1)

    atom = asset(name='APE-PERP', tp = 2.2, sl=-1.1)

    # =================================Place Assets in Array to loop through=================================

    tickers = [ltc ,matic ,atom] #'''[avax, eth, ada, sol, snx ,ftt ,flow ,btc ,xrp ,algo ,'''
    for i in range(len(tickers)):
        r = ftx.get_position_details(ticker = tickers[i].name)
        print(r['size'], r['entryPrice'])
        tickers[i].set_initial_position(size = r['size'], side = r['side'], entry_price = r['entryPrice'])

    initialtime = datetime.now().replace(microsecond=0, second=0, minute=0)

    while True:
        for i in range(len(tickers)):

            # =================================Scan Function and Debugging Statement=================================
            # try:
            tickers[i] = scan(tickers[i])
            tickers[i].describe()
            # except:
            #     print("api overcalled, trying again")
            currenttime = datetime.now().replace(microsecond=0, second=0, minute=0)
            # =================================Reactions to Commands=================================
            if currenttime > initialtime:
                message = f"As of {currenttime}\n\n"
                message += f"ticker : position : openPrice : size"
                for t in tickers:
                    message += f"{t.name} : {t.position} : {t.openPrice} : {t.get_tradeable_amount()}\n\n"
                bot.sendText(message)
                initialtime = currenttime
            time.sleep(2)

