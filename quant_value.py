import numpy as np
import pandas as pd
import xlsxwriter
import requests
from scipy import stats
import math

stocks = pd.read_csv('sp_500_stocks.csv')
print(stocks)