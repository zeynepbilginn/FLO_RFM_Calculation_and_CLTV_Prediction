###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..

###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

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

# RFM Metriklerinin Hesaplanması

# Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi
df["last_order_date"].max()
analiz_date = dt.datetime(2021, 6, 1)

# customer_id, recency, frequnecy ve monetary değerlerinin yer aldığı yeni bir rfm dataframe
rfm = df.groupby("master_id").agg({"last_order_date": lambda x: (analiz_date - x.max()).days,
                                   "total_transaction": lambda x: x,
                                   "total_price": lambda x: x})
rfm.columns = ["recency", "frequency", "monetary"]

# RF ve RFM Skorlarının Hesaplanması (Calculating RF and RFM Scores)

#  Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çevrilmesi ve
# Bu skorları recency_score, frequency_score ve monetary_score olarak kaydedilmesi
rfm["recency_score"] = pd.qcut(rfm["recency"], 5, [5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method='first'),5,[1,2,3,4,5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"],5,[1,2,3,4,5])

# recency_score ve frequency_score’u tek bir değişken olarak ifade edilmesi ve RF_SCORE olarak kaydedilmesi
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm.info()

#  RF Skorlarının Segment Olarak Tanımlanması


# Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlama ve  tanımlanan seg_map yardımı ile RF_SCORE'u segmentlere çevirme
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


# Segmentlerin recency, frequnecy ve monetary ortalamaları

rfm.groupby("segment").agg({"recency": "mean",
                            "frequency": "mean",
                            "monetary": "mean"})


# RFM analizi yardımı ile 2 case için ilgili profildeki müşterileri bulunuz ve müşteri id'lerini csv ye kaydetme.

# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde. Bu nedenle markanın
# tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçeilmek isteniliyor. Bu müşterilerin sadık  ve
# kadın kategorisinden alışveriş yapan kişiler olması planlandı. Müşterilerin id numaralarını csv dosyasına yeni_marka_hedef_müşteri_id.cvs
# olarak kaydetme.
rfm_filter = rfm["segment"]
result_df = pd.merge(df, rfm_filter, on="master_id", how="left")

women_and_loyal_customer = result_df[(result_df["segment"] == "loyal_customers") & (result_df["interested_in_categories_12"].apply(lambda x: "KADIN" in x))]
women_and_loyal_customer["master_id"].to_csv("women_and_loyal_customer.csv")
# b. Erkek ve Çoçuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşterilerden olan ama uzun süredir
# alışveriş yapmayan ve yeni gelen müşteriler özel olarak hedef alınmak isteniliyor. Uygun profildeki müşterilerin id'lerini csv dosyasına indirim_hedef_müşteri_ids.csv
# olarak kaydetme

cant_loose_and_at_risk_df = result_df[(result_df["segment"] == "at_Risk") | (result_df["segment"] == "cant_loose")]

reliant_customers = cant_loose_and_at_risk_df[cant_loose_and_at_risk_df["interested_in_categories_12"].apply(lambda x: ("COCUK" in x) | ("ERKEK" in x))]

reliant_customers["master_id"].to_csv("Sale_customers.csv",index=False)






