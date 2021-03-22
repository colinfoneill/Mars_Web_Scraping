#!/usr/bin/env python
# coding: utf-8
#import dependencies
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import requests
import time
import pandas as pd
import pymongo

def init_browser():
    # Setup splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path)

#define the function scrape
def scrape():
    #setup connection to mongoDB
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    # Select database and collection to use
    db = client.mars_db
    collection = db.mars

    # Create BeautifulSoup object; parse with 'html.parser'
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    
    #setup splinter
    browser = init_browser()
    browser.visit(url)
    time.sleep(3)
    soup = bs(browser.html, 'html.parser')

    #scrape the Mars website to get a specific article header and content
    result = soup.find_all('div', class_="content_title")
    news_title = result[1].text

    #scrape the article teaser from the result
    result_p = soup.find_all('div', class_="article_teaser_body")
    news_p = result_p[0].text


    # # JPL Mars Space Images - Featured Image

    #establish the base url and visit the url in browser
    base_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(base_url)


    #establish image soup
    html = browser.html
    image_soup = bs(html, 'html.parser')


    #get image_url
    image_relative = image_soup.find('img', class_='headerimage')['src']


    #append image url to base url to establish the entire featured_image_url
    base_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    featured_image_url = base_url + image_relative 


    # # Mars Facts


    #read the table into a pandas df
    facts_table = pd.read_html('https://space-facts.com/mars/')[0]
    facts_table


    #convert the table to an html object
    html_table = facts_table.to_html(index=False, header=False)


    # # Mars Hemispheres


    #establish path to url
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    #setup splinter
    browser.visit(url)
    time.sleep(5)
    soup = bs(browser.html, 'html.parser')

    #confirm the length of the parent div list
    parent = soup.find_all('div', class_="item")

    #loop through the parent divs and grab the image url and append it to the base url and append to a list of urls
    url_list = []
    for p in parent:
        image = p.find('a')["href"]
        full_url = "https://astrogeology.usgs.gov" + image
        
        url_list.append(full_url)


    #loop through the url list and append a dictionary with the keys "title" and "img_url"
    hemisphere_image_urls=[]
    for url in url_list:
        browser.visit(url)
        soup=bs(browser.html, 'html.parser')
        result = soup.find('div', class_='downloads')
        a_tag = result.find('a')["href"]
        title_div = soup.find('div', class_='content')
        h2 = title_div.find('h2').text
        hemisphere_image_urls.append({"Title":h2, "img_url":a_tag})
        

    #close browser after scraping
    browser.quit()

    #insert data into MongoDB
    data = {
        "article_title": news_title,
        "article_text": news_p,
        "featured_image": featured_image_url,
        "table": html_table,
        "hemisphere_images": hemisphere_image_urls
    }
    
    return data

# db.mars.drop()

# db.mars.insert(data)