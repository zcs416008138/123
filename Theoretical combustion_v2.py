#-*- coding: utf-8 -*-
"""
@author: Tian Dao Chou Qin
@time:2022/2/7  15:04
"""
import numpy as np
import pandas as pd
import xlwings as xw
import requests as rq
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler # 导入进程调度器
import pymysql
from dbutils.pooled_db import PooledDB
import matplotlib.pyplot as plt

def eid():
    url = 'http://e.ai:8083/data-governance/sensor/batch/latest'  # 需要请求的URL地址(
    data = {"id": ['6e7e9a99','756ca619','b1687620','7358300b','d78044d6','d0ae0913'] }  # POST请求需要提交的数据
    data = json.dumps(data)  # 有的时候data需要时json类型的
     #   print(data,type(data))
    headers = {
        'content-type': 'application/json'
    }  # 一种请求头，需要携带
    #    help(rq.post)
    res = rq.post(url=url,  headers=headers,data=data)  # 发起请求
    traget = res.json()  # 将获取到的数据变成json类型
      # return traget
    # print(traget)
    # print(typ e(traget))

    #解开json 串内的内容  9 这列的值就是需要的值
    val_1 = traget['data']
    # print(val_1)
    val_2 = pd.DataFrame(val_1)
    # print(val_2)
    val_2 = val_2['9'].astype(float)
    # print(val_2)
    # print(type(val_2))
    val_co = (val_2[0]+val_2[3])/2
    val_h2 = (val_2[2]+val_2[5])/2
    # print(val_co,val_h2)
    heat_value = (val_co*3046+val_h2*2580)/100
    print("实时热值：",heat_value,"Kcal/m³")
    lilun_k = (val_co*0.5+val_h2*0.5)/0.21/100
    excess_air_coefficient = 1.2            #空气过剩系数
    air_fuel_ratio = lilun_k*excess_air_coefficient
    print("理论燃烧空燃比：",'%.2f'%air_fuel_ratio)


if __name__ == '__main__':

    scheduler = BlockingScheduler()
    scheduler.add_job(eid,'interval', seconds=3)

    try:
        scheduler.start()
    except BaseException as r:
        print(r)