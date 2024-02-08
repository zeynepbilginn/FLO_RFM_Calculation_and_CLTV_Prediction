##############################################################
# BG-NBD ve Gamma-Gamma ile CLTV Prediction
##############################################################

import pandas as pd
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
import datetime as dt

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df_ = pd.read_csv("Miuul_CRM/Datasets/flo_data_20k.csv")
df = df_.copy()
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = round(low_limit)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = round(up_limit)


df.describe()

outlier_list = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", "customer_value_total_ever_online"]
for col in outlier_list:
    replace_with_thresholds(df, col)
df.describe()

df["total_transaction"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

date_columns = [col for col in df.columns if "date" in col]

for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')

df["last_order_date"].max()
analysis_date = dt.datetime(2021,6,1 )

df["recency_cltv"] = (df["last_order_date"] - df["first_order_date"]).dt.days / 7
cltv_df = df.groupby("master_id").agg({"recency_cltv": lambda x: x,
                                       "first_order_date": lambda x: (analysis_date - x.min()).days,
                                       "total_transaction": lambda x: x.astype(int),
                                       "total_price": lambda x: x})



cltv_df.columns = ["recency_cltv_weekly", "T_weekly", "frequency", "monetary_cltv_avg"]
cltv_df["monetary_cltv_avg"] = cltv_df["monetary_cltv_avg"] / cltv_df["frequency"]
cltv_df["T_weekly"] = cltv_df["T_weekly"] / 7
cltv_df = cltv_df[cltv_df["frequency"] > 1]
cltv_df.describe()


bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv_df["frequency"],
        cltv_df["recency_cltv_weekly"],
        cltv_df["T_weekly"])

cltv_df["exp_sales_3_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(3 * 4,
                                                                                   cltv_df["frequency"],
                                                                                   cltv_df["recency_cltv_weekly"],
                                                                                   cltv_df["T_weekly"])


cltv_df["exp_sales_6_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(6 * 4,
                                                                                   cltv_df["frequency"],
                                                                                   cltv_df["recency_cltv_weekly"],
                                                                                   cltv_df["T_weekly"])



cltv_df["exp_sales_6_month"].sort_values(ascending=False).head(10)

cltv_df["exp_sales_3_month"].sort_values(ascending=False).head(10)

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["frequency"],cltv_df["monetary_cltv_avg"])

cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df["frequency"],cltv_df["monetary_cltv_avg"])

cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df["frequency"],
                                   cltv_df["recency_cltv_weekly"],
                                   cltv_df["T_weekly"],
                                   cltv_df["monetary_cltv_avg"],
                                   6,
                                   freq = "W",
                                   discount_rate=0.01) #T'nin frekansını belirtir

cltv.reset_index()

cltv_final = cltv_df.merge(cltv, on="master_id", how="left")

cltv_final.sort_values("clv", ascending=False).head(20)


cltv_final["cltv_segment"] = pd.qcut(cltv_final["clv"],4,["D","C","B","A"])

cltv_final.groupby("cltv_segment").agg({"recency_cltv_weekly": "mean",
                                        "frequency": "mean",
                                        "monetary_cltv_avg": "mean"})







