# RFM Calculation and CLTV Prediction with FLO Dataset 

## Business Problem
FLO aims to segment its customers and develop marketing strategies based on these segments. To achieve this, customer behaviors will be identified, and groups will be formed based on these behavioral clusters.

## Dataset Story
The dataset consists of information derived from the past shopping behaviors of customers who made their last purchases in the years 2020 - 2021 through an OmniChannel approach (shopping both online and offline).

## Column Descriptions

- `master_id`: Unique customer number.
- `order_channel`: The channel used for shopping on the platform (Android, iOS, Desktop, Mobile, Offline).
- `last_order_channel`: The channel used for the most recent purchase.
- `first_order_date`: The date of the customer's first purchase.
- `last_order_date`: The date of the customer's last purchase.
- `last_order_date_online`: The date of the customer's last online purchase.
- `last_order_date_offline`: The date of the customer's last offline purchase.
- `order_num_total_ever_online`: The total number of online purchases made by the customer.
- `order_num_total_ever_offline`: The total number of offline purchases made by the customer.
- `customer_value_total_ever_offline`: The total amount paid by the customer for offline purchases.
- `customer_value_total_ever_online`: The total amount paid by the customer for online purchases.
- `interested_in_categories_12`: List of categories the customer shopped in the last 12 months.

