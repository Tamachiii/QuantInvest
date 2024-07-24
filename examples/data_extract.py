import yfinance as yf
import pandas as pd
import numpy as np

useful_keys = {
    'financials': [
        "EBIT", "Operating Income", "Gross Profit", "Total Revenue", "Net Income", "EBITDA", "Dividend Per Share"
    ],
    'balance-sheet': [
        "Invested Capital", "Total Assets", "Current Liabilities", "Total Debt"
    ],
    'cash-flow': [
        "Capital Expenditure", "Free Cash Flow"
    ]
}

def get_historical_data(ticker):
    company = yf.Ticker(ticker)
    historical_data = company.financials.transpose()

    historical_financials = {}
    for year in range(10):
        try:
            year_data = historical_data.iloc[year]
            for key in useful_keys['financials']:
                if key in year_data.index:
                    if key not in historical_financials:
                        historical_financials[key] = []
                    historical_financials[key].append(year_data[key])
        except IndexError:
            break

    return historical_financials

def calculate_margins_median(historical_data):
    margins_median = {}

    if "Gross Profit" in historical_data and "Total Revenue" in historical_data:
        gross_margins = [gp / tr for gp, tr in zip(historical_data["Gross Profit"], historical_data["Total Revenue"])]
        margins_median["Gross Margin Median 10 Years"] = np.median(gross_margins) * 100

    if "Operating Income" in historical_data and "Total Revenue" in historical_data:
        operating_margins = [oi / tr for oi, tr in zip(historical_data["Operating Income"], historical_data["Total Revenue"])]
        margins_median["Operating Margin Median 10 Years"] = np.median(operating_margins) * 100

    if "Net Income" in historical_data and "Total Revenue" in historical_data:
        net_margins = [ni / tr for ni, tr in zip(historical_data["Net Income"], historical_data["Total Revenue"])]
        margins_median["Net Margin Median 10 Years"] = np.median(net_margins) * 100

    return margins_median

def get_company_data(ticker):
    company = yf.Ticker(ticker)
    data = {}

    financials = company.financials.transpose()
    for key in useful_keys['financials']:
        if key in financials.columns:
            data[key] = financials[key].values[0] if not financials[key].empty else None

    balance_sheet = company.balance_sheet.transpose()
    for key in useful_keys['balance-sheet']:
        if key in balance_sheet.columns:
            data[key] = balance_sheet[key].values[0] if not balance_sheet[key].empty else None

    cashflow = company.cashflow.transpose()
    for key in useful_keys['cash-flow']:
        if key in cashflow.columns:
            data[key] = cashflow[key].values[0] if not cashflow[key].empty else None

    data["Ticker"] = ticker

    historical_data = get_historical_data(ticker)
    margins_median = calculate_margins_median(historical_data)
    data.update(margins_median)

    return data

tickers = ["MSFT", "AAPL", "GOOGL","AIR.PA","NVDA","TTE.PA"]

companies_data = []
for ticker in tickers:
    company_data = get_company_data(ticker)
    companies_data.append(company_data)

df = pd.DataFrame(companies_data)

columns_order = ["Ticker"] + [col for col in df.columns if col != "Ticker"]
df = df[columns_order]

df.to_csv("company_data.csv", index=False)
