import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

api_key = 'W59OQACAUZ0HS2N3'

ticker = 'MSFT'
url1 = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSCO.LON&outputsize=full&apikey={api_key}'
url2 = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
url3 = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&apikey={api_key}'

response = requests.get(url3)
json_data = response.json()
print(json_data)
data = json_data.get('Monthly Time Series')
df = pd.DataFrame(data)
data_df = df.T  # .T changes the rows and columns.
data_df.info()
sns.set_theme(style="darkgrid")
sns.lineplot(x=data_df.index, y=data_df['1. open'], data=data_df)

plt.show()
