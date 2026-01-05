import pandas as pd
import numpy as np
import os

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lac_data.csv')

def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")
    
    df = pd.read_csv(CSV_PATH)
    # Replace -999 with NaN for processing
    df.replace(-999, np.nan, inplace=True)
    return df

def get_locations(df):
    return sorted(df['Locations'].unique().tolist())

def get_stats_summary(df, location, year_range=None):
    filtered_df = df[df['Locations'] == location]
    if year_range:
        filtered_df = filtered_df[(filtered_df['YEAR'] >= year_range[0]) & (filtered_df['YEAR'] <= year_range[1])]
    
    summary = {
        'avg_temp': round(filtered_df['T2M'].mean(), 2),
        'max_temp': round(filtered_df['T2M_MAX'].max(), 2),
        'min_temp': round(filtered_df['T2M_MIN'].min(), 2),
        'total_rainfall': round(filtered_df['PRECTOTCORR'].sum(), 2),
        'avg_humidity': round(filtered_df['RH2M'].mean(), 2),
        'avg_wind_speed': round(filtered_df['WS2M_MAX'].mean(), 2)
    }
    return summary

def get_annual_trends(df, location):
    filtered_df = df[df['Locations'] == location]
    annual_data = filtered_df.groupby('YEAR').agg({
        'PRECTOTCORR': 'sum',
        'T2M': 'mean'
    }).reset_index()
    
    return {
        'years': annual_data['YEAR'].tolist(),
        'rainfall': annual_data['PRECTOTCORR'].round(2).tolist(),
        'temp': annual_data['T2M'].round(2).tolist()
    }

def get_monthly_averages(df, location, year):
    # Year-specific monthly averages
    filtered_df = df[(df['Locations'] == location) & (df['YEAR'] == year)].copy()
    
    # Accurate conversion of DOY to month
    # Note: unit='D' adds days, so DOY 1 should be origin + 0 days
    filtered_df['Month'] = pd.to_datetime(filtered_df['DOY'] - 1, unit='D', origin=pd.Timestamp(f'{year}-01-01')).dt.month
    
    monthly_data = filtered_df.groupby('Month').agg({
        'PRECTOTCORR': 'sum',
        'T2M': 'mean',
        'RH2M': 'mean',
        'WS2M_MAX': 'mean'
    }).reset_index()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    return {
        'months': months,
        'rainfall': monthly_data['PRECTOTCORR'].round(2).tolist(),
        'temp': monthly_data['T2M'].round(2).tolist(),
        'humidity': monthly_data['RH2M'].round(2).tolist(),
        'wind_speed': monthly_data['WS2M_MAX'].round(2).tolist()
    }
