#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 4 15:51:58 2022

@author: edgarsicat
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Web-Scrapping challenge for Delpha!')
st.write("For this challenge I have scrapped data from Linkedin & Yahoo Finance in order to populate a csv file with various informations.")
st.write("""
         In this [Github Repository](https://github.com/EdgarSic90/DataSc/tree/master/DELPHA) 
         you'll find the Web scrapping Python code full commented and and the csv file.
         """)
st.write("""
             In this [Github Repository](https://github.com/EdgarSic90/DataSc/tree/master/pages) 
             You'll find the code that allows for this Dashboard and app to be hosted ! (Feel free to explore my other projets & Homepage) 
         """)
st.write("Below is an interactive map with a few metrics to better grasp the dataset used")


@st.cache
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/EdgarSic90/DataSc/master/DELPHA/Companies_info.csv", index_col=False, delimiter='\t')
    
    return df

df = load_data()

@st.cache
def display_map():

    info = df[['Latitude', 'Longitude', 'name', 'Number_of_employees', 'Renevue']]
    fig = px.scatter_mapbox(info, lat='Latitude', lon='Longitude', hover_name='name', 
        hover_data=['Number_of_employees'], color='Renevue',
        zoom=1, height=350, width=750, size_max=50 , center={'lat' : 48.8588897, 'lon' : 2.3200410217200766})
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":1,"l":1,"b":1})
    return fig


container = st.container()

container.write(display_map())

df_display = container.checkbox("Display Dataframe", value=True)
if df_display:
    container.write(df)




