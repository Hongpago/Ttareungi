import datetime
import urllib.parse
import webbrowser

import folium
import pandas as pd
import plotly.graph_objects as go
from folium import plugins
from folium.plugins import MarkerCluster
from plotly.subplots import make_subplots
from pymongo import MongoClient

host = "localhost"
port = "17017"
username = urllib.parse.quote_plus('admin')
password = urllib.parse.quote_plus('admin')
mongo = MongoClient(host, int(port))
database = mongo.Ttareungi
print(database)

pipe1 = [{'$group': {'_id': "$rental_date(month)", 'total': {'$sum': "$number_of_rentals"},
                     'office_id': {'$first': "$rental_office_id"}}},
         {'$project': {'_id': 0, 'date': "$_id", 'total': 1, 'office_id': 1}}, {'$sort': {'date': -1}}]

pipe2 = [{'$group': {'_id': "$sub_date", 'total': {'$sum': "$sub_num"}}},
         {'$project': {'_id': 0, 'date': "$_id", 'total': 1}}, {'$sort': {'registers': 1}}]

pipe3 = [{'$group': {'_id': "$rental_office_id",
                     'avg': {'$avg': "$number_of_rentals"},
                     "office_name": {"$first": "$rental_office_name"}}},
         {'$project': {'_id': 0, 'office_id': "$_id", 'office_name': "$office_name", "avg": 1}}, {'$sort': {'avg': -1}}]

pipe4 = [{'$group': {'_id': {"year": {"$substr": ["$rental_date", 0, 4]}, "month": {"$substr": ["$rental_date", 5, 2]},
                             "rental": "$rental_office_id"}, "count": {'$sum': 1},
                     "name": {'$first': "$rental_office_name"}}},
         {'$group': {'_id': "$_id.rental", "avg": {"$avg": "$count"}}}, {"$sort": {"_id": 1}}]

pipe5 = [{'$group': {'_id': {"year": {"$substr": ["$return_date", 0, 4]}, "month": {"$substr": ["$return_date", 5, 2]},
                             "return": "$return_office_id"}, "count": {"$sum": 1},
                     "name": {"$first": "$return_office_name"}}},
         {'$group': {'_id': "$_id.return", "avg": {'$avg': "$count"}}}, {'$sort': {'_id': 1}}]
# pip3꺼를 설치시기 같은 애들 평균내서 년도별 평균 내기
install_date_query = {'rental_office_id': 1, 'installation_date': 1}

location_query = {'rental_office_id': 1, 'rental_office_name': 1, 'latitude': 1, 'longitude': 1}

# -------------------------------------------------------------------------------------------

use_by_month = database.rental_office_usage.aggregate(pipe1)
print("쿼리1 완료")
new_users_by_month = database.new_sub.aggregate(pipe2)
print("쿼리2 완료")
use_avg_by_rental_office = database.rental_office_usage.aggregate(pipe3)
print("쿼리3 완료")
rental_avg_by_rental_office = database.rental_history.aggregate(pipe4)
print("쿼리4 완료")
return_avg_by_rental_office = database.rental_history.aggregate(pipe5)
print("쿼리5 완료")
install_date_of_rental_office = database.rental_office.find({}, install_date_query)
print("쿼리6 완료")
rental_office_location = database.rental_office.find({}, location_query)
print("쿼리7 완료")

rental_office_install_date = dict(
    (data['rental_office_id'], data['installation_date']) for data in install_date_of_rental_office)
rental_office_rental_num = dict()

# -------------------------------------------------------------------------------------------
use_avg_by_install_date = dict()
count_by_install_date = dict()
dates = []
totals = []
date = []
pipe1_office_id = []
registers_total = []
office_name = []
avgs = []
office_id = []
office_id_avg = []
rental_return_avg_sub = dict()
office_locations = []
office_avg_month = dict()
pipe4_rental_avg = dict()
pipe4_return_avg = dict()
pipe4_rental_avg_list = []
pipe4_return_avg_list = []
pipe6_office_id = []
pipe6_office_install_date = []
pipe6_office_avg_month = []
pipe6_office_avg = []
group_office_id_high = dict()
group_office_id_low = dict()
# -------------------------------------------------------------------------------------------
for data in list(use_avg_by_rental_office):
    rental_office_id = data['office_id']

    install_date = rental_office_install_date.get(rental_office_id, 0)
    if install_date == 0 or install_date is None:
        continue

    year = install_date[:4]
    count_by_install_date[year] = count_by_install_date.get(year, 0) + 1
    use_avg_by_install_date[year] = use_avg_by_install_date.get(year, 0) + data["avg"]

    office_name.append(data['office_name'])
    avgs.append(data['avg'])
    office_avg_month[rental_office_id] = data['avg']

for year in ["2015", "2016", "2017", "2018", "2019", "2020", "2021"]:
    if use_avg_by_install_date.get(year):
        use_avg_by_install_date[year] = use_avg_by_install_date[year] // count_by_install_date[year]

for data in list(use_by_month):
    totals.append(data['total'] / 10000)
    dates.append(datetime.datetime(data['date'] // 100, data['date'] % 100, 1))
    pipe1_office_id.append(data['office_id'])

for data in list(new_users_by_month):
    registers_total.append(data['total'])
    date.append(datetime.datetime(data['date'] // 100, data['date'] % 100, 1))

for data in list(rental_avg_by_rental_office):
    rental_return_avg_sub[data['_id']] = data['avg']
    pipe4_rental_avg[data['_id']] = data['avg']

for data in list(return_avg_by_rental_office):
    if rental_return_avg_sub.get(data['_id']):
        sub = rental_return_avg_sub[data['_id']] - data['avg']
        rental_return_avg_sub[data['_id']] = sub
        pipe4_return_avg[data['_id']] = data['avg']
    else:
        rental_return_avg_sub[data['_id']] = -data['avg']
        pipe4_return_avg[data['_id']] = data['avg']
rental_return_avg_top = sorted(rental_return_avg_sub.items(), key=(lambda x: x[1]), reverse=True)
count = 0
for key, value in rental_return_avg_top:
    if type(key) != str and key is not None:
        if key <= 5000:
            office_id_avg.append(value)
            office_id.append(key)
            count += 1
            group_office_id_high[key] = 1

    if count >= 10:
        break

rental_return_avg_top = sorted(rental_return_avg_sub.items(), key=(lambda x: x[1]), reverse=False)
count = 0
for key, value in rental_return_avg_top:
    if type(key) != str and key is not None:
        if key <= 5000:
            office_id_avg.append(value)
            office_id.append(key)
            count += 1
            group_office_id_low[key] = 1

    if count >= 10:
        break

for key in office_id:
    pipe4_rental_avg_list.append(pipe4_rental_avg.get(key, 0))
    pipe4_return_avg_list.append(pipe4_return_avg.get(key, 0))

df = pd.DataFrame(rental_office_location)
for i in df.index[:]:
    if not rental_office_install_date.get(df.loc[i, 'rental_office_id']):
        continue
    pipe6_office_id.append(df.loc[i, 'rental_office_id'])
    pipe6_office_install_date.append(rental_office_install_date[df.loc[i, 'rental_office_id']])
    pipe6_office_avg_month.append(office_avg_month[df.loc[i, 'rental_office_id']] / 100)

for data in list(use_avg_by_rental_office):
    office_name.append(data['office_name'])
    avgs.append(data['avg'])
for year in ["2015", "2016", "2017", "2018", "2019", "2020", "2021"]:
    pipe6_office_avg.append(use_avg_by_install_date[year])
# -------------------------------------------------------------------------------------------
fig = make_subplots(rows=2, cols=2,
                    subplot_titles=('날짜별 대여소별 월 평균 사용량', '날짜별 신규 가입자 수', '대여량 반납량 순위', '설치 날짜별 평균 사용량'),
                    specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "scatter"}, {"type": "pie"}]])

# 1,2 번 시각화
# 날짜별 대여소별 월 평균 사용량 날짜별 신규 가입자 수
fig.add_trace(go.Bar(
    x=dates,
    y=totals, legendgroup='1', showlegend=False),
    row=1, col=1)
fig.add_trace(go.Bar(
    x=date,
    y=registers_total, legendgroup='2', showlegend=False),
    row=1, col=2)

# 4 번 시각화
# 반납량 대여량 차이
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], y=office_id_avg[:10], text=office_id[:10], textposition='middle center',
    showlegend=False),
    row=2, col=1)
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], y=office_id_avg[10:], text=office_id[10:], textposition='middle center',
    showlegend=False),
    row=2, col=1)
# 6 번 시각화
# 설치 날짜별 평균 사용량
fig.add_trace(go.Pie(
    values=pipe6_office_avg, labels=["2015", "2016", "2017", "2018", "2019", "2020", "2021"], legendgroup='4'),
    row=2, col=2)

fig['layout']['xaxis']['title'] = '년도'
fig['layout']['yaxis']['title'] = '사용량'
fig['layout']['xaxis2']['title'] = '년도'
fig['layout']['yaxis2']['title'] = '신규 가입자'
fig['layout']['xaxis3']['title'] = '대여량 반납량 순위'
fig['layout']['yaxis3']['title'] = '대여량 반납량 차이'
fig.update_layout(
    legend_tracegroupgap=180,
    legend=dict(
        bordercolor='black',
        borderwidth=1,
        orientation="v",
        yanchor="bottom",
        x=0.95,
        y=0.2,
        xanchor="center",
    ),
)
fig.write_html("graph.html")

##지도에 대여소 표시
# 서울중심
center = [37.541, 126.986]
m = folium.Map(location=center, min_zoom=10, width='100%', height='100%')
# 마커 클러스터 사용
marker_cluster = MarkerCluster(control=False).add_to(m)
# 그룹만들기
g1 = plugins.FeatureGroupSubGroup(marker_cluster, '평균 대여량 이하')
m.add_child(g1)
g2 = plugins.FeatureGroupSubGroup(marker_cluster, '평균 대여량 이상')
m.add_child(g2)

m.fit_bounds([[37.443036, 126.856744], [37.646073, 127.100117]])
for i in df.index[:]:
    # 위도 경도 값 없을시 건너뛰기
    if (df.loc[i, 'latitude']) and (df.loc[i, 'longitude']):
        install_date = rental_office_install_date[df.loc[i, 'rental_office_id']]
        use_avg = use_avg_by_install_date[install_date[:4]]
        avg_month = office_avg_month.get(df.loc[i, 'rental_office_id'], 0)
        rental_office_explain = f"대여소 명 : {df.loc[i, 'rental_office_name']}" \
                                f"<br>월 평균 대여량 : {int(avg_month)}" \
                                f"<br>설치 시기 : {install_date}" \
                                f"<br>같은 설치시기인 대여소 평균 대여량: {int(use_avg)}" \
                                f"<br>평균 대여량 반납량 차이: {int(rental_return_avg_sub.get(df.loc[i, 'rental_office_id'], 0))}"
        iframe = folium.IFrame(
            rental_office_explain, height='100%')
        popup = folium.Popup(iframe, min_width=500, max_width=500, max_height=160, min_height=160, script=True)
        color = ''
        if group_office_id_high.get(df.loc[i, 'rental_office_id'], 0) != 0:
            color = 'lightred'
        elif group_office_id_low.get(df.loc[i, 'rental_office_id'], 0) != 0:
            color = 'lightgray'

        if avg_month < use_avg:
            if color == '':
                color = 'lightblue'
            marker = folium.Marker(
                location=[df.loc[i, 'latitude'], df.loc[i, 'longitude']],
                popup=popup,
                icon=folium.Icon(color=color, icon='ok')
            ).add_to(g1)
        else:
            if color == '':
                color = 'lightgreen'
            marker = folium.Marker(
                location=[df.loc[i, 'latitude'], df.loc[i, 'longitude']],
                popup=popup,
                icon=folium.Icon(color=color, icon='ok')
            ).add_to(g2)

folium.LayerControl(collapsed=False).add_to(m)
# html 파일로 저장
m.save("a.html")
webbrowser.open_new_tab("exe.html")
