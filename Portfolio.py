import pandas as pd
import numpy as np
import pandas_datareader.data as web
from pandas_datareader import data
import datetime as dt


# Input the full timeframe
# In future this should be a user input
start_date = '2010-01-01'

end_date = '2020-01-01'



class Share:
# Build in the functionality to store historical values and dividends

    def __init__(self, name, asset_type):
        """Initialize attributes."""
        self.name = name
        self.type = asset_type
        self.value = pd.DataFrame() # set this as a blank data frame to be populated once we know the timeframe
        self.div = pd.DataFrame()
        # self.amount = amount

    def get_value(self, date): # At a given point in time
        # Change this to get the full data range first if empty rather than call the database each time
        if len(self.value) == 0:
            self.get_data(start_date,end_date)
        while date not in self.value.index:  # Not all dates will be in the dataframe (trading days only)
            date = pd.to_datetime(date) + dt.timedelta(days = 1) # Add days to the date until we get the next market day
        return round(self.value.loc[date, 'Close'], 2)


    def get_data(self,start_date,end_date):
        df = web.DataReader(self.name,'yahoo', start = start_date, end = end_date)
        df_div = web.DataReader(self.name,'yahoo-dividends', start = start_date, end = end_date)
        self.value = df
        self.div   = df_div

class Strategy:

    def __init__(self,shares, equity_distribution, bond_distribution, cash_distribution, threshold):
        self.shares = shares
        self.equity_distribution = equity_distribution # What percent of the portfolio should be equities?
        self.bond_distribution = bond_distribution # What percent of the portfolio is bonds?
        self.cash_distribution = 100 - (equity_distribution + bond_distribution) # How much is cash? (Leftover)
        self.threshold = threshold # At what threshold should shares be sold to balance the distribution?
# i.e. if a threshold is set to 1, then if the current value of equities (as a percent of the total portfolio)
##  is more than 1 percent higher, then shares need to be sold to balance the portfolio to the desired distribution.

class Portfolio:

    def __init__(self):
        self.shares = {}
        self.log = {}
        self.cash_bal = 0
        self.asset_split = {'Equities': None, 'Bonds': None, 'Cash': None}
        self.asset_values = {'Equities': None, 'Bonds': None, 'Cash': None}
        self.equities = []
        self.bonds = []
        for share in self.shares:
            if self.shares[share] == 'Equity':
                self.equities.append(share)
            elif self.shares[share] == 'Bond':
                self.bonds.append(share)


# Create a function to make the initial purchase based on a given portfolio strategy
# Based on the assumption that one ETF is used for either bonds or equities (amount could be evenly split (or risk weighted) among a series of ETFs or individual stocks)
    def initial_buy(self,amount, strategy,start_date):
        eq_amount = amount*(strategy.equity_distribution/100)
        bnd_amount = amount*(strategy.bond_distribution/100)
        eq_amount2 = eq_amount/len(self.equities)
        bnd_amount2 = bnd_amount/len(self.bonds)
        for share in self.equities:
            self.buy(share,eq_amount2,start_date)
        for share in self.bonds:
            self.buy(share,bnd_amount2,start_date)

    def buy(self, share, amount, date):
        purchase_price = share.get_value(date)
        shares = amount / purchase_price
        # Record the transaction
        self.log[len(self.log)] = ['Buy', share, amount, purchase_price, shares, date]
        # Add the number of shares
        if share in self.shares:
            self.shares[share] += shares
        elif share not in self.shares:
            self.shares[share] = shares

    def sell(self, share, amount, date):
        sell_price = share.get_value(date)
        shares = amount / sell_price
        # Record the transaction
        self.log[len(self.log)] = ['Sell', share, amount, sell_price, shares, date]
        # Add the number of shares
        if share in self.shares:
            self.shares[share] -= shares
        elif share not in self.shares:
            self.shares[share] = shares
        cash_bal += amount

    def calc_value(share, divs, start, end, initial_value):
        # Take the average of the day's high and low for starting share price
        num_shares = initial_value / np.mean([share.loc[start]['Low'], share.loc[start]['High']])
        divs = divs[(divs.index <= pd.to_datetime(end)) & (divs.index >= pd.to_datetime(start))]
        for date in divs.index:
            price = np.mean([share.High.loc[date], share.Low.loc[date]])
            div_value = divs.value.loc[date]
            num_shares += div_value / price
        output = {}
        output['Value'] = num_shares * np.mean([share.loc[end]['Low'], share.loc[end]['High']])
        output['ROI'] = output['Value'] - initial_value
        return (output)

    def reinvest_divs(self, date):
        for share in self.shares:
            if date in share.div.index:
                div_value = share.div.loc['Date','value']
                self.buy(share,div_value,date)

    def get_value(self, date):
        value = self.cash_bal
        # Iterate through the 'shares' attribute and get the current value for each 'Share' object
        for share in self.shares:
            value += share.get_value(date) * self.shares[share]
        return (value)

    def get_asset_values(self, date):
        bond_val = 0
        eq_val = 0
        for share in self.shares:
            if share.type == 'Bond':
                bond_val += share.get_value(date) * self.shares[share]
            elif share.type == 'Equity':
                eq_val += share.get_value(date) * self.shares[share]
        total = bond_val + eq_val + self.cash_bal
        self.asset_values = {'Equities': eq_val, 'Bonds': bond_val, 'Cash': self.cash_bal}
        self.asset_split = {'Equities': (eq_val / total) * 100, 'Bonds': (bond_val / total) * 100,
                            'Cash': (self.cash_bal / total) * 100}