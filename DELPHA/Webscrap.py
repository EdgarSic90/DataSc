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

class Wscrap:
    
    def __init__(self, LinkedinMail = str, LinkedinPassword = str):
        self.LinkedinMail = LinkedinMail
        self.LinkedinPassword = LinkedinPassword


    def get_page(self, ticker : str):
        """
        Download a webpage and return a beautiful soup doc
        """
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
        response = requests.get(f'http://finance.yahoo.com/quote/{ticker}/profile?p={ticker}',headers= headers)
        if not response.ok:
            print('Status code:', response.status_code)
            raise Exception('Failed to load page for {}'.format(ticker))
        page_content = response.text
        doc = BeautifulSoup(page_content, 'xml')
        return doc

    def convert_to_numeric(self, column : pd.DataFrame()):
        """
        Data processing for Yahoo finance quotes
        """
        first_col = [i.replace(',','') for i in column]
        second_col = [i.replace('-','') for i in first_col]
        final_col = pd.to_numeric(second_col)
        
        return final_col


    def Webdriver_instance(self, page : str, time_sleep = 3):
        """
        Creating a webdriver instance
        """
    
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # This instance will be used to log into LinkedIn
         
        # Opening linkedIn's login page
        #driver.get("https://linkedin.com/uas/login")
        self.driver.get(page)
         
        # waiting for the page to load
        time.sleep(time_sleep)
         
        # entering username
        username = self.driver.find_element_by_id("username")
         
        # In case of an error, try changing the element
        # tag used here.
         
        # Enter Your Email Address
        username.send_keys(self.LinkedinMail) 
         
        # entering password
        pword = self.driver.find_element_by_id("password")
        # In case of an error, try changing the element
        # tag used here.
         
        # Enter Your Password
        pword.send_keys(self.LinkedinPassword)       
         
        # Clicking on the log in button
        # Format (syntax) of writing XPath -->
        # //tagname[@attribute='value']
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        return 
    

    
    def Linkedin_company_webscrapping(self, company : str, time_sleep = 1, time_scrool = 5):
        """
        LINKEDIN WEBSCRAPPING
        """        
        self.name = None
        self.Sector = None
        self.adress = None
        self.Website = None
        
        self.driver.get(f'https://www.linkedin.com/company/{company}/about') 
        start = time.time()
        
        # will be used in the while loop
        initialScroll = 0
        finalScroll = 1000
        while True:
            self.driver.execute_script(f'window.scrollTo({initialScroll},{finalScroll})')
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
        
        src = self.driver.page_source
        # Now using beautiful soup
        self.soup = BeautifulSoup(src, 'xml') 
        
        # Finding The first header to collect Company names
        try:
            intro_company = self.soup.find('div', {'class': 'block mt2'})
            name_loc = intro_company.find("h1")
            self.name = name_loc.get_text().strip()
        except:
            self.name = np.NaN
            print(f'Unable to collect {company} name')

        # Creating a list comprehension to extract the first part of this section -> The website link
        try:
            Web_ = [item.get_text(strip=True) for item in self.soup.find_all(class_="mb4 text-body-small t-black--light")]
            self.Website = Web_[0]
        except:
            self.Website = np.NaN
            print(f'Unable to collect {company} website')

        # List comprehension to get Sector and Adress 
        try:
            Sector_Adress = [item.get_text(strip=True) for item in self.soup.find_all(class_="org-top-card-summary-info-list__info-item")]
            self.Sector = Sector_Adress[0]
            self.adress = Sector_Adress[-2]
        except:
            self.Sector = np.NaN
            self.adress = np.NaN
            print(f'Unable to collect {company} Sector & Adress')

        return [self.name, self.Sector, self.adress, self.Website]
            

    def Yahoo_profile_webscrapping(self, ticker : str):
        """
        YAHOO PROFILE WEBSCRAPPING
        """        
        self.Number_of_employees = None
        try:
            doc = self.get_page(ticker)
            Profile_info = [item.get_text(strip=True) for item in doc.find_all(class_="Fw(600)")]
            self.Number_of_employees = Profile_info[-1]
            self.Number_of_employees = int(self.Number_of_employees.replace(',',''))
        except:
            self.Number_of_employees = np.NaN
            print(f'Unable to collect {ticker} Number of employees')
            
        return self.Number_of_employees
    
    def Yahoo_quotes_webscrapping(self, ticker : str):
        """
        YAHOO QUOATE WEBSCRAPPING
        """      
        self.Revenue = None

        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        r = requests.get(f'https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}' ,headers=headers)
        soup = BeautifulSoup(r.content,'lxml')
        
        features = soup.find_all('div', class_='D(tbr)')
        headers = []
        temp_list = []
        label_list = []
        final = []
        index = 0
        try:
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
                df[column] = self.convert_to_numeric(df[column])
                final_df = df.fillna('-')
            temp = final_df.iloc[:1].values
            self.Revenue = temp[0][1]
        except:
            self.Revenue = np.NaN
            print(f'Unable to collect {ticker} Revenue')
            
        return self.Revenue


    def close_driver(self) -> None:
        """Closing driver"""
        self.driver.close()
        return
    
    def Coordinate_for_city(self, city : str):
        """
        Retreiving Coordinates from scrapped City adresses
        """ 
        self.Latitude = None
        self.Longitude = None
        from geopy.geocoders import Nominatim
        try:
            city_ = city.replace('cedex', '')
            geolocator = Nominatim(user_agent="Your_Name")
            location = geolocator.geocode(city_)
            self.Latitude = location.latitude
            self.Longitude = location.longitude
        except:
            self.Latitude = np.NaN
            self.Longitude = np.NaN
            print(f'Unable to collect {city} Coordinates')
        
        return [self.Latitude, self.Longitude]






