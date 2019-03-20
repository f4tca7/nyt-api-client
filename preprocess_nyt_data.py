import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def combine_nyt_data(filename_1, filename_2, base_path, from_y, from_m, to_y, to_m):    
    """
    Utility function to combine two NYT API datasets
    """
    nyt_data_1 = pd.read_csv(base_path + filename_1, index_col='date', parse_dates=True)
    nyt_data_2 = pd.read_csv(base_path + filename_2, index_col='date', parse_dates=True)
    nyt_data = pd.concat([nyt_data_1, nyt_data_2], sort=False).drop_duplicates()
    filename = 'nyt_archive_' + str(from_y) + '_' + str(from_m)  + '_' + str(to_y) + '_' + str(to_m) + '.csv'
    full_path = base_path + filename
    nyt_data.to_csv(full_path)
    print('Created ' + full_path)

def combine_text_columns(data_frame, to_drop):
    """ 
    Helper function to convert all text rows of data_frame to single vector 
    """
    
    to_drop = set(to_drop) & set(data_frame.columns.tolist())
    text_data = data_frame.drop(to_drop, axis=1)    
    text_data.fillna(' ', inplace=True)

    return text_data.apply(lambda x: " ".join(x), axis=1)


def preprocess(nyt_data, save_preprocessed=False, base_path='', filename=''):
    """
    Main preprocessing function
    - Drop all rows with NaNs
    - Combine multiple text columns into a single column    
    - Remove special characters
    - Remove single characters
    - Remove multiple spaces
    - Convert to lowercase
    - remove stop words
    - Lemmatize
    - Join all text for the same date into the same tuple
    """
    stemmer = WordNetLemmatizer()
    if 'Unnamed: 0' in nyt_data.columns:
        nyt_data = nyt_data.drop('Unnamed: 0', axis=1)
    #nyt_data = pd.read_csv('', parse_dates=True)
    
    nyt_data = nyt_data.dropna()
    print('NYT Data shape: ' + str(nyt_data.shape))

    nyt_data = nyt_data.reset_index(drop=True)
    print('Combining text into one column')
    nyt_data['all_text'] = combine_text_columns(nyt_data, ['date'])
    nyt_data = nyt_data.drop(['headline', 'snippet', 'keywords'], axis=1)

    print('Normalizing Text')
    # Remove all the special characters
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : re.sub(r'\W', ' ', x))
    # remove all single characters
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : re.sub(r'\s+[a-zA-Z]\s+', ' ', x))
    # Remove single characters from the start
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : re.sub(r'\^[a-zA-Z]\s+', ' ', x)) 
    # Substituting multiple spaces with single space
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : re.sub(r'\s+', ' ', x, flags=re.I))
    # Removing prefixed 'b'
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : re.sub(r'^b\s+', '', x))
    # Converting to Lowercase
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : x.lower())
    # Lemmatization
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : x.split())
    stop_words = stopwords.words('english')
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : [word for word in x if word not in stop_words])
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : [stemmer.lemmatize(word) for word in x])
    nyt_data['all_text'] = nyt_data['all_text'].apply(lambda x : ' '.join(x))

    print('Combine rows for same date')
    nyt_data['all_text'] = nyt_data.groupby(['date'],as_index=False)['all_text'].transform(lambda x: ' '.join(x))
    nyt_data = nyt_data[['date','all_text']].drop_duplicates()
    nyt_data = nyt_data.reset_index()

    print('Preprocessed data shape: ' + str(nyt_data.shape))

    if save_preprocessed == True :
        #rel_path = '../datasets/stock_data/'
        if len(filename) == 0:
            filename = 'preprocessed_nyt_data.csv'

        full_path = base_path + filename
        nyt_data.to_csv(full_path, index=False)        
        print('Created ' + full_path)

    return nyt_data
