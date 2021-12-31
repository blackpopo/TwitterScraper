import requests
from datetime_tool import *

def create_headers(bearer_token):
    headers = {
        "Authorization": "Bearer {}".format(bearer_token),
    }
    return headers

def create_twitter_url(twitter_id):
    tweet_url =  "https://api.twitter.com/2/tweets/"
    tweet_params = {
        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,conversation_id,created_at,lang',
        'expansions': 'author_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
        'next_token': {}
    }
    return tweet_url + twitter_id, tweet_params

def create_search_url(keyword, end_time, start_time):
    # print(f"JST \n end time {end_time} \n start time {start_time}\n")
    start_time = jst2utc_iso(start_time)
    end_time = jst2utc_iso(end_time)
    # print(f"UTC \n end time {end_time} \n start time {start_time}\n")
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    search_params = {'query': keyword + " lang:ja",
                     'start_time' : start_time,
                     'end_time' : end_time,
                     'tweet.fields': 'id,text,author_id,in_reply_to_user_id,conversation_id,created_at,lang',
                     'expansions': 'author_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
                     'next_token': {}
                     }
    return search_url, search_params

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url=url, headers=headers, params = params)
    if response.status_code != 200:
        print("Endpoint Response Code: " + str(response.status_code))
        raise Exception(response.status_code, response.text)
    return response.json()