# coding:utf-8 用内存作为默认的作业存储器
import pymysql
from DBUtils.PooledDB import PooledDB
import numpy as np
import time,datetime

# 建立连接池程序
#sensor
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

    mysql ="SELECT * FROM car_cone1.cone1_%d order by timeID desc limit 1"%m
    kk = readMysqlToArry(mysql,POOLSensor)
# print ("kk=",kk[0,1])
#     print(mysql)

# 字符类型的时间
    tss1 = str(kk[0,1])
# 转为时间数组
    timeArray = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
    print(timeArray)
# 转为时间戳
    timeStamp1 = int(time.mktime(timeArray))
    print("数据库时间戳：",timeStamp1)

# time获取当前时间戳
    now = int(time.time())     # 1533952277
    timenow = time.localtime(now)
    nowTime = time.strftime("%Y--%m--%d %H:%M:%S", timenow)
    # print(nowTime)
# 转为时间数组
    timeArray2 = time.strptime(nowTime, "%Y--%m--%d %H:%M:%S")
# 转为时间戳
    timeStamp2 = int(time.mktime(timeArray2))
    print("现在时间戳：",timeStamp2)

# 数据库与当前时间对比，超过十分钟b赋值为1
    a = timeStamp2-timeStamp1
    if a >= 600:
        b = 1
        print("cone1_%d"%m,b)
    else:
        b = 0
        print("cone1_%d"%m,b)
    # 跳出循环
    m += 1
    if m > 10:
        break