import pandas as pd

def total_sales_by_region(df):
    return df.groupby('region')['monthly_amount'].sum()

def monthly_sales_trend(df):
    return df.groupby(df['date'].dt.to_period('M'))['monthly_amount'].sum()

def top_performing_region(df):
    total_sales = total_sales_by_region(df)
    return total_sales.idxmax()
