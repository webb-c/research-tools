#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
This modified code searches for papers that cite a given paper by its title on Google Scholar, sorts the citing papers by the number of citations, and optionally exports the results to a .csv file.
"""

import requests
import os
import datetime
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep
import random
import sys
import warnings
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Solve conflict between raw_input and input on Python 2 and Python 3
if sys.version[0] == "3": raw_input = input

# Default Parameters
KEYWORD = ''  # Default is empty; requires a paper title for citation search
NRESULTS = 100
CSVPATH = os.getcwd()
SAVECSV = True
SORTBY = 'Citations'
PLOT_RESULTS = False
STARTYEAR = None
now = datetime.datetime.now()
ENDYEAR = now.year
DEBUG = False
MAX_CSV_FNAME = 255

# Websession Parameters
GSCHOLAR_URL = 'https://scholar.google.com/scholar?start={}&cites={}&hl=en&&as_sdt=2005&sciodt=0,5'
STARTYEAR_URL = '&as_ylo={}'
ENDYEAR_URL = '&as_yhi={}'

ROBOT_KW = ['unusual traffic from your computer network', 'not a robot', 'grecaptcha']


def get_command_line_args():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('--title', type=str, help="Title of the paper to get citation list for.")
    parser.add_argument('--sortby', type=str, help='Column to be sorted by. Default is by the columns "Citations", i.e., it will be sorted by the number of citations. If you want to sort by citations per year, use --sortby "cit/year"')
    
    parser.add_argument('--nresults', type=int, default=NRESULTS, help='Number of articles to fetch.')
    parser.add_argument('--csvpath', type=str, help='Path to save the exported csv file.')
    parser.add_argument('--notsavecsv', action='store_true', help='If selected, the results will not be saved as a csv file.')
    parser.add_argument('--plotresults', action='store_true', help='Flag to plot results with rank vs citation count.')
    parser.add_argument('--startyear', type=int, default=STARTYEAR, help='Start year for the search.')
    parser.add_argument('--endyear', type=int, default=ENDYEAR, help='End year for the search.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for testing.')

    args = parser.parse_args()
    return args

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_content_with_selenium(url):
    driver = setup_driver()
    driver.get(url)

    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        el = driver.find_element(By.TAG_NAME, "body")
        content = el.get_attribute('innerHTML')
        if any(kw in el.text for kw in ROBOT_KW):
            raw_input("Solve captcha manually and press enter here to continue...")
        else:
            break

    return content.encode('utf-8')

def get_paper_id(title):

    encoded_title = title.replace(" ", "+")
    search_url = f"https://scholar.google.com/scholar?q={encoded_title}"
    content = get_content_with_selenium(search_url)

    # print(url)
    if any(kw in content.decode('ISO-8859-1') for kw in ROBOT_KW):
        print("Robot checking detected, handling with selenium (if installed)")
        try:
            content = get_content_with_selenium(search_url)
        except Exception as e:
            print("No success. The following error was raised:")
            print(e)
    
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
    
    try:
        citation_link = soup.find("a", href=lambda x: x and "cites=" in x)['href']
        citation_id = citation_link.split("cites=")[-1].split("&")[0]
    except Exception as e:
        print("Error:", e)
        print("Search URL:", search_url)
        print("Contents: ", content)
    
    return citation_id


def get_citations(content):
    out = 0
    for char in range(0, len(content)):
        if content[char:char + 9] == 'Cited by ':
            init = char + 9
            for end in range(init + 1, init + 6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)


def get_year(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[char-5:char-1]
    if not out.isdigit():
        out = 0
    return int(out)

def get_author(content):
    content = content.replace('\xa0', ' ')  # Replaces the non-breaking space with a regular space
    if len(content)>0:
        out = content.split(" - ")[0]
    return out


def main():
    args = get_command_line_args()
    title = args.title
    number_of_results = args.nresults
    save_csv = not args.notsavecsv
    csvpath = args.csvpath
    plot_results = args.plotresults
    start_year = args.startyear
    end_year = args.endyear
    debug = args.debug
    sortby_column = args.sortby

    print(f"Searching for citations of: {title}")
    
    paper_id = get_paper_id(title)
    
    if start_year:
        GSCHOLAR_MAIN_URL = GSCHOLAR_URL + STARTYEAR_URL.format(start_year)
    else:
        GSCHOLAR_MAIN_URL = GSCHOLAR_URL

    if end_year != now.year:
        GSCHOLAR_MAIN_URL = GSCHOLAR_MAIN_URL + ENDYEAR_URL.format(end_year)
    
    session = requests.Session()

    links = []
    titles = []
    citations = []
    years = []
    authors = []
    venues = []
    publishers = []
    ranks = [0]

    for n in range(0, number_of_results, 10):
        print("Loading next {} results".format(n+10))
        
        # url = GSCHOLAR_MAIN_URL + f"&start={n}"
        url = GSCHOLAR_MAIN_URL.format(str(n), paper_id)
        page = session.get(url)
        c = page.content
        
        # print(url)
        if any(kw in c.decode('ISO-8859-1') for kw in ROBOT_KW):
            print("Robot checking detected, handling with selenium (if installed)")
            try:
                c = get_content_with_selenium(url)
            except Exception as e:
                print("No success. The following error was raised:")
                print(e)

        soup = BeautifulSoup(c, 'html.parser', from_encoding='utf-8')        
        
        mydivs = soup.findAll("div", {"class": "gs_or"})

        for div in mydivs:
            try:
                links.append(div.find('h3').find('a').get('href'))
            except: # catch *all* exceptions
                links.append('Look manually at: '+url)

            try:
                titles.append(div.find('h3').find('a').text)
            except:
                titles.append('Could not catch title')

            try:
                citations.append(get_citations(str(div.format_string)))
            except:
                warnings.warn("Number of citations not found for {}. Appending 0".format(title[-1]))
                citations.append(0)

            try:
                years.append(get_year(div.find('div',{'class' : 'gs_a'}).text))
            except:
                warnings.warn("Year not found for {}, appending 0".format(title[-1]))
                years.append(0)

            try:
                authors.append(get_author(div.find('div',{'class' : 'gs_a'}).text))
            except:
                authors.append("Author not found")

            try:
                publishers.append(div.find('div',{'class' : 'gs_a'}).text.split("-")[-1])
            except:
                publishers.append("Publisher not found")

            try:
                venues.append(" ".join(div.find('div',{'class' : 'gs_a'}).text.split("-")[-2].split(",")[:-1]))
            except:
                venues.append("Venue not fount")

            ranks.append(ranks[-1]+1)
        
        # Delay 
        sleep(random.uniform(0.5, 3))

    data = pd.DataFrame(list(zip(authors, titles, citations, years, publishers, venues, links)), index = ranks[1:],
                        columns=['Author', 'Title', 'Citations', 'Year', 'Publisher', 'Venue', 'Source'])
    data.index.name = 'Rank'

    data['cit/year'] = data['Citations'] / (end_year + 1 - data['Year'].clip(upper=end_year))
    data['cit/year']=data['cit/year'].round(0).astype(int)

    # Sort by the selected columns, if exists
    try:
        data_ranked = data.sort_values(by=sortby_column, ascending=False)
    except Exception as e:
        print('Column name to be sorted not found. Sorting by the number of citations...')
        data_ranked = data.sort_values(by='Citations', ascending=False)
        print(e)

    # Print data
    # print(data_ranked)

    if plot_results:
        plt.plot(data.index, data['Citations'], '*')
        plt.ylabel('Number of Citations')
        plt.xlabel('Rank')
        plt.title(f'Citations for papers citing "{title}"')
        plt.show()
    
    if save_csv:
        file_path = os.path.join(csvpath, title.replace(' ', '_').replace(':', '_') + '_citations.csv')
        data.to_csv(file_path, encoding='utf-8')
        print(f'Results saved to {file_path}')

if __name__ == '__main__':
    main()