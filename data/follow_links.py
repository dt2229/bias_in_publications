import re
import csv
import time
import sys
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
from webdriver_manager.chrome import ChromeDriverManager
import urllib3
from time import sleep
from selenium.webdriver.common.by import By



def unshorten_url(url):
    http = urllib3.PoolManager()
    test = http.request('GET', url)
    print(f"unshortened: {test}")
    unshortened = test.geturl()
    return unshortened

def clean_webpage(web_html):
    soup = BeautifulSoup(web_html, features="html.parser")

    # remove all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    page_text = soup.get_text()
    return page_text


def extract_text_fox(url):
    print(url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        result = response.text
    except:
        print('err')
        print(response)
        return

    return clean_webpage(response)

def set_up_nyt(url, cookies):
    url = unshorten_url(url)
    print(f"unshortened url: {url}")
    chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    url = unshorten_url(url)
    print(f"unshortened url: {url}")
    chrome_driver.get(url)

    for cookie_name in cookies.keys():
        cookie_to_add = {'name': cookie_name, 'value': cookies[cookie_name], 'domain': 'nytimes.com'}
        chrome_driver.add_cookie(cookie_to_add)
    sleep(90)
    # here user to sign in using google account
    return chrome_driver


def extract_text_nyt(driver, url):
    # To load entire webpage
    url = unshorten_url(url)
    print(f"unshortened url: {url}")
    driver.get(url)
    sleep(4)
    result = driver.find_element(By.XPATH, "/html/body").text
    return clean_webpage(result)


# for sites that require javascript
def extract_text_js(url, cookies):
    chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    # To load entire webpage
    chrome_driver.get(url)
    sleep(4)
    result = chrome_driver.find_element(By.XPATH, "/html/body").text
    return clean_webpage(result)


def follow_links(csv_file_to_read, csv_file_to_write, outlet, sub_list, cookies):
    with open(csv_file_to_read, 'r') as read_obj:
        with open(csv_file_to_write, 'w') as write_f:
            # create the csv writer
            writer = csv.writer(write_f)
            reader = csv.reader(read_obj)

            if outlet == 'nyt':
                chrome_driver = set_up_nyt(
                    'https://www.nytimes.com/2022/10/31/arts/music/taylor-swift-midnights-billboard-chart.html',
                    cookies)
            # return
            i = 0
            pull = False
            for row in reader:
                print('-------------------------------------------------------------------')
                print(f"pulling link text for tweet number: {i}\n")
                # theres an issue with tweet 29 in nyt so lets skip it

                print(f'length of tweet: {len(row)}')
                for tweet in row:
                    # if i <= 29:
                    #     i += 1
                    #     continue
                    i += 1
                    if 'Rahel Solomon breaks down the lates' in tweet:
                       pull = True
                    if not pull:
                        continue
                    print(tweet)

                    # this will pull all links in the tweet, so we might get some external links
                    # that the tweet is referencing, in addition to the link to the full article of
                    # the tweet, but we think this is ok because the linked article is likely still
                    # relevant and likely  displays similar viewpoints of the news outlet
                    links = re.findall(r'(https?://[^\s]+)', tweet)
                    for link in links:

                        if outlet=='fox':

                            text = extract_text_fox(link)
                        elif outlet == 'nyt':
                            text = extract_text_nyt(chrome_driver, link)
                        else:
                            text = extract_text_js(link, cookies)
                        # remove multiple spaces
                        text = re.sub(' +', ' ', text).strip()

                        for sub in sub_list:
                            text = text.replace(' ' + sub + ' ', ' ')
                        print(text)
                        writer.writerow([text])

if __name__ == "__main__":
    # allows us to execute script from root instead of data folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # change this to toggle between fox and nyt
    # outlet = 'fox'
    # outlet = 'nyt'
    outlet = 'cnn'
    # outlet = 'npr'

    if outlet == 'fox':
        csv_file_to_read = 'fox_tweets_1668364371_220901.csv'
        csv_file_to_write = f'fox_tweets_link_text_{time.time()}.csv'
        # random strings that show up in the fox news articles that we don't expect
        # to be meaningful
        sub_list = [
            'Subscribe',
            'Subscribed',
            'Election season is here! Get the latest race updates, exclusive interviews, and more Fox News politics content.',
            'You\'ve successfully subscribed to this newsletter!',
            'Arrives Tuesdays']
        cookies = {}
    elif outlet == 'nyt':
        csv_file_to_read = 'nyt_tweets_1668434311.csv'
        csv_file_to_write = f'nyt_tweets_link_text_{time.time()}.csv'
        sub_list = []
        # nyt cookies
        # cookies = {}
        cookies = {'nyt-geo': 'US',
                   'nyt-gdpr': '0',
                   'nyt-us': '1'}
        # cookies = {'nyt-geo': 'US',
        #            'nyt-gdpr': '0',
        #            'nyt-us': '1',
        #            'nyt-b3-traceid': '94093182e19d419f905930db25834dd2',
        #            'nyt-purr': 'cfhhcfhhhckfh',
        #            # 'user-id': '102419765750277570668',
        #            'sessionActive': 'true',
        #            'sessionIndex': '2|1668526345701|eTZREV25UPAl9IixM6Mx8y|1668523833672',
        #            'nyt-auth-method': 'sso',
        #            'nyt-cmots': 'eyJmcmVxdWVuY3kiOnsiMTQ3ODA4NjQ1NiI6eyJpbmxpbmVVbml0Ijp7ImYiOjEsInMiOjEsImZjIjoxNjY4NTI2NTIzLCJzYyI6MTY2ODUyNjUyMywiY2EiOjE2Njg1MjY1MjN9fSwiMTQ3ODU0NjMxMyI6eyJpbmxpbmVVbml0Ijp7ImYiOjIsInMiOjIsImZjIjoxNjY4NTIzODM2LCJzYyI6MTY2ODUyMzgzNiwiY2EiOjE2Njg1MjM4MzZ9fX19'}
    elif outlet == 'cnn':
        csv_file_to_read = 'cnn_tweets_1668521533_21986.csv'
        csv_file_to_write = f'cnn_tweets_link_text_{time.time()}.csv'
        sub_list = []
        cookies = {}
    elif outlet == 'npr':
        csv_file_to_read = 'npr_tweets_1668521713_4138281.csv'
        csv_file_to_write = f'npr_tweets_link_text_{time.time()}.csv'
        sub_list = []
        # nyt cookies
        cookies = {}
    else:
        sys.exit()

    follow_links(csv_file_to_read, csv_file_to_write, outlet, sub_list, cookies)
