import requests, json
import datetime
import pymysql
import time
import calendar
import os
import logging
import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from win32com.client import Dispatch
from DBUtils.PooledDB import PooledDB
import numpy as np
from numpy import *

# 建立连接池程序
POOL = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    host='10.6.1.82',
    port=3306,
    user='furnace',
    password='furnace',
    database='newbar',
    charset='utf8'
)

#建立连接池程序
POOL2 = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root123',
    database='lianxi',
    charset='utf8'
)

def readMysql(POOL0, sql):
    conn = POOL0.connection()
    # 创建游标
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        resultData = cursor.fetchall()
        bbb = []
        for n in resultData:
            bbb.append(list(n))
            # print("bbb",bbb)
        arryData = np.array(bbb)
        conn.commit()
        # print("读取数据库成功")
    except Exception as r:
        conn.rollback()
        print("读取数据库失败")
        print("故障码：", r)
        conn.close()
    finally:
        conn.close()
    return arryData


def updatesql(POOL1, sql):
    conn = POOL1.connection()
    # 创建游标
    cursor = conn.cursor()
    try:
        cursor.execute(sql)

        conn.commit()
        print("读取数据库成功")
    except Exception as r:
        conn.rollback()
        print("读取数据库失败")
        print("故障码：", r)
        conn.close()
    finally:
        conn.close()


#查看数据库
sql0 = "SELECT * FROM lianxi.cone1 order by cur asc"
# print("sql0=",sql0)
arr0 = readMysql(POOL2, sql0)
ID = arr0[:,0]          # 所有ID
timeID = arr0[:,2]    # 所有时间
# print(len(timeID))
# print(timeID)
# print(len(ID))
# print(ID)
for i in range(1010,len(ID)):
    sql1 = "SELECT timeID,nbmill_milio_mill05_guigexinghao_VALUE as guige FROM newbar.rulugenzong where timeID =  ' " + str(timeID[i]) + " ' "
    # print(sql1)
    arr1 = readMysql(POOL, sql1)
    print("lrn=",len(arr1))
    print("juzheng=",i,"  ",arr1)
    if len(arr1) ==0:
        print('continue=',i)
        continue
    else:
        print("else=",i)
        guige = arr1[:,1]
        guige = int(guige[0])
        # print(guige)
        insertdata = "update lianxi.cone1 set guige = '" + str(guige) + " 'where ID=  " + str(ID[i])
        print(insertdata)
        updatesql(POOL2,insertdata)
