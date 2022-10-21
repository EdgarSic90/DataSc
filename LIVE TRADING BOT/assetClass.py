from datetime import datetime
import sigfig
import pickle
class asset:

    def __init__(self, name: str, tp : float, sl : float, amount: float = 0):
        self.name = name
        self.amount = amount
        self.position = 0 #whereby 0 > none, 1 > long, -1 > short
        self.openPrice = None
        self.openTime = datetime.now()
        self.model = None
        self.stopTime = ""
        self.triggerID = ""
        self.tradeamt = amount
        self.martingaletrade = 0 #whereby 1 is a won trade, -1 is a lost trade
        self.tp = tp
        self.sl = sl
        self.tp_initial = None
        self.sl_initial = None
        self.consecutiveLoss = 0

    def get_tradable_tp(self) -> float:
        return self.tp

    def get_tradable_sl(self) -> float:
        return self.sl

    def initialise_tp_sl(self, tp : float, sl : float) -> None:
        self.tp = tp
        self.sl = sl
        self.tp_initial = tp
        self.sl_initial = sl

    def set_tp_sl(self, tp : float, sl : float) -> None:
        self.tp = tp
        self.sl = sl
        return

    def reset_tp_sl(self) -> None:
        self.tp = self.tp_initial
        self.sl = self.sl_initial
        return

    def increase_tp_sl(self, factor : float) -> None:
        self.tp = self.tp + factor
        self.sl = self.sl - factor
        return

    def detect_tp_from_server(self) -> None:
        placeholder = self.get_tradeable_amount()
        multiplier = 0
        while(placeholder > self.amount):
            placeholder /= 2.25
            print(placeholder)
            multiplier += 1
        self.set_tp_sl(self.tp_initial + 0.2*multiplier, self.sl_initial + -0.2*multiplier)

    def loadModel(self, directory: str) -> None:
        assert ".sav" in directory, "must be pickle file"
        self.model = pickle.load(open(directory, 'rb'))
        print(f'{directory} has been loaded as a {self.model}')
        return

    def openLongPosition(self, openPrice, openTime) -> None:
        self.position = 1
        self.openPrice = openPrice
        self.openTime = openTime
        print(f"Opened LONG position on {self.name}\n{self.openPrice}\n{self.openTime}")
        return

    def openShortPosition(self, openPrice, openTime) -> None:
        self.position = -1
        self.openPrice = openPrice
        self.openTime = openTime
        print(f"Opened SHORT position on {self.name}\n{self.openPrice}\n{self.openTime}")
        return

    def closePosition(self) -> None:
        self.position = 0
        return

    def inPosition(self) -> bool:
        return self.position != 0

    def inLongPosition(self) -> bool:
        return self.position == 1

    def inShortPosition(self) -> bool:
        return self.position == -1

    def inNoPosition(self) -> bool:
        return self.position == 0

    def get_tradeable_amount(self) -> float:
        return self.tradeamt

    def determine_tradeable_amount(self, usd_amount, asset_price) -> bool:
        t = sigfig.round((usd_amount / asset_price), 2)
        if self.inNoPosition():
            self.amount = t
            self.tradeamt = t
            print(f"Re-Calibrated {self.name} amount to {self.amount}")
            return True
        else:
            print(f"No Re-Calibration on {self.name}")
            return False
    
    def increase_tradeable_amount(self, factor : float) -> bool:
        self.tradeamt = self.tradeamt * factor
        return True
    
    def reset_tradable_amount(self) -> bool:
        self.tradeamt = self.amount
        return True

    def set_initial_position(self, size : float, side : str, entry_price : float) -> bool:
        if side == 'none':
            return
        self.tradeamt = size
        if side == 'buy':
            self.openLongPosition(openPrice=entry_price, openTime=datetime.now())
        elif side == 'sell':
            self.openShortPosition(openPrice=entry_price, openTime=datetime.now())
        return True

    def describe(self):
        print(f"\nName : {self.name}")
        print(f"Position : {self.position}")
        print(f"Open Price : {self.openPrice}")
        print(f"Open Size : {self.tradeamt}")
        print(f"Open Time : {self.openTime}")
        print(f"TP, SL : {self.get_tradable_tp()} {self.get_tradable_sl()}")
        return