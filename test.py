import datetime
import urllib.parse

import pandas as pd
import plotly
import plotly.graph_objects as go
from pymongo import MongoClient

host = "34.64.209.3"
port = "27017"
username = urllib.parse.quote_plus('admin')
password = urllib.parse.quote_plus('admin')
mongo = MongoClient('mongodb://%s:%s@34.64.209.3:27017',
                    username='admin',
                    password='admin',
                    authSource='Ttareungi')
# mongo = MongoClient(host, int(port))
database = mongo.Ttareungi
print(database)
print(plotly.__version__)

#
# def find_item(mongo, condition=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True,
#                                                   cursor_type=CursorType.EXHAUST)
#     return result
# db.rental_office_usage.aggregate([{$group:{_id:"$rental_date(month)",total:{$sum:"$number_of_rentals"}}},
#                                   {$project: {_id: 0, date: "$_id", total:1}}, {$sort:{date:-1}}])

# db.new_sub.aggregate([{$group:{_id:"$sub_date",total:{$sum:"$sub_num"}}},
#                       {$project: {_id: 0, registers: "$_id", total:1}}, {$sort:{registers:1}}])
# db.rental_office_usage.aggregate([{$group:{_id:"$rental_office_id",avg:{$avg:"$number_of_rentals"},"office_name":{"$first":"$rental_office_name"}}},
#                   {$project: {_id:0, office_id:"$_id", office_name:"$office_name", avg:1}},{$sort:{avg:-1}}])
# db.rental_history.aggregate([{$match:{}},{$group:{_id:{"year":{"$substr":["$rental_date",0,4]},"month":{"$substr":["$rental_date",5,2]},"rental":"$rental_office_id"},"count":{$sum:1},"name":{$first:"$rental_office_name"}}},{$group:{_id:"$_id.rental","avg":{$avg:"$count"}}},{$sort:{_id:1}}])
# db.rental_history.aggregate([{$group:{_id:{"year":{"$substr":["$return_date",0,4]},"month":{"$substr":["$return_date",5,2]},"return":"$return_office_id"},"count":{$sum:1},"name":{$first:"$rental_office_name"}}},{$group:{_id:"$_id.return","avg":{$avg:"$count"}}},{$sort:{_id:1}}])

pipe1 = [{'$group': {'_id': "$rental_date(month)", 'total': {'$sum': "$number_of_rentals"}}},
         {'$project': {'_id': 0, 'date': "$_id", 'total': 1}}, {'$sort': {'date': -1}}]

pipe2 = [{'$group': {'_id': "$sub_date", 'total': {'$sum': "$sub_num"}}},
         {'$project': {'_id': 0, 'date': "$_id", 'total': 1}}, {'$sort': {'registers': 1}}]

pipe3 = [{'$group': {'_id': "$rental_office_id",
                     'avg': {'$avg': "$number_of_rentals"},
                     "office_name": {"$first": "$rental_office_name"}}},
         {'$project': {'_id': 0, 'office_name': "$office_name", "avg": 1}}, {'$sort': {'avg': -1}}]

pipe4 = [{'$group': {'_id': {"year": {"$substr": ["$rental_date", 0, 4]}, "month": {"$substr": ["$rental_date", 5, 2]},
                             "rental": "$rental_office_id"}, "count": {'$sum': 1},
                     "name": {'$first': "$rental_office_name"}}},
         {'$group': {'_id': "$_id.rental", "avg": {"$avg": "$count"}}}, {"$sort": {"_id": 1}}]

pipe5 = [{'$group': {'_id': {"year": {"$substr": ["$return_date", 0, 4]}, "month": {"$substr": ["$return_date", 5, 2]},
                             "return": "$return_office_id"}, "count": {"$sum": 1},
                     "name": {"$first": "$rental_office_name"}}},
         {'$group': {'_id': "$_id.return", "avg": {'$avg': "$count"}}}, {'$sort': {'_id': 1}}]
# pip3꺼를 설치시기 같은 애들 평균내서 년도별 평균 내기
install_date_query = {'rental_office_id': 1, 'installation_date': 1}

location_query = {'rental_office_id': 1, 'rental_office_name': 1, 'latitude': 1, 'longitude': 1}

# -------------------------------------------------------------------------------------------

use_by_month = database.rental_office_usage.aggregate(pipe1)
new_users_by_month = database.new_sub.aggregate(pipe2)
use_avg_by_rental_office = database.rental_office_usage.aggregate(pipe3)
rental_avg_by_rental_office = database.rental_history.aggregate(pipe4)
return_avg_by_rental_office = database.rental_history.aggregate(pipe5)
install_date_of_rental_office = database.rental_office_install_date.find({}, install_date_query)
rental_office_location = database.rental_office_install_date.find({}, location_query)

rental_office_install_date = dict(
    (data['rental_office_id'], data['installation_date']) for data in install_date_of_rental_office)
rental_office_rental_num = dict()

# -------------------------------------------------------------------------------------------

# print(rental_office)
#
use_avg_by_install_date = dict()
count_by_install_date = dict()
dates = []
totals = []
date = []
registers_total = []
office_name = []
avgs = []
office_id = []
office_id_avg = []
rental_return_avg_sub = dict()
# print(new_users_by_month)
office_locations = []
# -------------------------------------------------------------------------------------------

for data in list(use_avg_by_rental_office):
    rental_office_id = data['office_id']
    install_date = rental_office_install_date[rental_office_id]
    if install_date is None:
        continue
    year = install_date[:4]
    count_by_install_date[year] = count_by_install_date.get(year, 0) + 1
    use_avg_by_install_date[year] = use_avg_by_install_date(year, 0) + data["avg"]

for year in list("2015", "2016", "2017", "2018", "2019", "2020", "2021"):
    if use_avg_by_install_date.get(year):
        use_avg_by_install_date[year] = use_avg_by_install_date[year] // count_by_install_date[year]

for data in list(use_by_month):
    totals.append(data['total'])
    dates.append(datetime.datetime(data['date'] // 100, data['date'] % 100, 1))

for data in list(new_users_by_month):
    registers_total.append(data['total'])
    date.append(datetime.datetime(data['date'] // 100, data['date'] % 100, 1))

for data in list(use_avg_by_rental_office):
    office_name.append(data['office_name'])
    avgs.append(data['avg'])

for data in list(rental_avg_by_rental_office):
    rental_office_id.append(data['_id'])
    avgs.append(data['avg'])
    rental_return_avg_sub[data['_id']] = data['avg']

for data in list(return_avg_by_rental_office):
    # return_office_id.append(data['_id'])
    # avgs.append(data['avg'])
    print("ID", data['_id'])
    if rental_return_avg_sub.get(data['_id']):
        print(rental_return_avg_sub[data['_id']], " - ", data['avg'], " = ")
        sub = rental_return_avg_sub[data['_id']] - data['avg']
        print("sub", sub)
        rental_return_avg_sub[data['_id']] = sub
    else:
        rental_return_avg_sub[data['_id']] = -data['avg']

for key, value in rental_return_avg_sub.items():
    print("key", key, value)
    if type(key) != str :
        office_id_avg.append(value)
        office_id.append(key)

df = pd.DataFrame(rental_office_location)
for data in list(use_avg_by_rental_office):
    office_name.append(data['office_name'])
    avgs.append(data['avg'])

# -------------------------------------------------------------------------------------------
# data1 = [go.Bar(
#     x=dates,
#     y=totals
# )]
#
# fig = go.Figure(data=data1)
# fig.show()
#
# data2 = [go.Bar(
#     y=registers_total,
#     x=date
# )]
#
# fig2 = go.Figure(data=data2)
#
# fig2.show()
#
# data3 = [go.Bar(
#     x=office_name,
#     y=avgs
# )]
#
# fig3 = go.Figure(data=data3)
#
# fig3.show()

print("id",office_name)
print("id",avgs)
data4 = [go.Bar(
    x=office_name,
    y=avgs
)]

fig4 = go.Figure(data=data4)

# fig4.show()

# pipe = [{'$group': {'_id': "$가입일자", 'total': {'$sum': "$가입 수"}}},
#         {'$project': {'_id': 0, 'registers': "$_id", 'total': 1}}, {'$sort': {'registers': 1}}]
# result = database.new_sub.aggregate(pipe)
#
# totals = []
# registers = []
# df = DataFrame(list(result))


# for data in list(result):
#     totals.append(data['total'])
#     registers.append(data['registers'])
# print(totals)
# print(registers)
# data = [go.Bar(
#     x=registers,
#     y=totals
# )]
# fig = go.Figure(data=data)
# fig.show()

##지도에 대여소 표시
## df = pd.read_csv('data/rental_office.csv', encoding='utf-8')
## df.head()
## geo_data = 'data/seoul_geo.json'
## 서울중심
# center = [37.541, 126.986]
# m = folium.Map(location=center, zoom_start=10)
## 마커 클러스터 사용
# marker_cluster = MarkerCluster().add_to(m)
# for i in df.index[:]:
#     # print(df.loc[i, 'latitude'], "and", (df.loc[i, 'latitude']))
#     # print(df.loc[i, 'longitude'], "and", (df.loc[i, 'longitude']))
#     # print(df.loc[i, 'rental_office_name'])
#     # print(i)
#     # 위도 경도 값 없을시 건너뛰기
#     if (df.loc[i, 'latitude']) and (df.loc[i, 'longitude']):
#         folium.Marker(
#             location=[df.loc[i, 'latitude'], df.loc[i, 'longitude']],
#             popup=df.loc[i, 'rental_office_name'],
#             icon=folium.Icon(color='cadetblue', icon='ok')
#         ).add_to(marker_cluster)

## 마커 표시
# for i in df.index[:]:
#     if not pd.isna(df.loc[i, '위도']) and not pd.isna(df.loc[i, '경도']):
#         folium.Marker(
#             location=[df.loc[i, '위도'], df.loc[i, '경도']],
#             popup=df.loc[i, '대여소 번호'],
#             icon=folium.Icon(color='cadetblue', icon='ok')
#         ).add_to(marker_cluster)

##원 표시
# for i in df.index[:]:
#     # print(df.loc[i,'위도'])
#     # print(df.loc[i,'경도'])
#     # print(df.loc[i, '대여소 번호'])
#     # print(i)
#     if not pd.isna(df.loc[i, '위도']) and not pd.isna(df.loc[i, '경도']):
#         folium.Circle(
#             location=[df.loc[i, '위도'], df.loc[i, '경도']],
#             tooltip=df.loc[i, '대여소 번호'],
#             radius=200
#         ).add_to(m)

## 등치맵 사용
# folium.Choropleth(
#     geo_data=geo_data,
#     data=df,
#     columns=('자치구', '대여소 번호'),
#     key_on='feature.properties.name',
#     fill_color='BuPu',
#     legend_name='자치구',
# ).add_to(m)
# html 파일로 저장
m.save("a.html")

# -------------------------------------------------------------------------------------------

# cursor=find_item(mongo,"Ttareungi","new_sub")
# pipe=[{$group:{_id:"$가입일자",total:{$sum:"$가입 수"}}}, {$project: {_id: 0, registers: "$_id", total:1}}, {$sort:{registers:1}}]
# result=database.new_sub.aggregate(pipeline)
# db.new_sub.aggregate([{$group:{_id:"$가입일자",total:{$sum:"$가입 수"}}}, {$project: {_id: 0, registers: "$_id", total:1}}, {$sort:{registers:1}}])
# { "total" : 15627, "registers" : 201912 }
# { "total" : 15407, "registers" : 202001 }
# { "total" : 21246, "registers" : 202002 }
# { "total" : 100046, "registers" : 202003 }
# { "total" : 131456, "registers" : 202004 }
# { "total" : 127535, "registers" : 202005 }
# { "total" : 110181, "registers" : 202006 }
