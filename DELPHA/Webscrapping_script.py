#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 4 15:51:58 2022

@author: edgarsicat
"""


import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_page(ticker):
    """Download a webpage and return a beautiful soup doc"""
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
    response = requests.get(f'http://finance.yahoo.com/quote/{ticker}/profile?p={ticker}',headers= headers)
    if not response.ok:
        print('Status code:', response.status_code)
        raise Exception('Failed to load page {}'.format(ticker))
    page_content = response.text
    doc = BeautifulSoup(page_content, 'html.parser')
    return doc

def convert_to_numeric(column):
    first_col = [i.replace(',','') for i in column]
    second_col = [i.replace('-','') for i in first_col]
    final_col = pd.to_numeric(second_col)
    
    return final_col



###########  Creating a webdriver instance #########################

driver = webdriver.Chrome(ChromeDriverManager().install())
# This instance will be used to log into LinkedIn
 
# Opening linkedIn's login page
driver.get("https://linkedin.com/uas/login")
 
# waiting for the page to load
time.sleep(3)
 
# entering username
username = driver.find_element_by_id("username")
 
# In case of an error, try changing the element
# tag used here.
 
# Enter Your Email Address
username.send_keys("YOUR EAMIL HERE") 
 
# entering password
pword = driver.find_element_by_id("password")
# In case of an error, try changing the element
# tag used here.
 
# Enter Your Password
pword.send_keys("YOUR PASSWOARD HERE")       
 
# Clicking on the log in button
# Format (syntax) of writing XPath -->
# //tagname[@attribute='value']
driver.find_element_by_xpath("//button[@type='submit']").click()


############### Defining company names for Linkedin & Yahoo webscrapping ####################

companies_linkedin = ['microsoft', 'salesforce', 'bouygues-construction', 'bnp-paribas', 'hsbc', 'dataiku']
tickers = ['MSFT', 'CRM', 'BOUYY', 'BNPQY', 'HSBC', 'dataiku']


############### LINKEDIN WEBSCRAPPING ############################

dict_company_info = {}
name = []
Sector = []
adress = []
Website = []
Number_of_employees = []

for company in companies_linkedin:

    driver.get(f'https://www.linkedin.com/company/{company}/about') 
    start = time.time()
 
    # will be used in the while loop
    initialScroll = 0
    finalScroll = 1000

    while True:
        driver.execute_script(f'window.scrollTo({initialScroll},{finalScroll})')
        # this command scrolls the window starting from
        # the pixel value stored in the initialScroll
        # variable to the pixel value stored at the
        # finalScroll variable
        initialScroll = finalScroll
        finalScroll += 1000

        # we will stop the script for 3 seconds so that
        # the data can load
        time.sleep(1)
        # You can change it as per your needs and internet speed

        end = time.time()

        # We will scroll for 20 seconds.
        # You can change it as per your needs and internet speed
        if round(end - start) > 5:
            break
            
    src = driver.page_source
     
    # Now using beautiful soup
    soup = BeautifulSoup(src, 'xml') 
    
    # Finding The first header to collect Company names
    intro_company = soup.find('div', {'class': 'block mt2'})
    name_loc = intro_company.find("h1")
    name.append(name_loc.get_text().strip())
    dict_company_info['name'] = name
    
    # Creating a list comprehension to rextract the first part of this section -> The website link
    Web_ = [item.get_text(strip=True) for item in soup.find_all(class_="mb4 text-body-small t-black--light")]
    Website.append(Web_[0])
    dict_company_info['Website'] = Website
    
    if company == 'dataiku': # Creating manual correction for dataiku
        Sector_Adress = [item.get_text(strip=True) for item in soup.find_all(class_="org-top-card-summary-info-list__info-item")]
        Sector.append(Sector_Adress[0])
        adress.append(Sector_Adress[2])
        dict_company_info['Sector'] = Sector
        dict_company_info['adress'] = adress
    else:
        # List comprehension to get Sector and Adress 
        Sector_Adress = [item.get_text(strip=True) for item in soup.find_all(class_="org-top-card-summary-info-list__info-item")]
        Sector.append(Sector_Adress[0])
        adress.append(Sector_Adress[1])
        dict_company_info['Sector'] = Sector
        dict_company_info['adress'] = adress

for ticker in tickers:
    if ticker == 'dataiku':
        Number_of_employees.append(1000) 
        dict_company_info['Number_of_employees'] = Number_of_employees
    else:
        doc = get_page(ticker)
        Profile_info = [item.get_text(strip=True) for item in doc.find_all(class_="Fw(600)")]
        Number_of_employees.append(Profile_info[-1])
        dict_company_info['Number_of_employees'] = Number_of_employees

    
######################## Yahoo Finance web scrapping ##################################

Revenue = []
for ticker in tickers:
    if ticker == 'dataiku':
        Revenue.append(0)
        dict_company_info['Renevue'] = Revenue
    else:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        r = requests.get(f'https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}' ,headers=headers)
        soup = BeautifulSoup(r.content,'lxml')
        features = soup.find_all('div', class_='D(tbr)')
        headers = []
        temp_list = []
        label_list = []
        final = []
        index = 0
        #create headers
        for item in features[0].find_all('div', class_='D(ib)'):
            headers.append(item.text)
        #statement contents
        while index <= len(features)-1:
            #filter for each line of the statement
            temp = features[index].find_all('div', class_='D(tbc)')
            for line in temp:
                #each item adding to a temporary list
                temp_list.append(line.text)
            #temp_list added to final list
            final.append(temp_list)
            #clear temp_list
            temp_list = []
            index+=1
        df = pd.DataFrame(final[1:])
        df.columns = headers
        for column in headers[1:]:
            df[column] = convert_to_numeric(df[column])
            final_df = df.fillna('-')
        temp = final_df.iloc[:1].values
        Revenue.append(temp[0][1])
        dict_company_info['Renevue'] = Revenue


################## Retreiving Coordinates from scrapped City adresses ###################

Latitude = []
Longitude = []
from geopy.geocoders import Nominatim
for adress in dict_company_info['adress']:
    ad = adress.replace('cedex', '')
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(ad)
    Latitude.append(location.latitude)
    Longitude.append(location.longitude)
     
dict_company_info['Latitude'] = Latitude
dict_company_info['Longitude'] = Longitude

############## dict_company_info is completted now exporting to csv #####################


df_info = pd.DataFrame.from_dict(dict_company_info)
df_info.to_csv('Companies_info.csv', index=False, sep ='\t')

driver.close()




