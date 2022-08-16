import requests
import json
import pandas as pd
import math
import numpy as np


def fenzhong():
    url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"   #秒级数据区间查询
    #url = "http://e.ai:8083/data-governance/sensor/batch/hour/avg"


    #url ="http://e.ai:8083/data-governance/sensor/batch/minite/avg"
    data = {
        "id":['de29ffd4'],            #在此处填写要查询的eid
        "beginTime": "2022-03-03 08:00:00",       #在此处填写要查询的开始时间
        "endTime": "2022-03-03 09:00:00",          #在此处填写要查询的结束时间
        "limit": 9000000,                            #最大数据量
        "orderBy": "desc"}#desc倒序排列，asc正序排列
    #print("data=",data)
    # print("开始从数据库里面读取文件，需要较长时间，请耐心等待")
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
    #print("result=", res.text)  # 打印出结果
    data0 = res.text
    # print("data0=",data0)
    data11 = json.loads(data0)  # 将json数据转化为字典数据。
    # print(data11)
    return data11



datalist = fenzhong()
ll1 = datalist['data']
# print(ll1)
# print(ll1[0])
ll2 = ll1[0]
# print(ll2)
ll3 = ll2['datas']
# print(len(ll3))
a = 0.00
for i in range(len(ll3)):
    ll4= ll3[i]
    ll5 = ll4['2']
    ll5 = ll5.replace(',','')
    ll5 = float(ll5)
    # print(ll5)
    a += ll5
b = a/3600
print(b)