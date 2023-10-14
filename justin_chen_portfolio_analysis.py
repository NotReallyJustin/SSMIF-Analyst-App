# Name: Justin Chen

# You may not import any additional libraries for this challenge besides the following
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import os
import re
from math import isnan

class PortfolioAnalysis:
    """
    Create a constructor that reads in the excel file and calls all necessary methods
    You may set the output of these methods to be attributes of the class that you may
    access later on in other challenges.

    Create a method called `clean_data` which accurately deals with any discrepancies
    in the input data and returns usable data that you can access for the rest of your tasks
    You must have comments explaining why you chose to make any of the changes you did. Any
    missing (NA) values must be calculated for or found from yfinance accordingly.
    The cleaned data should be exported to an excel file with 3 sheets, all of the same format
    as the original data. The file name should be called `cleaned_data.xlsx`.
    
    #NOTE:
    You may import and use this cleaned data file for any of the optional challenges, as needed.
    You may also import this file and create an instance of the PortfolioAnalysis class to use
    in any of the optional challenges, as needed.

    Create a method called `asset_value` that calculates the total market value of each equity
    in the portfolio at the end of the month, with tickers in the rows and dates in the columns
    as well as another row that keeps track of the portfolio's Net Asset Value (NAV) at the end
    of each month. If there is no position for a certain equity during a given month, its value
    should be 0. This data should be kept track of from the end of June to the end of September

    Create a method called `unrealized_returns` that calculates the unrealized returns of each stock.
    The output should be a dataframe that has tickers in the rows, dates in the columns, and the
    unrealized gain/loss of each ticker at the end of each month.
    If there is no unrealized loss to be calculated for a given stock during a given month, its
    value should be 0.

    Create a method called `plot_portfolio` that builds a plot of the portfolio's value over time,
    from the end of June to the end of September

    Create a method called `plot_liquidity` that builds a plot of the ratio between the cash on
    hand and the portfolio's total value, from the end of June to the end of September
    """

    def __init__(self, excel_path:str, export_clean_data:bool=True):
        '''
        Creates a portfolio analysis that reads an .xlsx file path (ie. dummy_data) and cleans it by replacing missing data with either
        data found on Y-Finance, or linear regression if it still can't be found. Then, it calculates asset values and unrealized returns, then 
        stores them inside parameters/arguments
        @param excel_path The path to the excel file
        @param export_clean_data Whether Whether or not to export the cleaned data. `True` by default.
        '''

        # Just a paranoid error checking thing because I might use this library down the line - make sure the excel file exists
        assert os.path.exists(excel_path), 'The excel_path entered does not exist'
        assert os.path.isfile(excel_path), 'The path provided is not a file'
        assert os.path.splitext(excel_path)[-1].lower() == ".xlsx", 'The path provided is not an excel file'

        # Mistake learned, we're not rewriting Pandas this year

        '''
        A list of the column names for items that should be numeric
        '''
        self.NUMERIC_COLS = ["Quantity", "UnitCost", "MarketPrice"]
        
        '''
        A dictionary that stores all the CSVs of inside the excel as dataframes
        '''
        self.excel_dfs:dict = pd.read_excel(excel_path, sheet_name=None)       # None loads all worksheets as a dict
        self.excel_dfs:dict = dict(sorted(self.excel_dfs.items()))             # Sort the dictionary
        #self.clean_data(export_clean_data)
        self.clean_data(False)

        self.asset_value()
        self.unrealized_returns()

    def clean_data(self, export:bool):
        '''
        Cleans the data by replacing missing data with data found on Y-Finance, if possible. If not, we look back to the last possible day with data
        @param export If this is set to true, the clean data will be exported to cleaned_data.xlsx
        '''

        # Characters to ignore and get rid of
        IGNORE_CHARS = r'["\+\'$ ]'
        NAN_RE = r'nan'

        # ⭐ Going to create a dict that stores unit cost; we'll see what that does later
        unit_cost:dict = dict()
        
        for key in self.excel_dfs.keys(): # For each sheet

            # Step 1: Clean Data
            for to_convert_cols in self.NUMERIC_COLS:
                # First, get rid of the chars we can choose to ignore. 
                self.excel_dfs[key][to_convert_cols] = self.excel_dfs[key][to_convert_cols].map(lambda item : re.sub(IGNORE_CHARS, "", item) if isinstance(item, str) else item)
                # Then, convert to numbers
                self.excel_dfs[key][to_convert_cols] = pd.to_numeric(self.excel_dfs[key][to_convert_cols], errors='coerce')

            # Step 2: Find Missing Data, if it exists

            # First, let's take care of market price
            for index, row in self.excel_dfs[key].iterrows():

                # Feels a bit redundant, but this saves a lot of runtime with you not having to constantly fetch yfinance data
                if isnan(row["MarketPrice"]):
                    try:
                        # 🚨 Sometimes, we might not have a trading day. What we will do is download data for the past 5 days and take
                        # the most recent of them

                        # Remember they key was technically also the time
                        end_time = datetime.strptime(key, "%Y-%m-%d")
                        start_time = end_time - timedelta(days=5)

                        # We only need to take the most recent one
                        dl_data = yf.download(tickers=row["Stock"], start=start_time, end=end_time).iloc[-1]
                        self.excel_dfs[key].loc[index, "MarketPrice"] = dl_data["Adj Close"]
                        
                    except:
                        # If we get to this place, it means the stock data does not exist. If it doesn't exist, then 
                        self.excel_dfs[key].loc[index, "MarketPrice"] = 0

                # ⭐ Next, let's take care of UnitPrice
                # @see: https://www.investopedia.com/terms/u/unitcost.asp#:~:text=The%20unit%20cost%2C%20also%20known,this%20price%20is%20company%20profit.
                # Unit price *is* our "break even point", which doesn't really change between months (since it's when we bought the stock)
                
                # Initialize UnitCost dictionary if it's empty
                if (not (row["Stock"] in unit_cost)):
                    unit_cost[row["Stock"]] = -1        # Unit costs can never be -1 so this is a placeholder

                # Try to find a unit cost value
                if not(isnan(row["UnitCost"])):
                    unit_cost[row["Stock"]] = row["UnitCost"]

        # ⭐ If a stock does not have a UnitCost, use the 1st MarketPrice we have
        for stock_ticker in unit_cost:
            for key in self.excel_dfs.keys():
                if unit_cost[stock_ticker] == -1:   # if we found the marketprice, stop.
                    filtered_row = self.excel_dfs[key].query(f"Stock == '{stock_ticker}'")
                    unit_cost[stock_ticker] = filtered_row["MarketPrice"]

        # ⭐ Loop back into the dataframe and fill in the missing UnitCosts
        for key in self.excel_dfs.keys(): # For each sheet
            for index, row in self.excel_dfs[key].iterrows():
                if isnan(row["UnitCost"]):
                    self.excel_dfs[key].loc[index, "UnitCost"] = unit_cost[row["Stock"]]

            # If needed, print dfs here
            # print(self.excel_dfs[key])
            # print("-------------")

        # If needed, export
        if (export):
            self.export_data()

    
    def export_data(self):
        '''
        Exports a cleaned data to cleaned_data.xlsx with all 3 sheets of excel files
        '''
        # @see https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html

        with pd.ExcelWriter("cleaned_data.xlsx") as writer:
            for sheet_name, sheet in self.excel_dfs.items():
                sheet.to_excel(writer, sheet_name=sheet_name, index=False)

    def asset_value(self):
        '''
        Calculates the total asset value of each equity, the net asset value of our equity portfolio, and exports it as a dataframe
        If there is no position for a certain equity during a given month, its value is 0.
        '''

        # Dataframe to store all the asset values
        asset_df = pd.DataFrame()

        for sheet_date, sheet in self.excel_dfs.items():
            # Note to self: pandas brackets == columns
            for index, row in sheet.iterrows():
                asset_df.loc[row["Stock"], sheet_date] = row["MarketPrice"] * row["Quantity"]
        
        asset_df = asset_df.fillna(0)      # If no position, its value is 0

        # Add a row for net asset values
        # According to https://www.wallstreetprep.com/knowledge/net-asset-value-nav/, Net Asset Value (NAV) = Fund Assets – Fund Liabilities. 
        # We don't have liabilities (I hope, because I'd be kinda mad if we're not allowed to short stuff because "liability" and still have debt) so it's just net assets
        
        asset_df.loc["Net Asset Value", :] = asset_df.sum()
        self.asset_values = asset_df

    def unrealized_returns(self):
        '''
        Calculates the unrealized returns of each stock and exports it as a dataframe.
        If there is no unrealized gain/loss to be calculated for a given stock during a given month, its value is 0.
        '''

        # Unrealized returns according to Investopedia is just the total value of an equity if we subtract the unit costs
        # In other words, (marketPrice - unitCosts) * quantity
        # We could use the net asset value dataframe to do half the calculations, but since we're already looping through the CSVs
        # to calculate total value of our unit costs, it's much neater to just not call net asset value

        # Dataframe to store all the unrealized returns
        ureturns_df = pd.DataFrame()

        for sheet_date, sheet in self.excel_dfs.items():
            for index, row in sheet.iterrows():
                ureturns_df.loc[row["Stock"], sheet_date] = (row["MarketPrice"] - row["UnitCost"]) * row["Quantity"]
        
        ureturns_df = ureturns_df.fillna(0)      # If no position, its value is 0

        print(ureturns_df)
        self.unrealized_pnl = ureturns_df


if __name__ == "__main__":  # Do not change anything here - this is how we will test your class as well.
    fake_port = PortfolioAnalysis("dummy_data.xlsx")
    # print(fake_port.asset_values)
    # print(fake_port.unrealized_pnl)
    # fake_port.plot_portfolio()
    # fake_port.plot_liquidity()