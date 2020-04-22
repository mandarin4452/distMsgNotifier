import requests
import json
import sqlite3
import time
import datetime


def get_current_num(cur):
    cur.execute('select count(distinct date) from message;')
    for row in cur:
        row_lst = list(str(row).split(','))[0]
        return int(row_lst[1:])

def update_db():
    # Request datas from api
    key = 'rNsMxrTdG3oFs9MkFe9%2FasT1LZfz0mf60MqrgiJb2r9jZ%2FzAnle99U%2BQHA0xtUnDhmbus4n6VqwCJYNG2oNNAQ%3D%3D'
    page = 1
    r = requests.get(f"http://apis.data.go.kr/1741000/DisasterMsg2/getDisasterMsgList?ServiceKey={key}&type=json&pageNo={page}&numOfRows=10&flag=Y")
    json_data = r.json()

    tot_msg = json_data['DisasterMsg'][0]['head'][0]['totalCount']
    print(tot_msg)

    conn = sqlite3.connect('data.db')

    cur = conn.cursor()
    tot_db = get_current_num(cur)
    print(tot_db)
    # Initialize Database
    if tot_msg != tot_db:
        diff = tot_msg - tot_db
        print("Difference : " + str(diff))
        last_page = (diff // 10) + 1

        for i in range(last_page ,0,-1):
            r = requests.get(f"http://apis.data.go.kr/1741000/DisasterMsg2/getDisasterMsgList?ServiceKey={key}&type=json&pageNo={i}&numOfRows=10&flag=Y")
            json_data = r.json()
            length = len(json_data['DisasterMsg'][1]['row'])
            len_lst = [(lambda x: x)(x) for x in range(length)]
            len_lst = reversed(len_lst)

            for j in len_lst:
                try : 
                    cur = conn.cursor()
                    date = json_data['DisasterMsg'][1]['row'][j]['create_date']
                    loc = json_data['DisasterMsg'][1]['row'][j]['location_name']
                    msg = json_data['DisasterMsg'][1]['row'][j]['msg']
                    date = datetime.datetime.strptime(date,'%Y/%m/%d %H:%M:%S')
                    cur.execute('insert into message values (?,?,?);',(date, loc,msg))
                    conn.commit()
                    print(f"Page {i} committed!")
                except :
                    continue

