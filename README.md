# EIP-4844
Blob usage in transactions


We have collected blob usage in Ethereum blocks from May 1st to August 31st, 2024, which corresponds to Ethereum blocks from #19771560 to #20651993. The figures below (plot_results.py) show the daily rate of zero blob blocks (upper-left), BTXs issued over time (upper-right), mean blob usage per BTX (lower-left) and mean blob usage per block considering zero blob blocks as well (lower-right). During this time, almost 39% of blocks were devoid of blobs while mean blob-carrying transaction (BTX) rate was 1.19 per block with mean blob usage of 1.93 per BTX. However, as figures demonstrate, a shift in blob usage is evident near June 1st, which is more apparent in the upper figures.
 
![image](https://github.com/user-attachments/assets/609923d2-cb52-4fa5-b2ce-305f8a772fe5)

To investigate the cause, we compared the fluctuations in blob usage with those of Ethereum’s price. Our analysis involved correlating aggregated data with daily close and open prices, as well as trading volume.
During this time frame, the highest correlation was observed with closing prices, with coefficients falling in the range of 0.1 to 0.15. Surprisingly, the correlation appears to be low, suggesting that price might not have a significant impact on blob usage. However, we’ll delve into why this isn’t necessarily the case later. Figure below illustrates the daily rate of zero blob blocks alongside Ethereum’s closing prices.

![image](https://github.com/user-attachments/assets/b61f59d8-f176-4ca0-9a17-43e8c5b6ed9f)

As observed, around the beginning of June, there was a price surge driven by speculation about the acceptance of Ethereum ETFs. They were later officially approved on July 23rd, though. Interestingly, the dynamics remained consistent after June even in August, despite the price being lower than that of May. This suggests that additional factors might be at play beyond price alone. Perhaps demand remained steady during this period. However, we’re not entirely certain whether other variables are influencing the situation. For instance, around June 1st, Optimism adopted Bitly compression. Nonetheless, according to l2beat, Optimism holds only a modest 16% share of the market.

It is worth noting that blob usage per BTX decreased near both Ethereum ETF deadlines, indicating that rollups shifted toward smaller BTXs with a higher issuance rate (faster transaction issuance).

![image](https://github.com/user-attachments/assets/f7aeb7d1-dde9-4283-b166-06680bee5cd3)
 
Due to the clear shift in blob usage, we decided to further analyze the results before and after 1st of June separately. Before 1st of June, 52% of blocks were devoid of blocks with mean blob-carrying transaction (BTX) rate of 0.76 per block with mean blob usage of 2.2 per BTX. After 1st of June, 34% of blocks were devoid of blocks with mean blob-carrying transaction (BTX) rate of 1.34 per block with mean blob usage of 1.88 per BTX. Figure below shows how the percentage of BTXs with different blob usage changed. While rate of BTXs with 1, 2 and 4 blobs stayed almost the same, most of the rate of 6-blob BTXs before 1st of June has been dispersed between 3 and 5 blob BTXs. 

Due to the clear shift in blob usage, we decided to analyze the results before and after June 1st separately. Prior to June 1st, 52% of blocks lacked any BTXs while the mean BTX rate was 0.76 per block with mean blob usage of 2.2 per BTX. After June 1st, 34% of blocks still lacked any BTXs, but the mean BTX rate increased to 1.34 per block while mean blob usage decreased to 1.88 per BTX. The figures below illustrate how the percentage of BTXs with different blob usage changed. Notably, while the rates of BTXs with 1, 2, and 4 blobs remained relatively stable, the distribution of 6-blob BTXs before June 1st shifted toward 3 and 5 blob BTXs.

![image](https://github.com/user-attachments/assets/e08f4eba-0303-49a7-9a52-0cadf8efc15d)

Upon separating the data and examining its correlation with price, some interesting patterns emerge. The absolute correlation between zero blob blocks and prices peaked when considering open prices, with a coefficient of -0.47. However, it is worth noting that the pre-June dataset covers only one month, which isn’t a very extensive timeframe. After June 1st, correlations still peak with open prices. Correlation between daily open prices and zero blob blocks is 0.3 while it is 0.54 with mean blob usage per BTX. Hence as prices increase, BTXs tend to become larger while at the same time a bit less frequent.


