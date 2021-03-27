import pandas as pd
import numpy as np
import pandas_datareader.data as web
from pandas_datareader import data
import datetime as dt


# Input the full timeframe (from user set start and end dates)

class Share:
    # Build in the functionality to store historical values and dividends

    def __init__(self, name, asset_type = None, start_date = dt.datetime.now() - dt.timedelta(days = 365), end_date = dt.datetime.now()):
        """Initialize attributes."""
        self.name = name
        self.type = asset_type
        self.value = pd.DataFrame()  # set this as a blank data frame to be populated once we know the timeframe
        self.div = pd.DataFrame()
        self.start_date = start_date
        self.end_date = end_date  # Maybe make the start and end date optional parameters-default as today and one year ago?
        self.rolling_90_days = pd.DataFrame()
        # self.amount = amount

    def get_value(self, date):  # At a given point in time
        # Change this to get the full data range first if empty rather than call the database each time
        if len(self.value) == 0:
            self.get_data()
        hit_the_end = False  # Identify if we have hit the end of the data range

        while date not in self.value.index:  # Not all dates will be in the dataframe (trading days only)
            if pd.to_datetime(date) >= pd.to_datetime(self.end_date):
                hit_the_end = True  # if we have, then count down until we find a trading date in the range
            if hit_the_end == True:
                date = pd.to_datetime(date) - dt.timedelta(days=1)
            else:
                date = pd.to_datetime(date) + dt.timedelta(days=1)

        return round(self.value.loc[date, 'Close'], 2)

    def get_data(self):
        ninety_days_before = pd.to_datetime(self.start_date) - dt.timedelta(days=90)
        df = web.DataReader(self.name, 'yahoo', ninety_days_before, end=self.end_date)
        df_div = web.DataReader(self.name, 'yahoo-dividends', start=self.start_date, end=self.end_date)
        self.value = df
        self.div = df_div

    def get_rolling(self, date):
        df = self.value
        date = pd.to_datetime(date)
        ninety_days_before = date - dt.timedelta(days=90)
        df = df[(df.index <= date) & (df.index > ninety_days_before)]
        self.rolling_90_days = df


class Strategy:

    def __init__(self, equity_distribution, bond_distribution, cash_distribution, threshold):
        self.equity_distribution = equity_distribution  # What percent of the portfolio should be equities?
        self.bond_distribution = bond_distribution  # What percent of the portfolio is bonds?
        self.cash_distribution = 100 - (equity_distribution + bond_distribution)  # How much is cash? (Leftover)
        self.threshold = threshold  # At what threshold should shares be sold to balance the distribution?


# i.e. if a threshold is set to 1, then if the current value of equities (as a percent of the total portfolio)
##  is more than 1 percent higher, then shares need to be sold to balance the portfolio to the desired distribution.

class Portfolio:
    def __init__(self, shares, div_reinvest=True):
        self.share_types = shares  # Dictionary of share
        self.shares = {}
        self.log = {'Share': [], 'Action': [], 'Date': [], 'Amount': []}  # Transactional history
        self.val_hist = {'Date': [], 'Total Value': [], 'Equities': [], 'Bonds': []}
        self.cash_bal = 0
        self.asset_split = {'Equities': None, 'Bonds': None, 'Cash': None}
        self.asset_values = {'Equities': None, 'Bonds': None, 'Cash': None}
        self.equities = []
        self.bonds = []
        self.div_reinvest = div_reinvest
        for share in self.share_types:
            if self.share_types[share] == 'Equity':
                self.equities.append(share)
            elif self.share_types[share] == 'Bond':
                self.bonds.append(share)

    # Create a function to make the initial purchase based on a given portfolio strategy
    # Based on the assumption that one ETF is used for either bonds or equities (amount could be evenly split (or risk weighted) among a series of ETFs or individual stocks)
    def initial_buy(self, amount, strategy, start_date):
        eq_amount = amount * (strategy.equity_distribution / 100)
        bnd_amount = amount * (strategy.bond_distribution / 100)
        if len(self.equities) == 0:
            eq_amount2 = 0
        else:
            eq_amount2 = eq_amount / len(self.equities)
        if len(self.bonds) == 0:
            bnd_amount2 = 0
        else:
            bnd_amount2 = bnd_amount / len(self.bonds)
        self.cash_bal = amount
        for share in self.equities:
            self.buy(share, eq_amount2, start_date)
        for share in self.bonds:
            self.buy(share, bnd_amount2, start_date)

    def manual_setup(self, shares_input):
        # shares_input is a dictionary type object where the stock ticker is the key and the value is a list containing the date, the number of shares, and the total amount.
        self.shares = {} # Overwrite any previous shares in file; The point of this function is to initialize a new portfolio.
        self.cash_bal = 0 # Overwrite previous values
        for share in shares_input:
            # Buy each share so data is logged
            amount = float(shares_input[share][2])
            volume_shares = float(shares_input[share][1]) # get the number of shares
            date = shares_input[share][0] # Need to convert this to datetime
            date = dt.datetime.strptime(date, '%m/%d/%Y')
            share = Share(share) # Convert to share object
            #self.shares[share] = volume_shares # get amount of shares
            self.cash_bal += amount
            self.buy(share,amount,date,volume_shares = volume_shares, price = amount/volume_shares)

    def buy(self, share, amount, date, volume_shares = None, price = None):
        if price is None:
            purchase_price = share.get_value(date)
        else:
            purchase_price = price
        if volume_shares is None:
            shares = amount / purchase_price
        else:
            shares = volume_shares
        # Record the transaction
        self.log['Share'].append(share.name)
        self.log['Action'].append('Buy')
        self.log['Date'].append(date)
        self.log['Amount'].append(float(amount))
        # Add the number of shares
        if share in self.shares:
            self.shares[share] += shares
        elif share not in self.shares:
            self.shares[share] = shares
        self.cash_bal -= float(amount)

    def sell(self, share, amount, date,volume_shares = None, value = None):
        if value is None:
            sell_price = share.get_value(date)
        else:
            sell_price = value
        if volume_shares is None:
            shares = amount / sell_price
        else:
            shares = volume_shares
        # Record the transaction
        self.log['Share'].append(share.name)
        self.log['Action'].append('Sell')
        self.log['Date'].append(date)
        self.log['Amount'].append(float(amount))
        if share in self.shares:
            self.shares[share] -= shares
        elif share not in self.shares:
            self.shares[share] = shares
        self.cash_bal += float(amount)

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
                div_value = share.div.loc[date, 'value'] * self.shares[share]
                self.cash_bal += div_value
                if self.div_reinvest:
                    self.buy(share, div_value, date)

    def get_value(self, date, indiv_print = False):

        value = self.cash_bal
        print(f"Cash: {value}")
        # Iterate through the 'shares' attribute and get the current value for each 'Share' object
        for share in self.shares:
            share_val = share.get_value(date) * self.shares[share]
            value += share_val
            if indiv_print:
                print(f"{share.name}: ${share_val}")
        print(f"Total: ${value}")
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
        if total > 0:
            self.asset_split = {'Equities': (eq_val / total) * 100, 'Bonds': (bond_val / total) * 100,
                            'Cash': (self.cash_bal / total) * 100}
        self.val_hist['Date'].append(date)
        self.val_hist['Total Value'].append(total)
        self.val_hist['Equities'].append(eq_val)
        self.val_hist['Bonds'].append(bond_val)

    def get_hist_df(self):
        return (pd.DataFrame.from_dict(self.val_hist))

    def get_log(self):
        return (pd.DataFrame.from_dict(self.log))

        # Record the values
        # return(self.asset_values)
        # print(self.asset_values)

# Define start date and end date

# start_date = '2015-01-01'
#
# end_date = '2020-01-05'
#
#
# # Define Shares
#
# # Provide the name of the ticker and type (Equity or Bond)
#
# voo = Share('VOO', 'Equity', start_date,end_date)
# bnd = Share('BND', 'Bond', start_date, end_date)
#
# shares_list = [voo, bnd]
#
# shares_dict = {}
#
# for share in shares_list:
#     shares_dict[share] = share.type
#
# # Provide the equity distribution, the bond distriubtion, cash distribution, and the threshold
# strat = Strategy(50,50,0,5)
#
# # Run the portfolio over a series of months
#
# #
# # portfolio = Portfolio(shares_dict)
# #
# # portfolio.initial_buy(500, strat, start_date)
# #
# # time_period = pd.date_range(pd.to_datetime(start_date), pd.to_datetime(end_date))
# #
# # for day in time_period:
# #     print(day)
# #     portfolio.reinvest_divs(day)
# #     portfolio.get_asset_values(day)
# #     #print(portfolio.asset_split)
# #     if portfolio.asset_split['Equities'] > strat.equity_distribution + strat.threshold:
#         sell_amt = (portfolio.asset_values['Equities'] + portfolio.asset_values['Bonds']) * (
#                     (portfolio.asset_split['Equities'] - strat.equity_distribution) / 100)
#         sell_amt_per = sell_amt / len(portfolio.equities)
#         for share in portfolio.equities:  # sell equities and buy more bonds
#             portfolio.sell(share, sell_amt_per, day)
#         for share in portfolio.bonds:
#             portfolio.buy(share, sell_amt_per, day)
#
#     if portfolio.asset_split['Bonds'] > strat.bond_distribution + strat.threshold:
#         sell_amt = (portfolio.asset_values['Equities'] + portfolio.asset_values['Bonds']) * (
#                     portfolio.asset_split['Bonds'] - strat.bond_distribution)
#         sell_amt_per = sell_amt / len(portfolio.bonds)
#         for share in portfolio.bonds:  # sell bonds and buy more equities
#             portfolio.sell(share, sell_amt_per, day)
#         for share in portfolio.bonds:
#             portfolio.buy(share, sell_amt_per, day)
# portfolio.get_hist_df()
