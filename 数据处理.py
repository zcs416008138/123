import requests, json
import datetime
import pymysql
import time
from DBUtils.PooledDB import PooledDB
import numpy as np
from numpy import *


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

def zhongweishu(guige):
    if len(guige) % 2 == 0:
        i = len(guige) / 2
        z = (guige[int(i)] + guige[int(i)-1]) / 2.0
        z = round(z, 2)
    elif len(guige) % 2 == 1:
        i = len(guige) / 2
        z = guige[int(i)]
    return z

 # 查看gangpiNumber 数据库
sql0 = "SELECT * FROM lianxi.shujuchuli"
# print("sql0=",sql0)
arr0 = readMysql(POOL2, sql0)
# print("arr0=",arr0)
guige = arr0[:, 3]  # 规格
# print(len(guige))
# print("规格:",guige)
Billet_absorption_heat = arr0[:, 10]  # 钢坯吸热效率
# print(len(Billet_absorption_heat))
# print("钢坯吸热效率:",Billet_absorption_heat)

guige_20 = []
guige_22 = []
guige_25 = []
guige_28 = []
guige_32 = []
guige_36 = []
for i in range (len(guige)):
    if guige[i] == 20:
        guige_20.append(Billet_absorption_heat[i])
    elif guige[i] == 22:
        guige_22.append(Billet_absorption_heat[i])
    elif guige[i] == 25:
        guige_25.append(Billet_absorption_heat[i])
    elif guige[i] == 28:
        guige_28.append(Billet_absorption_heat[i])
    elif guige[i] == 32:
        guige_32.append(Billet_absorption_heat[i])
    elif guige[i] == 36:
        guige_36.append(Billet_absorption_heat[i])
guige_20.sort()                 # 从小到大排列
guige_22.sort()
guige_25.sort()
guige_28.sort()
guige_32.sort()
guige_36.sort()
# print("guige_20 = ",guige_20)
# print("guige_22 = ",guige_22)
# print("guige_25 = ",guige_25)
# print("guige_28 = ",guige_28)
# print("guige_32 = ",guige_32)
# print("guige_36 = ",guige_36)

zhong_20 = zhongweishu(guige_20)
zhong_22 = zhongweishu(guige_22)
zhong_25 = zhongweishu(guige_25)
zhong_28 = zhongweishu(guige_28)
zhong_32 = zhongweishu(guige_32)
zhong_36 = zhongweishu(guige_36)

pingjun_20 = sum(guige_20) / len(guige_20)
pingjun_22 = sum(guige_22) / len(guige_22)
pingjun_25 = sum(guige_25) / len(guige_25)
pingjun_28 = sum(guige_28) / len(guige_28)
pingjun_32 = sum(guige_32) / len(guige_32)
pingjun_36 = sum(guige_36) / len(guige_36)
pingjun_20 = round(pingjun_20, 2)
pingjun_22 = round(pingjun_22, 2)
pingjun_25 = round(pingjun_25, 2)
pingjun_28 = round(pingjun_28, 2)
pingjun_32 = round(pingjun_32, 2)
pingjun_36 = round(pingjun_36, 2)

print("规格20的平均数：",pingjun_20,"规格20的中位数：",zhong_20,"规格20的最小值：",guige_20[0],"规格20的最大值：",guige_20[-1])
print("规格22的平均数：",pingjun_22,"规格22的中位数：",zhong_22,"规格22的最小值：",guige_22[0],"规格22的最大值：",guige_22[-1])
print("规格25的平均数：",pingjun_25,"规格25的中位数：",zhong_25,"规格25的最小值：",guige_25[0],"规格25的最大值：",guige_25[-1])
print("规格28的平均数：",pingjun_28,"规格28的中位数：",zhong_28,"规格28的最小值：",guige_28[0],"规格28的最大值：",guige_28[-1])
print("规格32的平均数：",pingjun_32,"规格32的中位数：",zhong_32,"规格32的最小值：",guige_32[0],"规格32的最大值：",guige_32[-1])
print("规格36的平均数：",pingjun_36,"规格36的中位数：",zhong_36,"规格36的最小值：",guige_36[0],"规格36的最大值：",guige_36[-1])
