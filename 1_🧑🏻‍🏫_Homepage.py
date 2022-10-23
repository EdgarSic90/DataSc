#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 12:37:51 2022

@author: edgarsicat
"""

import streamlit as st
import requests
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋"
    )

st.sidebar.success("Select a page above.")
st.sidebar.write('💻 Find the code on [Github](https://github.com/EdgarSic90/DataSc)')
st.sidebar.write('💬 Contact me on [Linkedin](https://linkedin.com/in/edgar-sicat)')

def lad_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Use local CSS
def local_css(file_name):
    with open(file_name) as f: st.markdown (f" <style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")



    
#---- LOAD ASSETS -----

lottie_coding = lad_lottieurl("https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ----HEADER SECTION---------
with st.container():
    st.subheader("Hi, I am Edgar :wave:")
    st.write("This is a platform presenting some of my projects !")
    st.write("Feel free to explore the code on my [Github](https://github.com/EdgarSic90/DataSc)")
    st.write("Open for opportunities >[Linkedin](https://linkedin.com/in/edgar-sicat)")


#---------WHAT I DO -------
with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown("_Data science & Machine learning deserve to be shared with others_")
        st.write("##")
        st.write("""
                 
                 What you'll find 
                 - Interactive dashboards & visualizations
                 - Modeling & testing on github 
                 - Various EDA on github
                 
                 """)


#if 'my_input' not in st.session_state:
#    st.session_state["my_input"] = ""
    
#my_input = st.text_input("Input a text here", st.session_state["my_input"])
#submit = st.button("Submit")
#if submit:
#    st.session_state["my_input"] = my_input
#    st.write("You have entered: ", my_input)
    
    with right_column:
        st_lottie(lottie_coding, height=300)
        

# ---- CONTACT ------

with st.container():
    st.write("---")
    st.header("Get In Touch With Me!")
    st.write("##")
    
# Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
    contact_form = """
    <form action="https://formsubmit.co/edgar.sicat93@gmail.com" method="POST"> 
        <input type="hidden" name="_captcha" value="false"
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here" required></textarea>
        <button type="submit">Send</button>
    </form>
    """
    
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown(contact_form, unsafe_allow_html=True)
    with right_column:
        st.empty()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    