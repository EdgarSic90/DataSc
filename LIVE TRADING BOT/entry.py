import pandas as pd

def makeEntry(csvfile : str, type : str, asset : str, opentime, openprice : float, closetime, closeprice : float, size, pnl : float):
    assert ".csv" in csvfile, "file has to be a csv file"
    assert type in ["long", "short"], "type has to be long or short"
    log = pd.read_csv(csvfile)
    data = {'Pair': asset,
            'Timebuy': opentime,
            'TimeSell': closetime,
            'Length' : closetime-opentime,
            'Entryprice': openprice,
            'Exitprice': closeprice,
            'Return': pnl,
            'Position': type,
            'Size' : size}
    log = log.append(data, ignore_index=True)
    log.to_csv(csvfile, index = False)
    print("Stored new log")
    return True
