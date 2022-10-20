#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 13:49:57 2022

@author: edgarsicat
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import pickle
from urllib.request import urlopen
import json
import plotly.express as px
import math 
import requests


st.title('House prediction in Perth Australia')


@st.cache
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/EdgarSic90/DataS/main/House_Prediction_FIles/all_perth_310121.csv")
    
    return df

df = load_data()

@st.cache
def load_data2():
     global __data_columns
     global __locations 
     url = 'https://raw.githubusercontent.com/EdgarSic90/DataS/main/House_Prediction_FIles/columns.json'
     f = requests.get(url)
     __data_columns = f.json()['data_columns']
     __locations = __data_columns[6:]
     return __locations

def load_data4():
     global __data_columns
     global __locations 
     url = 'https://raw.githubusercontent.com/EdgarSic90/DataS/main/House_Prediction_FIles/columns.json'
     f = requests.get(url)
     __data_columns = f.json()['data_columns']
     return __data_columns

def load_data3():       
     global __model
     with open("home_prices_model.pickle", 'rb') as f:
         __model = pickle.load(f)
         return __model
         

def predict_price(BEDROOMS,BATHROOMS,GARAGE,BUILD_YEAR_log,FLOOR_AREA_log, LAND_AREA_log, SUBURB):    
    loc_index = load_data4().index(SUBURB.lower())

    x = np.zeros(len(load_data4()))
    x[0] = float(BEDROOMS)
    x[1] = float(BATHROOMS)
    x[2] = float(GARAGE)
    x[3] = math.log(float(BUILD_YEAR_log))
    x[4] = math.log(float(FLOOR_AREA_log))
    x[5] = math.log(float(LAND_AREA_log))
        
    if loc_index >= 0:
        x[loc_index] = 1

    return math.exp(load_data3().predict([x])[0])

def display_map():

    info = df[['LATITUDE', 'LONGITUDE', 'PRICE', 'SUBURB', 'BUILD_YEAR']]
    fig = px.scatter_mapbox(info, lat='LATITUDE', lon='LONGITUDE', hover_name='SUBURB', 
        hover_data=['BUILD_YEAR'], color='PRICE',
        zoom=8, height=500, width=850)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":1,"l":1,"b":1})
    return fig



container = st.container()

container.write(display_map())

BEDROOMS = container.text_input("Number of bedroom")
BATHROOMS = container.text_input("Number of bathroom")
GARAGE = container.text_input("Number of garage space")
BUILD_YEAR_log = container.text_input("Year the house was built")
FLOOR_AREA_log = container.text_input("Floor area in square metres")
LAND_AREA_log = container.text_input("Land area in square metres")
SUBURB = container.selectbox('Select your suburb', load_data2())

prediction = 0

if container.button('Click here for your House Price Prediction in K$ !'):
    prediction = predict_price(BEDROOMS,BATHROOMS,GARAGE,BUILD_YEAR_log,FLOOR_AREA_log, LAND_AREA_log, SUBURB)

container.success(round(prediction/1000))




