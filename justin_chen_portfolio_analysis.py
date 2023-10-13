# Name: Justin Chen

# You may not import any additional libraries for this challenge besides the following
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf

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
    #TODO delete the following line and start building the PortfolioAnalysis class.
    pass


if __name__ == "__main__":  # Do not change anything here - this is how we will test your class as well.
    fake_port = PortfolioAnalysis("dummy_data.xlsx")
    print(fake_port.asset_values)
    print(fake_port.unrealized_pnl)
    fake_port.plot_portfolio()
    fake_port.plot_liquidity()