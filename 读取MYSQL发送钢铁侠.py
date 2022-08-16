import time
import os
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import numpy as np
import datetime
import pandas as pd



POOLSensor = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    host='192.168.110.11',
    port=3306,
    user='furnace',    # 用户名
    password='furnace',      # 密码
    database='car_cone1',  # 库名
    charset='utf8'
)



# 建立连接MYSQL程序
def readMysqlToArry(mysql1, POOL0):
    conn = POOL0.connection()      #建立连接
    cursor = conn.cursor()         ## 使用cursor()方法获取操作游标
    # print("mysql1:", mysql1)
    try:
        cursor.execute(mysql1)      # 使用execute方法执行SQL语句
        ccc = []
        for x in cursor.fetchall():
            ccc.append(list(x))
        # 将数据库里面读取出来的数据bbb全部写成矩阵形式。
        arr1 = np.array(ccc)
        conn.commit()
        #print("读取出来的数据为：", arr1)
        # print("读取数据库成功")
    except Exception as r:
        conn.rollback()
        print("读取数据库失败")
        print("故障码：", r)
        conn.close()
    finally:
        conn.close()
    return arr1





m = 1
while 1:

    mysql ="SELECT * FROM car_cone1.cone1ping order by timeID desc limit 1"
    kk = readMysqlToArry(mysql,POOLSensor)
    print(kk)
    while 1:
        if kk[0,m] == '1':
            print("cone1_%dping网络正常"%m)
        else :
            print("cone1_%dping网络异常!!!!!!"%m)
        m += 1
        if m > 10:
            break
    time.sleep(600)
