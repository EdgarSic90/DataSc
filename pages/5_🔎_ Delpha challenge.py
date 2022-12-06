#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 4 15:51:58 2022

@author: edgarsicat
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.title('🔍Web-Scrapping challenge for Delpha!🔎')
st.write("For this challenge I have scrapped data from Linkedin & Yahoo Finance in order to populate a csv file with various informations.")
st.write("""
         In this [Github Repository](https://github.com/EdgarSic90/DataSc/tree/master/DELPHA) 
         you'll find the Web scrapping Python code full commented and the csv file.
         """)
st.write("""
             In this [Github Repository](https://github.com/EdgarSic90/DataSc/tree/master/pages) 
             You'll find the code that allows for this Dashboard and app to be hosted ! (Feel free to explore my other projets & Homepage) 
         """)
st.write("Below is an interactive map with a few metrics to better grasp the dataset used & useful visualizations")


@st.cache
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/EdgarSic90/DataSc/master/DELPHA/Companies_info.csv", index_col=False, delimiter='\t')
    
    return df

df = load_data()
count_nan = sum(df.isnull().sum().values)
all_count_ = df.count().values
all_count = all_count_[0]*all_count_[1]
percent_missing = round((count_nan/all_count)*100, 2)

@st.cache
def display_map():

    info = df[['Latitude', 'Longitude', 'Name', 'Number_of_employees', 'Revenue']]
    fig = px.scatter_mapbox(info, lat='Latitude', lon='Longitude', hover_name='Name', 
        hover_data=['Number_of_employees'],
        zoom=2, height=350, width=750, size_max=50 , center={'lat' : 48.8588897, 'lon' : 2.3200410217200766})
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":1,"l":1,"b":1})
    return fig


container = st.container()

container.write(display_map())


df_display = container.checkbox("Click to display scrapped data", value=True)
if df_display:
    container.write(df)
    
col1, col2, = st.columns(2)

col1.bar_chart(df, x="Name", y="Number_of_employees")

col2.bar_chart(df, x="Name", y="Revenue")

container2 = st.container()

#container2.subheader(f"{percent_missing}% of missing data")

container2.markdown(f"<h4 style='text-align: center;'>{percent_missing}% of missing data</h4>", unsafe_allow_html=True)



