import time
import os
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import datetime




#建立连接池程序
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
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root123',
    database='hazhou',
    charset='utf8'
)




def pingComputer():

    m = {}
    n = []
    n.clear()

    now = int(time.time())  # 1533952277
    timenow = time.localtime(now)
    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", timenow)
    n.append(nowTime)




    for i in range(141, 151):
        host = '10.6.129.' + str(i)
        p = os.popen("ping "+ host + " -n 2")
        line = p.read()

        if "无法访问目标主机" in line:
            m[host] = 0
        else:
            m[host] = 1

    # 遍历字典中的所有值，values()
    for b in m.values():
        n.append(b)
    print(n)
    # print(m)
    return  n




# 插入数据
def func(insertdata, data):
    conn = POOL.connection()
    # 创建游标
    cursor = conn.cursor()
    try:
        cursor.execute(insertdata,(data))
        conn.commit()
        print("插入成功func")
    except Exception as rs:
        conn.rollback()
        print("插入失败func")
        print("funcfault=", rs)
        conn.close()
    finally:
        conn.close()




while 1:
    n1 = pingComputer()
    # print(n1)
    insertdata = "INSERT INTO cone1(timeID,cone1_1,cone1_2,cone1_3,cone1_4,cone1_5,cone1_6,cone1_7,cone1_8,cone1_9,cone1_10)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    func(insertdata, n1)
    time.sleep(600)
