# nyt-api-client

Retrieve data from the New York Times Archives API and preprocess for NLP

### Usage:

1) Get an NYT API key from https://developer.nytimes.com/
2) Create a file `secrets.py` in which you set `nyt_api_key` to your API Key (or just replace the key directly in nyt_api.py)
3) In main_program.py, check the date range and target folder
4) Run main_program.py

### What it does:

In `nyt_api.py`:
- Call function load_from_archives_api() to load data from the NYT Archives API https://developer.nytimes.com/docs/archive-product/1/overview
- Arguments from_year, to_year, from_month, to_month specify for which date range to request. Dates are inclusive. E.g. to request data for Dec 2018, Jan 2019, Feb 2019, set `from_year=2018, from_month=12, to_year=2019, to_month=2`
- Only records pub_date, headline, snippet fields
- Returns a Pandas DataFrame. Each row corresponds to one article

In `preprocess_nyt_data.py`:
- Accepts a Pandas DataFrame in the same format as provided by nyt_api.py
- Drop all rows with NaNs
- Combine multiple text columns into a single column    
- Remove special characters
- Remove single characters
- Remove multiple spaces
- Convert to lowercase
- Lemmatize
- Join all text for the same date into one tuple

Dependencies:
pandas, numpy, re, nltk, requests, datetime, json
