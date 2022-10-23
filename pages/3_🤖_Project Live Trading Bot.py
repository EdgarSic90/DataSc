#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:34:16 2022

@author: edgarsicat
"""

import streamlit as st
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image

st.title('Live Trading Bot')

st.write("""
         In this project I've create a robust live trading model placing orders with FTX broker API.
         A telegram bot for 24/7 (alert and general wallet information as been implemented.
         You'll find the code on this [github repository](https://github.com/EdgarSic90/DataSc/tree/master/LIVE%20TRADING%20BOT), the current strategy was to predict 5 min candles
         with mutiple features and make trading decisions from it. 
         To evaluate the strategy & selection of assets a python Backtesting script has been developped as well.
         """)
st.write("You can see below a plot of an asset Backtested with a few performance metrics")

container = st.container()

image = Image.open('Back-Testing-Trading-Bot.png')
st.image(image, caption='Backtest of live trading bot')
