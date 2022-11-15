import os
import requests
import csv
import time


BEARER_TOKEN = os.getenv('TWITTER_BEARER')

headers = {
    'Authorization': f"Bearer {BEARER_TOKEN}",
}

# params = {
#     'query': 'from:foxnews',
#     'max_results': '10'
# }

params = {
    'query': 'from:nytimes',
    'max_results': '10'
}

def connect_to_endpoint():
    # open the file in the write mode
    with open(f'fox_tweets_{time.time()}', 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        next_token= None
        i = 0
        while next_token != 'finished':

            print(f"iteration: {i}")
            print(f"next token: {next_token}")
            if next_token:
                params['next_token'] = next_token
            response = requests.get('https://api.twitter.com/2/tweets/search/recent', params=params, headers=headers)
            json = response.json()
            print(json)
            meta = json['meta']
            if 'next_token' in meta.keys():
                next_token = meta['next_token']
            else:
                next_token = 'finished'
            data = json['data']

            for tweet in data:
                text = tweet['text']
                writer.writerow([text])
            i += 1


def main():
    connect_to_endpoint()


if __name__ == "__main__":
    main()