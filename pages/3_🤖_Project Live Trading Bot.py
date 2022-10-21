#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:34:16 2022

@author: edgarsicat
"""

import streamlit as st
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

st.title('Live Trading Bot')

container = st.container()

img = mpimg.imread('Back-Testing-Trading-Bot.png')
container.write(plt.imshow(img))
