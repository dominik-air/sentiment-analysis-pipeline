#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
from dask import dataframe as df1
from fastapi import FastAPI


# USED DATASET
# https://www.kaggle.com/datasets/kazanova/sentiment140
TWEETS = df1.read_csv('data/tweets.csv', names=['target', 'ids', 'date', 'flag', 'user', 'text'])
TWEETS = TWEETS[['ids', 'text', 'user', 'date']]


def get_tweets(N: int) -> pd.DataFrame:
    if N >= 1600:
        raise ValueError
    df_sampled = TWEETS.sample(frac=0.001, replace=None)
    tweets_dict = {}
    tweet_id, body, user, created_at = [], [], [], []
    for n, tweet in enumerate(df_sampled.itertuples()):
        if n >= N:
            break
        tweet_id.append(tweet[1])
        body.append(tweet[2])
        user.append(tweet[3])
        created_at.append(tweet[4])
    tweets_dict['id'], tweets_dict['body'], tweets_dict['user'], tweets_dict['created_at'] = tweet_id, body, user, created_at
    return pd.DataFrame(tweets_dict)


app = FastAPI()


@app.get('/')
async def get_n_tweets(n: int):
    tweets_df = get_tweets(n)
    return tweets_df.to_dict(orient="records")
