import pandas as pd
from datetime import datetime
import os
import requests


# Function to get block timestamp from Etherscan
def get_block_date(block_number, apiKey):
    url = f"https://api.etherscan.io/api"
    params = {
        'module': 'block',
        'action': 'getblockreward',
        'blockno': block_number,
        'apikey': apiKey
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    if result['status'] == '1':
        timestamp = int(result['result']['timeStamp'])
        return pd.to_datetime(timestamp, unit='s').date()
        # return datetime.utcfromtimestamp(timestamp).date()
    else:
        print(f"Error fetching timestamp for block {block_number}: {result['message']}")
        return None
    
# Function to load existing date data
def load_existing_date_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=['Date', 'BlockNumber'])
    
    date_df = pd.read_csv(file_path)
    date_df['Date'] = pd.to_datetime(date_df['Date'], errors='coerce')
    return date_df

# Function to sort CSV content based on block number
def sort_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    # Ensure 'BlockNumber' is read as integer
    df['BlockNumber'] = pd.to_numeric(df['BlockNumber'], errors='coerce')
    # Sort the dataframe by 'BlockNumber'
    df_sorted = df.sort_values(by='BlockNumber')
    df_sorted.to_csv(csv_file_path, index=False)
    print("CSV file sorted and saved successfully.")

# Function to parse the CSV content
def custom_parse_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        headers = file.readline().strip().split(',')
        for line in file:
            parts = line.strip().split(',')
            block_number = parts[0]
            # Clean and convert blob lengths
            blob_lengths = [int(x.strip().replace('"', '')) for x in parts[1:]] if len(parts) > 1 else [0]
            data.append([block_number, blob_lengths])
    return pd.DataFrame(data, columns=headers)

# Assign dates to blocks based on the mapping
def assign_date(block_number, block_to_date_mapping):
    for start_block, end_block, date in block_to_date_mapping:
        if start_block <= block_number <= end_block:
            return date
    return None

# Function to get the block number at a specific timestamp
def get_block_number_by_timestamp(timestamp, apiKey):
    url = f"https://api.etherscan.io/api"
    params = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': timestamp,
        'closest': 'before',
        'apikey': apiKey
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    if result['status'] == '1':
        return int(result['result'])
    else:
        print(f"Error fetching block number: {result['message']}")
        return None

# Function to get the dates and their opening blocks based on the range provided 
def get_opening_blocks(date_file_path, first_block_number, last_block_number, apiKey):

    # Load existing date data
    date_df = load_existing_date_data(date_file_path)
    # If DataFrame is empty, handle it appropriately
    if date_df.empty:
        existing_dates = set()
    else:
        existing_dates = set(date_df['Date'].dt.date)

    # Define your date range
    first_block_date = get_block_date(first_block_number, apiKey)
    last_block_date = get_block_date(last_block_number, apiKey)
    date_range = pd.date_range(start=first_block_date, end=last_block_date)

    # Find missing dates
    missing_dates = [date for date in date_range if date.date() not in existing_dates]
    # Create a list to hold new entries
    new_entries = []
    # Fetch and prepare missing data
    for date in missing_dates:
        timestamp = int(date.timestamp())
        block_number = get_block_number_by_timestamp(timestamp, apiKey)
        print(date, block_number)
        if block_number is not None:       
            new_entries.append({
                'Date': date,
                'BlockNumber': block_number + 1
            })

    # Convert new entries to a DataFrame
    new_entries_df = pd.DataFrame(new_entries)
    # Append new entries to the existing DataFrame
    date_df = pd.concat([date_df, new_entries_df], ignore_index=True)
    # Sort blocks by date
    date_df = date_df.sort_values('Date')
    # Save the updated date data to CSV
    date_df.to_csv(date_file_path, index=False)
    return date_df

# Create a dictionary for block number ranges to dates
def block_to_date_mapping(date_df):
    bd_dictionary = []
    for i in range(len(date_df) - 1):
        start_block = date_df.iloc[i]['BlockNumber']
        end_block = date_df.iloc[i + 1]['BlockNumber'] - 1
        date = date_df.iloc[i]['Date']
        bd_dictionary.append((start_block, end_block, date))

    # Include the last date range
    last_block = date_df.iloc[-1]['BlockNumber']
    last_date = date_df.iloc[-1]['Date']
    bd_dictionary.append((last_block, last_block, last_date))
    return bd_dictionary
    # Convert mapping to DataFrame for merging
    # mapping_df = pd.DataFrame(bd_dictionary, columns=['StartBlock', 'EndBlock', 'Date'])
    # return mapping_df

