import requests
import json
import secrets
import datetime
import nyt_api
import preprocess_nyt_data
import numpy as np
import pandas as pd


FROM_Y = 2019
TO_Y = 2019
FROM_M = 1
TO_M = 2
base_path = 'datasets/'

def load_and_store(from_year, to_year, from_month, to_month):
    """
    Sample call of NYT API
    """
    df = nyt_api.load_from_archives_api(FROM_Y, TO_Y, FROM_M, TO_M, True, base_path) 
    filename = 'nyt_archive_' + str(from_year) + '_' + str(from_month)  + '_' + str(to_year) + '_' + str(to_month) + '.csv'
    df.to_csv(base_path + filename)
    print('Created ' + base_path + filename)
    return df

def preprocess(df):
    preprocess_nyt_data.preprocess(df, save_preprocessed=True, base_path=base_path)

#df = load_and_store(FROM_Y, TO_Y, FROM_M, TO_M)
df = pd.read_csv('datasets/nyt_archive_2019_1_2019_2.csv') 
print(df.head())
preprocess(df)