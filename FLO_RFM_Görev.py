######################## ##################
# Customer Segmentation with RFM
######################## ##################

######################## ##################
# Business Issue
######################## ##################
# FLO wants to divide its customers into segments and determine marketing strategies according to these segments.
# In this regard, customers' behaviors will be defined and groups will be created according to these behavioral clusters.

######################## ##################
# Dataset Story
######################## ##################
# The data set is based on historical shopping behavior of customers who made their last purchases (both online and offline shopping) on OmniChannel in 2020 - 2021.
# consists of the information obtained.

# master_id: Unique customer number
#order_channel: Which channel of the shopping platform is used (Android, iOS, Desktop, Mobile, Offline)
# last_order_channel : Channel where the last purchase was made
#first_order_date: Customer's first purchase date
# last_order_date : Customer's last shopping date
# last_order_date_online : The customer's last shopping date on the online platform
# last_order_date_offline : The customer's last shopping date on the offline platform
# order_num_total_ever_online : Total number of purchases made by the customer on the online platform
# order_num_total_ever_offline : Total number of purchases made by the customer offline
# customer_value_total_ever_offline : The total price the customer paid for offline purchases
# customer_value_total_ever_online : The total price the customer paid for online purchases
#interest_in_categories_12 : List of categories the customer has shopped in the last 12 months

import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
import datetime as dt


df = pd.read_csv("Miuul_CRM/Datasets/flo_data_20k.csv")
df.head(10)
df.columns
df.describe()
df.isnull().sum()
df.info()

df.info()


df["total_transaction"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

date_columns = df.columns[df.columns.str.contains("date")]
for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')
# df["last_order_date"] = df["last_order_date"].apply(pd.to_datetime)



df.groupby("order_channel").agg({"master_id": "count",
                                 "total_price": "mean",
                                 "total_transaction": "mean"})


df.sort_values("total_price",ascending=False).head(10)


df.sort_values("total_transaction",ascending=False).head(10)


def data_preperation(df):
    df["total_transaction"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
    date_columns = df.columns[df.columns.str.contains("date")]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')

# Calculation of RFM Metrics

# The analysis date is 2 days after the date of the last purchase in the data set.
df["last_order_date"].max()
analiz_date = dt.datetime(2021, 6, 1)

# customer_id, recency, frequnecy ve monetary değerlerinin yer aldığı yeni bir rfm dataframe
rfm = df.groupby("master_id").agg({"last_order_date": lambda x: (analiz_date - x.max()).days,
                                   "total_transaction": lambda x: x,
                                   "total_price": lambda x: x})
rfm.columns = ["recency", "frequency", "monetary"]

# Calculating RF and RFM Scores

# Converting Recency, Frequency and Monetary metrics into scores between 1-5 with the help of qcut and
# Saving these scores as recency_score, frequency_score and monetary_score

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, [5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method='first'),5,[1,2,3,4,5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"],5,[1,2,3,4,5])

# recency_score ve frequency_score’u tek bir değişken olarak ifade edilmesi ve RF_SCORE olarak kaydedilmesi
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm.info()

#  RF Skorlarının Segment Olarak Tanımlanması


## To make the created RFM scores more explainable, define segments and convert RF_SCORE into segments with the help of the defined seg_map.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)


# Recency, frequency and monetary averages of segments

rfm.groupby("segment").agg({"recency": "mean",
                            "frequency": "mean",
                            "monetary": "mean"})


# Find the customers in the relevant profile for 2 cases with the help of RFM analysis and save the customer IDs to CSV.

# a. FLO is adding a new women's shoe brand. The product prices of the included brand are above general customer preferences. Therefore the brand
# We want to be able to specifically contact customers with the profile that would be interested in # promotion and product sales. These customers are loyal and
# It was planned to have shoppers from the # women category. Enter the ID numbers of the customers into the csv file new_brand_target_customer_id.cvs
# Save as #.

rfm_filter = rfm["segment"]
result_df = pd.merge(df, rfm_filter, on="master_id", how="left")

women_and_loyal_customer = result_df[(result_df["segment"] == "loyal_customers") & (result_df["interested_in_categories_12"].apply(lambda x: "KADIN" in x))]
women_and_loyal_customer["master_id"].to_csv("women_and_loyal_customer.csv")

# b. Nearly 40% discount is planned for Men's and Children's products. Those who have been good customers in the past but have been for a long time are interested in categories related to this sale.
# New customers who have not made purchases are specifically targeted. Save the IDs of customers in the appropriate profile to the csv file discount_target_customer_ids.csv
# save as #

cant_loose_and_at_risk_df = result_df[(result_df["segment"] == "at_Risk") | (result_df["segment"] == "cant_loose")]

reliant_customers = cant_loose_and_at_risk_df[cant_loose_and_at_risk_df["interested_in_categories_12"].apply(lambda x: ("COCUK" in x) | ("ERKEK" in x))]

reliant_customers["master_id"].to_csv("Sale_customers.csv",index=False)






