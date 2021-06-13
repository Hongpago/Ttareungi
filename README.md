# Ttareungi
발표시 추가
데이터 선택이유
데이터 세부사항

## 도커를 통한 최적화 적용
docker pull mongo

docker network create mongo

docker run -it -d --net mongo --name=mongo1 mongo mongod --replSet config-replica-set --configsvr --port 27017
docker run -it -d --net mongo --name=mongo2 mongo mongod --replSet config-replica-set --configsvr --port 27017
docker run -it -d --net mongo --name=mongo-router1 mongo mongos --configdb config-replica-set/mongo1:27017,mongo2:27017 --bind_ip_all
docker run -it -d --net mongo --name=mongo-router2 mongo mongos --configdb config-replica-set/mongo1:27017,mongo2:27017 --bind_ip_all

docker run -it -d --net mongo --name=mongo-node1 mongo mongod --shardsvr --replSet shard-replica-set --bind_ip_all
docker run -it -d --net mongo --name=mongo-node2 mongo mongod --shardsvr --replSet shard-replica-set --bind_ip_all
docker run -it -d --net mongo --name=mongo-node mongo mongod --shardsvr --replSet shard-replica-set --bind_ip_all

docker run -it -d --net mongo --name=mongo-node3 mongo mongod --shardsvr --replSet second --bind_ip_all
docker run -it -d --net mongo --name=mongo-node4 mongo mongod --shardsvr --replSet second --bind_ip_all
docker run -it -d --net mongo --name=mongo-node5 mongo mongod --shardsvr --replSet second --bind_ip_all

###mongo1,2 에서

mongo mongo1:27017
rs.initiate({
_id: "config-replica-set",
configsvr: true,
members: [
{_id: 0, host: "mongo1:27017"},
{_id: 1, host: "mongo2:27017"}
]
})

###mongo-node1,3 에서

mongo mongo-node1:27018
rs.initiate({
_id: "shard-replica-set",
members: [
{_id: 0, host: "mongo-node1:27018"},
{_id: 1, host: "mongo-node2:27018"},
{_id: 2, host: "mongo-node:27018"}
]
})

mongo mongo-node3:27018
rs.initiate({
_id: "second",
members: [
{_id: 0, host: "mongo-node3:27018"},
{_id: 1, host: "mongo-node4:27018"},
{_id: 2, host: "mongo-node5:27018"}
]
})

###mongo-router1,2에서
mongo mongo-router1:27017
sh.addShard("shard-replica-set/mongo-node1:27018,mongo-node2:27018,mongo-node:27018")
sh.addShard("second/mongo-node3:27018,mongo-node4:27018,mongo-node5:27018")


##데이터
rental_office - 공공자전거 대여소 정보
rental_office_usage_info - 공공자전거 대여소별 이용정보
usage_info_month - 공공자전거 이용정보(월별)
new_sub_month - 서울특별시 공공자전거 신규가입자 정보(월별) (18년7월~19년5월까지 유저코드,젠더없음)
rental_history - 공공자전거 대여이력 정보

## 쿼리
1. 월별 사용량 
- db.rental_office_usage.aggregate([{$group:{_id:"$rental_date(month)",total:{$sum:"$number_of_rentals"}}}, {$project: {_id: 0, date: "$_id", total:1}}, {$sort:{date:-1}}])

2. 월별 신규 사용자수 
- db.new_sub.aggregate([{$group:{_id:"$sub_date",total:{$sum:"$sub_num"}}}, {$project: {_id: 0, registers: "$_id", total:1}}, {$sort:{registers:1}}])

3. 지도에 (2.지역 or 1.대여소)마다 사용량 표시(원이나 표식) 
- 대여소 별 전체 사용 (월 단위 사용량 평균) 
- db.rental_office_usage.aggregate([{$group:{_id:"$rental_office_id",avg:{$avg:"$number_of_rentals"},"office_name":{"$first":"$rental_office_name"}}},{$project: {_id:0, office_iㅊ:"$_id", office_name:"$office_name", avg:1}},{$sort:{avg:-1}}])

4. 범위별 전체 대여량, 반납 평균 - 3번 구해서 차이확인
- db.rental_history.aggregate([{$group:{_id:{"year":{"$substr":["$rental_date",0,4]},"month":{"$substr":["$rental_date",5,2]},"rental":"$rental_office_id"},"count":{$sum:1},"name":{$first:"$rental_office_name"}}},{$group:{_id:"$_id.rental","avg":{$avg:"$count"}}},{$sort:{_id:1}}])

- db.rental_history.aggregate([{$group:{_id:{"year":{"$substr":["$return_date",0,4]},"month":{"$substr":["$return_date",5,2]},"return":"$return_office_id"},"count":{$sum:1},"name":{$first:"$rental_office_name"}}},{$group:{_id:"$_id.return","avg":{$avg:"$count"}}},{$sort:{_id:1}}])

5. 반납량 - 대여량(인력 추가?거나 거치대 조절)

6. 설치시기 년도별 평균, 평균보다 큰 그룹, 작은 그룹
  3번 쿼리를 설치일수에 따라 평균냄
- db.rental_office.find({}, {rental_office_id:1, installation_date: 1})

## 시각화 주제
1. 구글 지도 API를 통한 대여소별 위치와 월 평균량 표시
2. 대여소별 대여량, 반납량 차이로 개선방안 표시
3. 대여소 설치시기 년도별 평균 쿼리랑과 그 평균보다 작거나 큰 쿼리 그룹들 표시