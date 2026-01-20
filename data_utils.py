import pandas as pd
import numpy as np
import os
import io

CSV_PATH = os.path.join(os.path.dirname(__file__), 'lac_data.csv')

# Required columns with their roles
REQUIRED_COLUMNS = {
    'core': ['Locations', 'YEAR'],  # Absolutely required
    'optional': ['DOY', 'T2M', 'T2M_MAX', 'T2M_MIN', 'RH2M', 'PRECTOTCORR', 'WS2M_MAX', 'QV2M']
}

def get_required_columns():
    """Return the expected columns for validation reference"""
    return {
        'core': REQUIRED_COLUMNS['core'],
        'optional': REQUIRED_COLUMNS['optional'],
        'all': REQUIRED_COLUMNS['core'] + REQUIRED_COLUMNS['optional']
    }

def normalize_columns(df):
    """
    Normalize column names to match expected format.
    Auto-detects location and year columns from any CSV file.
    """
    # Possible location column names (case-insensitive)
    location_patterns = [
        'locations', 'location', 'city', 'place', 'region', 'area', 'state',
        'province', 'country', 'province/state', 'country/region', 'name',
        'site', 'station', 'district', 'zone', 'territory'
    ]
    
    # Possible year/time column names (case-insensitive)
    year_patterns = [
        'year', 'yr', 'date', 'time', 'period', 'month', 'day'
    ]
    
    rename_map = {}
    columns_lower = {col: col.lower().strip() for col in df.columns}
    
    # Find location column
    location_found = False
    for col, col_lower in columns_lower.items():
        if col_lower in location_patterns or any(p in col_lower for p in location_patterns):
            rename_map[col] = 'Locations'
            location_found = True
            break
    
    # If no location column found, use first string column
    if not location_found:
        for col in df.columns:
            if df[col].dtype == 'object':
                rename_map[col] = 'Locations'
                break
    
    # Find year column
    year_found = False
    for col, col_lower in columns_lower.items():
        if col_lower in year_patterns or 'year' in col_lower:
            rename_map[col] = 'YEAR'
            year_found = True
            break
    
    # If no year column, try to extract year from date-like columns or create from index
    if not year_found:
        for col in df.columns:
            # Check if column looks like a date
            try:
                sample = str(df[col].iloc[0]) if len(df) > 0 else ''
                if '/' in sample or '-' in sample:
                    # Try to parse as date
                    df['YEAR'] = pd.to_datetime(df[col], errors='coerce').dt.year
                    year_found = True
                    break
            except:
                pass
    
    # If still no year, create a synthetic year column
    if not year_found and 'YEAR' not in df.columns:
        df['YEAR'] = 2024  # Default year
    
    # Apply column renames
    if rename_map:
        df = df.rename(columns=rename_map)
    
    # Normalize other optional columns
    optional_mappings = {
        'doy': 'DOY', 'day_of_year': 'DOY',
        't2m': 'T2M', 'temp': 'T2M', 'temperature': 'T2M', 'avg_temp': 'T2M',
        't2m_max': 'T2M_MAX', 'temp_max': 'T2M_MAX', 'max_temp': 'T2M_MAX',
        't2m_min': 'T2M_MIN', 'temp_min': 'T2M_MIN', 'min_temp': 'T2M_MIN',
        'rh2m': 'RH2M', 'humidity': 'RH2M', 'relative_humidity': 'RH2M',
        'prectotcorr': 'PRECTOTCORR', 'precipitation': 'PRECTOTCORR', 
        'rainfall': 'PRECTOTCORR', 'rain': 'PRECTOTCORR',
        'ws2m_max': 'WS2M_MAX', 'wind_speed': 'WS2M_MAX', 'wind': 'WS2M_MAX',
        'lat': 'LAT', 'latitude': 'LAT',
        'long': 'LONG', 'lon': 'LONG', 'longitude': 'LONG',
    }
    
    rename_map2 = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in optional_mappings and col != optional_mappings[col_lower]:
            rename_map2[col] = optional_mappings[col_lower]
    
    if rename_map2:
        df = df.rename(columns=rename_map2)
    
    return df

def validate_csv(df):
    """
    Validate CSV data with graceful fallbacks.
    Returns dict with 'valid', 'errors', 'warnings', 'missing_columns', 'found_columns', and 'is_climate_data'
    """
    # Climate-specific columns that indicate this is climate data
    CLIMATE_COLUMNS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'RH2M', 'PRECTOTCORR', 'WS2M_MAX', 'QV2M', 
                       'ALLSKY_SFC_UV_INDEX', 'T2MDEW', 'PS', 'WD2M']
    
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_columns': [],
        'found_columns': list(df.columns),
        'is_climate_data': False
    }
    
    # Check if this is climate data (has at least 3 climate columns)
    climate_cols_found = sum(1 for col in CLIMATE_COLUMNS if col in df.columns)
    result['is_climate_data'] = climate_cols_found >= 3
    
    # Check core required columns
    for col in REQUIRED_COLUMNS['core']:
        if col not in df.columns:
            # If 'Locations' is missing, try common alternatives
            if col == 'Locations':
                loc_alts = ['LOCATION', 'location', 'City', 'CITY', 'Name', 'NAME']
                found_alt = next((alt for alt in loc_alts if alt in df.columns), None)
                if found_alt:
                    df['Locations'] = df[found_alt]
                else:
                    result['valid'] = False
                    result['errors'].append(f"Missing required column: {col}")
            else:
                result['valid'] = False
                result['errors'].append(f"Missing required column: {col}")
    
    # Only warn about optional columns if this appears to be climate data
    if result['is_climate_data']:
        for col in REQUIRED_COLUMNS['optional']:
            if col not in df.columns:
                result['warnings'].append(f"Missing optional column: {col} (will use defaults)")
                result['missing_columns'].append(col)
    
    # Check for empty dataframe
    if len(df) == 0:
        result['valid'] = False
        result['errors'].append("CSV file is empty")
    
    # Add helpful message if validation failed
    if not result['valid']:
        result['errors'].append(f"Found columns: {', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
    
    return result

def fill_missing_columns(df):
    """Fill missing optional columns with default values"""
    defaults = {
        'DOY': 1,
        'T2M': 25.0,
        'T2M_MAX': 30.0,
        'T2M_MIN': 20.0,
        'RH2M': 50.0,
        'PRECTOTCORR': 0.0,
        'WS2M_MAX': 5.0,
        'QV2M': 10.0  # Specific humidity (g/kg)
    }
    
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
    
    return df

def load_data_from_upload(file_content, filename):
    """
    Load and validate data from uploaded file content.
    Returns dict with 'success', 'data', 'validation', and 'message'
    """
    try:
        # Try to read as CSV
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8')
        
        df = pd.read_csv(io.StringIO(file_content))
        
        # Normalize column names (handle case variations and common alternatives)
        df = normalize_columns(df)
        
        # Validate the data
        validation = validate_csv(df)
        
        # Try to convert all potential numeric columns
        for col in df.columns:
            if col not in ['Locations', 'YEAR', 'YEARS', 'LOCATION']:
                # Attempt conversion
                converted = pd.to_numeric(df[col], errors='coerce')
                # If the conversion yields mostly numbers, keep it
                if converted.notna().sum() > len(df) * 0.5:
                    df[col] = converted
        
        # Also handle common Month column
        month_cols = ['month', 'MONTH', 'Month']
        for col in month_cols:
            if col in df.columns and 'DOY' not in df.columns:
                df['DOY'] = (pd.to_numeric(df[col], errors='coerce') - 1) * 30 + 1 # Rough conversion for monthly grouping
        
        # Replace -999 with NaN
        df.replace(-999, np.nan, inplace=True)
        
        # Clean up data types to prevent comparison errors
        if 'YEAR' in df.columns:
            df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce').fillna(2024).astype(int)
        if 'Locations' in df.columns:
            df['Locations'] = df['Locations'].astype(str).fillna('Unknown')
        
        return {
            'success': True,
            'data': df,
            'validation': validation,
            'message': f'Successfully loaded {len(df)} records from {filename}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'validation': {'valid': False, 'errors': [str(e)]},
            'message': f'Error reading file: {str(e)}'
        }

def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")
    
    df = pd.read_csv(CSV_PATH)
    # Replace -999 with NaN for processing
    df.replace(-999, np.nan, inplace=True)
    return df

def get_locations(df):
    return sorted(df['Locations'].unique().tolist())

def get_data_metadata(df):
    """Detect if data is climate and identify primary numeric columns for display"""
    climate_cols = ['PRECTOTCORR', 'T2M', 'RH2M', 'WS2M_MAX', 'T2M_MAX', 'T2M_MIN']
    found_climate = [c for c in climate_cols if c in df.columns]
    is_climate = len(found_climate) >= 3
    
    # Identify primary columns to show in cards/charts
    if is_climate:
        return {
            'is_climate': True,
            'primary': 'PRECTOTCORR',
            'secondary': 'T2M',
            'tertiary': 'RH2M',
            'quaternary': 'WS2M_MAX',
            'labels': {
                'primary': 'Rainfall (mm)',
                'secondary': 'Temperature (°C)',
                'tertiary': 'Humidity (%)',
                'quaternary': 'Wind Speed (m/s)'
            }
        }
    
    # Generic data: find first 2-3 numeric columns that aren't metadata
    exclude = ['YEAR', 'Locations', 'DOY', 'LAT', 'LONG', 'index', 'Unnamed: 0']
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    
    primary = numeric_cols[0] if len(numeric_cols) > 0 else None
    secondary = numeric_cols[1] if len(numeric_cols) > 1 else None
    
    return {
        'is_climate': False,
        'primary': primary,
        'secondary': secondary,
        'labels': {
            'primary': primary if primary else 'Value',
            'secondary': secondary if secondary else ''
        }
    }

def get_stats_summary(df, location, year_range=None):
    filtered_df = df[df['Locations'] == location]
    if year_range:
        filtered_df = filtered_df[(filtered_df['YEAR'] >= year_range[0]) & (filtered_df['YEAR'] <= year_range[1])]
    
    meta = get_data_metadata(df)
    
    summary = {
        'is_climate': meta['is_climate'],
        'labels': meta['labels']
    }
    
    if meta['is_climate']:
        summary.update({
            'avg_temp': round(filtered_df['T2M'].mean(), 2) if 'T2M' in filtered_df.columns else 0,
            'max_temp': round(filtered_df['T2M_MAX'].max(), 2) if 'T2M_MAX' in filtered_df.columns else 0,
            'min_temp': round(filtered_df['T2M_MIN'].min(), 2) if 'T2M_MIN' in filtered_df.columns else 0,
            'total_rainfall': round(filtered_df['PRECTOTCORR'].sum(), 2) if 'PRECTOTCORR' in filtered_df.columns else 0,
            'avg_humidity': round(filtered_df['RH2M'].mean(), 2) if 'RH2M' in filtered_df.columns else 0,
            'avg_wind_speed': round(filtered_df['WS2M_MAX'].mean(), 2) if 'WS2M_MAX' in filtered_df.columns else 0
        })
    else:
        # General data: return all available numeric columns summarized
        exclude = ['YEAR', 'Locations', 'DOY', 'LAT', 'LONG', 'index', 'Unnamed: 0']
        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
        metrics = []
        for col in numeric_cols[:4]:
            metrics.append({
                'label': col,
                'total': round(float(filtered_df[col].sum()), 2) if not pd.isna(filtered_df[col].sum()) else 0,
                'avg': round(float(filtered_df[col].mean()), 2) if not pd.isna(filtered_df[col].mean()) else 0
            })
        summary['metrics'] = metrics
        summary['record_count'] = len(filtered_df)
        
    return summary

def get_annual_trends(df, location):
    filtered_df = df[df['Locations'] == location]
    meta = get_data_metadata(df)
    
    agg_dict = {}
    if meta['primary']: agg_dict[meta['primary']] = 'sum'
    if meta['secondary']: agg_dict[meta['secondary']] = 'mean'
    
    annual_data = filtered_df.groupby('YEAR').agg(agg_dict).reset_index()
    
    return {
        'years': annual_data['YEAR'].tolist(),
        'primary_data': annual_data[meta['primary']].round(2).tolist() if meta['primary'] else [],
        'secondary_data': annual_data[meta['secondary']].round(2).tolist() if meta['secondary'] else [],
        'labels': meta['labels']
    }

def get_monthly_averages(df, location, year):
    # Year-specific monthly averages
    filtered_df = df[(df['Locations'] == location) & (df['YEAR'] == year)].copy()
    meta = get_data_metadata(df)
    
    # If no DOY, assume data might be monthly already or just group by everything
    if 'DOY' in filtered_df.columns:
        filtered_df['Month'] = pd.to_datetime(filtered_df['DOY'] - 1, unit='D', origin=pd.Timestamp(f'{year}-01-01')).dt.month
    else:
        # If no DOY but we have records, we might need another way to get months. 
        # For now, let's just return what we can.
        return {
            'months': [], 'data': [], 'labels': meta['labels']
        }
        
    agg_dict = {}
    if meta['primary']: agg_dict[meta['primary']] = 'sum'
    if meta['secondary']: agg_dict[meta['secondary']] = 'mean'
    
    if not agg_dict:
        return {'months': [], 'data': [], 'labels': meta['labels']}

    monthly_data = filtered_df.groupby('Month').agg(agg_dict).reset_index()
    
    months_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    return {
        'months': [months_names[m-1] for m in monthly_data['Month']],
        'primary_data': monthly_data[meta['primary']].round(2).tolist() if meta['primary'] else [],
        'secondary_data': monthly_data[meta['secondary']].round(2).tolist() if meta['secondary'] else [],
        'labels': meta['labels']
    }
