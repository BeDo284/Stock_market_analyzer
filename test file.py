import json
import os
import seaborn as sns
import pandas as pd
import requests
from matplotlib import pyplot as plt

api_key1 = 'W59OQACAUZ0HS2N3'
api_key2 = 'TWGWL6U2XC4X2L6C'

ticker = 'AAPL'
url_daily = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key2}'
url_monthly = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&apikey={api_key2}'
url_weekly = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&{ticker}=IBM&apikey={api_key2}'
url_intra_day = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={api_key2}'

# Define the relative path
relative_path = 'data/intraday/intraday_stock_market_data-%s.json' % ticker
# Get the base directory of the current Python script
base_directory = os.path.dirname(os.path.abspath(__file__))
# Construct the full path by joining the base directory and the relative path
file_to_save = os.path.join(base_directory, relative_path)


def create_file():
    response = requests.get(url_intra_day)
    json_data = response.json()
    directory = os.path.dirname(file_to_save)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_to_save, 'w', newline='') as file:
        json.dump(json_data, file, indent=4)


def create_dataframes():
    meta_data = None
    stock_data = None
    try:
        with open(file_to_save) as f:
            data = json.load(f)
        # Separate meta_data and stock_data
        meta_data = pd.DataFrame(data['Meta Data'], index=['Meta Data']).T
        stock_data = pd.DataFrame(data['Time Series (5min)']).T
        #stock_data = pd.DataFrame(data['Time Series (Daily)']).T
        # stock_data = pd.DataFrame(data['Monthly Time Series']).T
        # .T transposes the DataFrame, so that dates become rows and attributes become columns.
        # Display the DataFrames
        print("Meta Data:")
        print(meta_data)
        print("\nStock Data:")
        print(stock_data)
    except Exception as e:
        print(f'An error occurred: {e}')
    return meta_data, stock_data


#create_file()
meta_data_df, stock_data_df = create_dataframes()

plt.figure(figsize=(10, 6))
sns.lineplot(data=stock_data_df['1. open'], label='Open')
plt.title('Stock Market Data: Open')
plt.xlabel('Date')
plt.ylabel('Value')
every_sixth_tick = stock_data_df.index[::6]
plt.xticks(ticks=every_sixth_tick, rotation=45)
plt.legend()
plt.show()