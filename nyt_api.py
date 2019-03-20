import requests
import json
import secrets
import datetime
import numpy as np
import pandas as pd


COLUMNS = ['date', 'headline', 'snippet', 'keywords']
API_URL = 'https://api.nytimes.com/svc/archive/v1/'

def json_to_list(data):   
    """
    Reads pub_date, headline, snippet and keywords from an NYT Archive API json document and converts them into a 2d list
    """
    #data = json.load(f)
    rows = []
    for doc in data['response']['docs']:
        cols = []
        if 'pub_date' in doc:
            cols.append(pd.to_datetime(doc['pub_date']).date())
        else :
            cols.append(' ')
        if ('headline' in doc) & ('main' in doc['headline']):    
            cols.append(doc['headline']['main'])
        else :
            cols.append(' ')
        if 'snippet' in doc:                
            cols.append(doc['snippet'])
        else :
            cols.append(' ')            
        pub_keywords = ''
        for keyword in doc['keywords']:
            pub_keywords =  pub_keywords + (keyword['value']) + ' '
        cols.append(pub_keywords)
        rows.append(cols)    
    return rows


def load_from_archives_api(from_year, to_year, from_month, to_month, store_indermediate=False, intermediate_path=''):
    """
    All params are inclusive. E.g. for to_year == 2019, to_month == 1, data for January 2019 will be included
    Loads data from New York Times Archives API for the specified period.
    Returns one consolidated pandas dataframe
    Only extracts pub_date, headline, snippet and keywords

    Keyword arguments:
    from_year, to_year, from_month, to_month -- Data range to load, inclusive
    store_indermediate -- Set store_indermediate to True to save an intermediate csv every 12 month into intermediate_path
    intermediate_path  -- should have a trailing /
    """
    now = datetime.datetime.now()

    if from_year > to_year :
        raise Exception('from_year should not be larger than to_year')
    if (from_year == to_year) & (from_month > to_month):
        raise Exception('from_month should not be larger than to_month for the same year')   
    if from_year < 1851 :
        raise Exception('can olny read data from 1851 onwards')   
    if (from_year > now.year) | (to_year > now.year) :
        raise Exception('cannot read articles from the future')
    if (to_year == now.year) & (to_month > now.month) :
        raise Exception('cannot read articles from the future. Set to_month lower')
    elapsed_month = 0
    num_req_month = 0
    all_rows = []
    num_years = to_year - from_year
    num_month = num_years * 12
    num_month += to_month + 1
    num_month -= from_month

    curr_year = from_year
    curr_month = from_month

    for month in range(num_month) :
        print('Fetching data for ' + str(curr_year) +'_' + str(curr_month))
        url = API_URL + str(curr_year) +'/' + str(curr_month) + '.json?api-key=' + secrets.nyt_api_key
        resp = requests.get(url)
        if resp.status_code != 200:
            # Continue, but print error
            print('ERROR GET /archive/v1/' +  str(curr_year) +'/' + str(curr_month) + '.json?api-key=' + secrets.nyt_api_key + ' {}'.format(resp.status_code))
        else :
            print('200 GET ' + url)
            json_parsed = resp.json()
            rows = json_to_list(json_parsed)
            if len(all_rows) == 0 :
                all_rows = np.array(rows)
            else :
                all_rows = np.vstack((all_rows,rows))
            num_req_month += 1

        if curr_month % 12 == 0 :
            curr_month = 1
            curr_year += 1
        else :
            curr_month +=1
        
        elapsed_month += 1

        if (elapsed_month % 12 == 0) & (store_indermediate==True) :
            df = pd.DataFrame.from_records(all_rows, columns=COLUMNS) 
            filename = 'intermediate_nyt_archive_' + str(from_year) + '_' + str(from_month)  + '_' + str(curr_year) + '_' + str(curr_month) + '.csv'
            df.to_csv(intermediate_path + filename)
            print('Created ' + intermediate_path + filename)
            elapsed_month = 0
        

    df = pd.DataFrame.from_records(all_rows, columns=COLUMNS)
    print('Successfully loaded data fror ' + str(num_req_month) + ' month')
    print('')
    print('Shape of consolidate DataFrame: ', df.shape)      
    return df

