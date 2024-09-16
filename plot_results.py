import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import get_read_blocks as grb
import yfinance as yf
from dotenv import load_dotenv
import os


load_dotenv()                                               # Load environment variables from .env file
apiKey = os.getenv('API_KEY')                               # Etherscan API key             
csv_file_path = 'block_data.csv'                            # Path to the block data CSV file
# csv_file_path = 'post_June_data.csv'                      # Path to the block data CSV file
date_file_path = 'date_vs_opening_blocks.csv'               # Path to the date CSV file


grb.sort_csv(csv_file_path)                                 # Sort the CSV file
df = grb.custom_parse_csv(csv_file_path)                    # Read the CSV file with custom parsing

first_block_number = int(df.iloc[0].BlockNumber)
last_block_number = int(df.iloc[-1].BlockNumber) + 7200     # 7200 blocks to roughly add a day
date_df = grb.get_opening_blocks(date_file_path, first_block_number, last_block_number, apiKey)
bd_dictionary = grb.block_to_date_mapping(date_df)

# Ensure 'BlobLengths' is read as string and split into individual blob lengths
df['BlobLengths'] = df['BlobLengths'].apply(lambda x: x if isinstance(x, list) else [0])
df['BlockNumber'] = df['BlockNumber'].astype(int)
total_blocks = len(df['BlobLengths']) + 1
print("Total Blocks:", total_blocks)
df['Date'] = df['BlockNumber'].apply(lambda x: grb.assign_date(x, bd_dictionary))
exploded_df = df.explode('BlobLengths')                     # Explode the BlobLengths column into individual rows
exploded_df['BlockNumber'] = exploded_df['BlockNumber'].astype(int)
# print(exploded_df)


# Filtering 
zero_blob_df = exploded_df[exploded_df['BlobLengths'] == 0]
total_blocks_per_day = df.groupby('Date').size()
zero_blob_blocks_per_day = zero_blob_df.groupby('Date').size()
percentage_zero_blobs = (zero_blob_blocks_per_day / total_blocks_per_day) * 100
percentage_zero_blobs_df = percentage_zero_blobs.reset_index(name='NoBlobUsage')

non_zero_blobs_df = exploded_df[exploded_df['BlobLengths'] > 0]
total_btx_per_day = non_zero_blobs_df.groupby('Date').size()  
# print(total_BTXs_per_day)
# one_blob_df = exploded_df[exploded_df['BlobLengths'] == 1]
# one_blob_df = one_blob_df.groupby('Date').size()  
total_blobs_per_day = non_zero_blobs_df.groupby('Date')['BlobLengths'].sum()        
mean_blob_usage_per_btx = total_blobs_per_day / total_btx_per_day
# mean_blob_usage_per_btx = one_blob_df / total_btx_per_day * 100
mean_blob_usage_per_btx_df = mean_blob_usage_per_btx.reset_index(name='MeanBlobUsage')

# # Rate of one blob BTXs per day
# one_blob_df = exploded_df[exploded_df['BlobLengths'] == 1]                          
# total_one_blob_per_day = one_blob_df.groupby('Date').size()  
# mean_one_blob_usage_per_btx = total_one_blob_per_day / total_btx_per_day * 100                                           

mean_blob_usage_per_day_df = exploded_df.groupby('Date')['BlobLengths'].mean().reset_index()
mean_blob_usage_per_day_df.rename(columns={'BlobLengths': 'MeanBlobUsage'}, inplace=True)
mean_blob_usage_per_day_df['Date'] = pd.to_datetime(mean_blob_usage_per_day_df['Date'])


# Create subplots (2x2 layout)
fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

# Plot Percentage of Zero Blob Blocks Over Time
axs[0, 0].plot(percentage_zero_blobs_df['Date'], percentage_zero_blobs_df['NoBlobUsage'], marker='o', linestyle='-')
axs[0, 0].set_title('Percentage of Blocks with Zero Blobs Over Time')
axs[0, 0].set_ylabel('Percentage of Zero Blob Blocks (%)')

# Plot Total BTXs Over Time
axs[0, 1].plot(total_btx_per_day.index, total_btx_per_day, marker='o', linestyle='-', color='r')
axs[0, 1].set_title('Total BTXs Over Time')
axs[0, 1].set_ylabel('Total BTXs')

# Plot Mean Blob Usage per BTX
axs[1, 0].plot(mean_blob_usage_per_btx_df['Date'], mean_blob_usage_per_btx_df['MeanBlobUsage'], marker='o', linestyle='-', color='b')
axs[1, 0].set_title('Mean Blob Usage Per BTX')
axs[1, 0].set_ylabel('Mean Blob Usage')

# Plot Mean Blob Usage Over Time
axs[1, 1].plot(mean_blob_usage_per_day_df['Date'], mean_blob_usage_per_day_df['MeanBlobUsage'], marker='o', linestyle='-', color='b')
axs[1, 1].set_title('Mean Blob Demand Per Blocks')
axs[1, 1].set_xlabel('Date')
axs[1, 1].set_ylabel('Mean Blob Usage')

# Format the x-axis labels for all plots
for ax in axs.flat:
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# Get historical price data using yfinance: Better to write it in try/catch block later!
eth_ticker = yf.Ticker("ETH-USD")
# eth_ticker = yf.Ticker("BTC-USD")
eth_prices = eth_ticker.history(start=date_df.iloc[0]['Date'], end=date_df.iloc[-1]['Date'])
# Extract open and close prices
eth_prices['Date'] = eth_prices.index
price_data_df = eth_prices[['Date', 'Open', 'Close', 'Volume']].reset_index(drop=True)
# print(price_data_df)

blob_usage_df = mean_blob_usage_per_btx_df                  # mean_blob_usage_per_day_df              
blob_usage_df['Date'] = pd.to_datetime(blob_usage_df['Date'])
blob_usage_df['Date'] = blob_usage_df['Date'].dt.tz_localize(None)
price_data_df['Date'] = pd.to_datetime(price_data_df['Date'])
price_data_df['Date'] = price_data_df['Date'].dt.tz_localize(None)

merged_df = pd.merge(blob_usage_df, price_data_df, on='Date', how='inner')
# print(merged_df)
correlation_matrix = merged_df[['MeanBlobUsage', 'Open', 'Close', 'Volume']].corr()
print(correlation_matrix)

# Create a new figure
fig, ax1 = plt.subplots(figsize=(10, 6))
# Plot MeanBlobUsage on primary y-axis
ax1.plot(blob_usage_df['Date'], blob_usage_df['MeanBlobUsage'], 'b-', marker='o', label='Mean Blob Usage')
ax1.set_xlabel('Date')
ax1.set_ylabel('Mean Blob Usage Per BTX', color='b')
ax1.tick_params(axis='y', labelcolor='b')
# Create a twin axes sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(price_data_df['Date'], price_data_df['Close'], 'r-', marker='o', label='Close Price')
ax2.set_ylabel('Close Price (USD)', color='r')
ax2.tick_params(axis='y', labelcolor='r')
# Title and layout adjustments
fig.suptitle('Mean Blob Usage and ETH Closing Prices')
fig.tight_layout()
plt.show()


percentage_zero_blobs_df['Date'] = pd.to_datetime(percentage_zero_blobs_df['Date'])
percentage_zero_blobs_df['Date'] = percentage_zero_blobs_df['Date'].dt.tz_localize(None)
merged_df = pd.merge(percentage_zero_blobs_df, price_data_df, on='Date', how='inner')
correlation_matrix = merged_df[['NoBlobUsage', 'Open', 'Close', 'Volume']].corr()
print(correlation_matrix)

# Create a new figure
fig, ax1 = plt.subplots(figsize=(10, 6))
# Plot MeanBlobUsage on primary y-axis
ax1.plot(percentage_zero_blobs_df['Date'], percentage_zero_blobs_df['NoBlobUsage'], 'b-', marker='o', label='Zero Blob Usage')
ax1.set_xlabel('Date')
ax1.set_ylabel('Percentage of Zero Blob Blocks (%)', color='b')
ax1.tick_params(axis='y', labelcolor='b')
# Create a twin axes sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(price_data_df['Date'], price_data_df['Close'], 'r-', marker='o', label='Close Price')
ax2.set_ylabel('Close Price (USD)', color='r')
ax2.tick_params(axis='y', labelcolor='r')
# Title and layout adjustments
fig.suptitle('Zero Blob Usage and ETH Closing Prices')
fig.tight_layout()
plt.show()


# Calculate percentages
counts = exploded_df['BlobLengths'].value_counts() 
counts = counts.sort_index()
input_rate = counts[1:].sum() / total_blocks
print("BTX rate per block:", input_rate)
empty_blocks = counts[0] / total_blocks
print("Percentage of blocks without BTXs:", empty_blocks)
blob_usage = counts[1:] / counts[1:].sum() * 100
print(blob_usage)
blob_usage_avg = np.dot(np.arange(1, len(counts)), blob_usage.values.reshape(-1, 1))
print(blob_usage_avg / 100)
# counts = exploded_df['BlobLengths'].value_counts(normalize=True) * 100
# counts = counts.sort_index()
# print(counts)



# Plot the histogram
plt.figure(figsize=(10, 6))
plt.bar(blob_usage.index.astype(int), blob_usage, width=0.8, edgecolor='black', align='center')
plt.title('Percentage Histogram of Blob Usage in BTXs After 1st of June')
plt.ylim(0, 100)
plt.xlabel('Blob usage in BTXs')
plt.ylabel('Percentage')
plt.xticks(blob_usage.index.astype(int))  # Ensure bars are centered at integer values
# plt.grid(True)
plt.show()
