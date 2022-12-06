#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 4 15:51:58 2022

@author: edgarsicat
"""
import pandas as pd
from Webscrap import Wscrap
from Credentials import Credentials


############### Defining company names for Linkedin & Yahoo webscrapping ####################

companies_linkedin = ['microsoft', 'salesforce', 'bouygues-construction', 'bnp-paribas', 'hsbc', 'dataiku'] 
tickers = ['MSFT', 'CRM', 'BOUYY', 'BNPQY', 'HSBC', 'dataiku'] 


if __name__ == '__main__':
    
    print('Initiating Webscrapping ...')
        # Instanciating linkedin creadentials & chrome driver 
    creds = Credentials()
    ws = Wscrap(creds.email, creds.password)
    ws.Webdriver_instance("https://linkedin.com/uas/login")
        # Defining variables for our dataset
    Company_info_dict = {}
    Name = []
    Sector = []
    Adress = []
    Website = []
    Social_media = []
    Number_of_employees = []
    Revenue = []
    Latitude = []
    Longitude = []
    
        # Looping through compagnies
    for i in range(len(companies_linkedin)):
        
            # Linkedin scrapping
        linkedin_info = ws.Linkedin_company_webscrapping(companies_linkedin[i])
        Name.append(linkedin_info[0])
        Sector.append(linkedin_info[1])
        Adress.append(linkedin_info[2])
        Website.append(linkedin_info[3])
        Number_of_employees.append(linkedin_info[4])
            
            # Yahoo profile scrapping
        #nb_employees_ = ws.Yahoo_profile_webscrapping(tickers[i])
        #Number_of_employees.append(nb_employees_)
            
            # Yahoo quotes scrapping
        Revenue_ = ws.Yahoo_quotes_webscrapping(tickers[i])
        Revenue.append(Revenue_)
        
            # Social media links scrapping
        s_m = ws.collect_social_media_links(linkedin_info[3])
        Social_media.append(s_m)
        
            # Retrieving coordinates from scrapped adresses
        Localisation = ws.Coordinate_for_city(linkedin_info[2])
        Latitude.append(Localisation[0])
        Longitude.append(Localisation[1])
     
        # Filling the dictionary
    Company_info_dict['Name'] = Name
    Company_info_dict['Sector'] = Sector
    Company_info_dict['Adress'] = Adress
    Company_info_dict['Website'] = Website
    Company_info_dict['Social_media'] = Social_media
    Company_info_dict['Number_of_employees'] = Number_of_employees
    Company_info_dict['Revenue'] = Revenue
    Company_info_dict['Latitude'] = Latitude
    Company_info_dict['Longitude'] = Longitude
    
        # Exporting
    df_info = pd.DataFrame.from_dict(Company_info_dict)
    df_info.to_csv('Companies_info.csv', index=False, sep ='\t')
    print('New csv Companies_info.csv created')
        # Closing instance
    ws.close_driver()
    print('The show is done !')
    
    
    
    
    
    
    
    
    
    
    