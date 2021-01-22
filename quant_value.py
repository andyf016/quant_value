import numpy as np
import pandas as pd
import xlsxwriter
import requests
from scipy import stats
from scipy.stats import percentileofscore as score
import math
from secrets import IEX_CLOUD_API_TOKEN

stocks = pd.read_csv('sp_500_stocks.csv')
symbol = ''

api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'

# chunks function adapted from:
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """ Yield successive n-sized chunks from lst """
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


# create lists of symbols in order to make batch api calls
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#    print(symbol_strings[i])

# columns for pandas data frame
my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']

final_dataframe = pd.DataFrame(columns = my_columns)

# make batch api calls
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    data[symbol]['quote']['peRatio'],
                    'N/A'
                ],
                index = my_columns
            ), ignore_index = True
        )

# Remove glamour stocks
# Sort the dataframe by the stocks' price to earnings ratio, 
# drop all stocks outside the top 50,
# and remove any stocks with a negateive PTE ratio
final_dataframe.sort_values("Price-to-Earnings Ratio", ascending = True, inplace = True)
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1, inplace = True)


def portfolio_input():
    global portfolio_size 
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except:
        print("Please anter an actual number \n Try again:")
        portfolio_size = input("Enter the size of your portfolio:")

portfolio_input()
# print(final_dataframe)

position_size = float(portfolio_size)/len(final_dataframe.index)
for row in final_dataframe.index:
    final_dataframe.loc[row, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[row, 'Price'])
print(final_dataframe)

"""
Start filtering stocks with the lowest percentiles on the following metrics:
- Price-to-earnings ratio
- Price-to-book ratio
- Price-to-sales ratio
- Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization
- Enterprise value divided by Gross Profit

Some of these metrics arent provided by the IEX Cloud API and must be computed
manually after pulling raw data
"""

symbol = 'AAPL'
batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
data = requests.get(batch_api_call_url).json()


# Price-to-earnings ratio
pe_ratio = data[symbol]["quote"]["peRatio"]


# Price-to-book ratio
pb_ratio = data[symbol]['advanced-stats']['priceToBook']

# Price-to-sales ratio
ps_ratio = data[symbol]['advanced-stats']['priceToSales']

# Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization (EV/EBITDA)
enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
ebitda = data[symbol]['advanced-stats']['EBITDA']
ev_to_ebitda = enterprise_value/ebitda


# Enterprise value divided by Gross Profit
gross_profit = data[symbol]['advanced-stats']['grossProfit']
ev_to_gross_profit = enterprise_value/gross_profit

# Setting columns for robust value dataframe
# rv stands for robust value
rv_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'Price-to-earnings ratio',
    'PE Percentile',
    'Price-to-book ratio',
    'PB Percentile',
    'Price-to-sales ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'RV Score'
]

# create rv Pandas Dataframe
rv_dataframe = pd.DataFrame(columns = rv_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']

        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN
        rv_dataframe = rv_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]['quote']['latestPrice'],
                'N/A',
                data[symbol]['quote']['peRatio'],
                'N/A',
                data[symbol]['advanced-stats']['priceToBook'],
                'N/A',
                data[symbol]['advanced-stats']['priceToSales'],
                'N/A',
                ev_to_ebitda,
                'N/A',
                ev_to_gross_profit,
                'N/A',
                'N/A'
            ],
            index = rv_columns),
            ignore_index = True
        )


# replace missing data with the average non NaN datapoint from that column
for column in ['Price-to-earnings ratio', 'Price-to-book ratio', 'Price-to-sales ratio', 'EV/EBITDA', 'EV/GP']:
    rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)
rv_dataframe[rv_dataframe.isnull().any(axis=1)]


metrics ={  
    'Price-to-earnings ratio': 'PE Percentile',
    'Price-to-book ratio': 'PB Percentile',
    'Price-to-sales ratio': 'PS Percentile',
    'EV/EBITDA': 'EV/EBITDA Percentile',
    'EV/GP': 'EV/GP Percentile',
}

for metric in metrics.keys():
    for row in rv_dataframe.index:
        rv_dataframe.loc[row, metrics[metric]] = score(rv_dataframe[metric], rv_dataframe.loc[row, metric])
print(rv_dataframe)