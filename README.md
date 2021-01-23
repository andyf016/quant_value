# Quantitative Value Investing App
This app will take in a portfolio value in dollars and return an xls spreadsheet containing to best 50 stocks from the S&P 500 and how many shares to buy of each. 

Quantitative value investing, also known as Systematic value investing, is a form of value investing that analyzes fundamental data such as financial statement line items, economic data, and unstructured data in a rigorous and systematic manner. Practitioners often employ quantitative applications such as statistical / empirical finance or mathematical finance, behavioral finance, natural language processing, and machine learning.
https://en.wikipedia.org/wiki/Quantitative_value_investing

## Installation
Afte cloning the repo create a virtual environment and activate it. Then install the requirements using pip. 
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

## Usage
After installing all required packages. Run the program, the console will prompt you to input the value of your portfolio. After making the necessary api calls the program will create an Excel spreadsheet in its base directory with the best 50 stock and how many shares of each to buy.
```bash
python quant_value.py
```

## Contributing
This application is based on the Free Code Camp Algorithmic Trading course given by Nick McCullum.
https://www.youtube.com/watch?v=xfzGZB4HhEE



