import re
import csv
import time
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup

# allows us to execute script from root instead of data folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def extract_text(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # remove all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    page_text = soup.get_text()
    return page_text

# change this to toggle between fox and nyt
outlet = 'fox'
# outlet = 'nyt'
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
else:
    csv_file_to_read = 'nyt_tweets_1668434311.csv'
    csv_file_to_write = f'nyt_tweets_link_text_{time.time()}.csv'

with open(csv_file_to_read, 'r') as read_obj:
    with open(csv_file_to_write, 'w') as write_f:
        # create the csv writer
        writer = csv.writer(write_f)
        reader = csv.reader(read_obj)
        rows_list = list(reader)
        # if we want to pick up requests at a certain row, use this idx
        i = 308
        for i in range(i, len(rows_list)):
            print('-------------------------------------------------------------------')
            print(f"pulling link text for tweet number: {i}\n")
            tweet = rows_list[i][0]
            i += 1
            # this will pull all links in the tweet, so we might get some external links
            # that the tweet is referencing, in addition to the link to the full article of
            # the tweet, but we think this is ok because the linked article is likely still
            # relevant and likely  displays similar viewpoints of the news outlet
            links = re.findall(r'(https?://[^\s]+)', tweet)
            for link in links:
                text = extract_text(link)
                # remove multiple spaces
                text = re.sub(' +', ' ', text).strip()

                for sub in sub_list:
                    text = text.replace(' ' + sub + ' ', ' ')
                print(text)
                writer.writerow([text])
