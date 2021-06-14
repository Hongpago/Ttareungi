import csv
import json
input_file_name = "data/rental_office.csv"
output_file_name = "data.txt"
with open(input_file_name, "r", encoding="utf-8", newline="") as input_file, \
        open(output_file_name, "w", encoding="utf-8", newline="") as output_file:

    reader = csv.reader(input_file)
    # 첫 줄은 col_names 리스트로 읽어 놓고
    col_names = next(reader)
    # 그 다음 줄부터 zip으로 묶어서 json으로 dumps
    for cols in reader:
        doc = {col_name: col for col_name, col in zip(col_names, cols)}
        print(json.dumps(doc, ensure_ascii=False), file=output_file)


# c1 = database.rental_office_usage.find()
# c2 = database.new_sub.find()
# c3 = database.rental_history.find()
# c4 = database.rental_office.find()
#
# j_dict = {}
# i = 0
# for row in c1:
#     j_dict[i] = {'rental_date(month)': row['rental_date(month)'],
#                  'rental_office_id': row['rental_office_id'],
#                  'rental_office_name': row['rental_office_name'],
#                  'number_of_rentals': row['number_of_rentals']}
#     i = i + 1
#
# with open('rental_office_usage.json', 'w') as file:
#     json.dump(j_dict, file, indent=4,ensure_ascii = False)
#
# print("json 파일 생성")
#
# j_dict = {}
# i = 0
# for row in c2:
#     j_dict[i] = {'sub_date': row['sub_date'], 'user_age': row['user_age'], 'sub_num': row['sub_num']}
#     i = i + 1
#
# with open('new_sub.json', 'w') as file:
#     json.dump(j_dict, file, indent=4, ensure_ascii = False)
#
# print("json 파일 생성")

# j_dict = {}
# i = 0
# for row in c3:
#     j_dict[i] = {'bicycle_id': row['bicycle_id'], 'rental_date': row['rental_date'],
#                  'rental_holder_id': row['rental_holder_id'], 'rental_office_id': row['rental_office_id'],
#                  'rental_office_name': row['rental_office_name'], 'return_date': row['return_date'],
#                  'return_holder_id': row['return_holder_id'], 'return_office_id': row['return_office_id'],
#                  'return_office_name': row['return_office_name'], 'use_distance': row['use_distance'],
#                  'use_time': row['use_time']}
#     i = i + 1
#
# with open('rental_history.json', 'w') as file:
#     json.dump(j_dict, file, indent=4, ensure_ascii = False)
#
# print("json 파일 생성")
#
# j_dict = {}
# i = 0
# for row in c4:
#     j_dict[i] = {'rental_office_id': row['rental_office_id'], 'rental_office_name': row['rental_office_name'],
#                  'gu': row['gu'], 'detail_address': row['detail_address'], 'latitude': row['latitude'],
#                  'longitude': row['longitude'], 'installation_date': row['installation_date'],
#                  'operation_method': row['field9']}
#     i = i + 1
#
# with open('rental_office.json', 'w') as file:
#     json.dump(j_dict, file, indent=4, ensure_ascii = False)
#
# print("json 파일 생성")