import requests, json
import datetime
import pymysql
import time
import threading
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


def diaoqushuju(eid,Begin,End):
    url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"
    data = {
        "id": eid,
        "beginTime": Begin,
        "endTime": End,
        "limit": 90000,
        "orderBy": "desc"}
    # print("data",data)
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
    # print("result=", res.text)  # 打印出结果
    data0 = res.text
    data11 = json.loads(data0)  # 将json数据转化为字典数据。
    return data11

def shujuchuli(shuju,h):      #      处理调取出来的数据，提取想要的
    gang = []
    ll1 = shuju['data']
    ll2 = ll1[0]
    ll3 = ll2['datas']
    for i in range(len(ll3)):
        ll4 = ll3[i]
        ll5 = ll4[h]
        ll5 = ll5.replace(',', '')
        ll5 = float(ll5)
        gang.append(ll5)

    return gang


def time_begin (shuju,max):
    ll1 = shuju['data']
    ll2 = ll1[0]
    ll3 = ll2['datas']
    for i in range(len(ll3)):
        ll4 = ll3[i]
        ll5 = ll4['50']
        ll5 = ll5.replace(',', '')
        ll5 = float(ll5)
        if ll5 == max:
            ll6 = ll4['timeID']
    return ll6


# 非整点执行向前取整
def time_quzheng(time123):
    time_array = time.strptime(time123, "%Y-%m-%d %H:%M:%S") # 转换成时间数组
    time_timestamp = time.mktime(time_array)              # 转换为时间戳
    time_yushu = time_timestamp % 3600  # 对时间戳进行取余数
    if time_yushu < 1800:                                    # 做判定，取证，接近哪个整点，取哪个
        time_timestamp2 = time_timestamp - time_timestamp % 3600     # 对时间戳进行取整
    elif time_yushu >= 1800:
        time_timestamp2 = time_timestamp - time_timestamp % 3600 + 3600  # 对时间戳进行取整
    # print("time_timestamp2 = ",time_timestamp2)
    time_array2 = time.localtime(int(time_timestamp2))
    time_x = time.strftime("%Y-%m-%d %H:%M:%S",time_array2)  # 转换成时间数组
    # print("time_x = ",time_x)
    return time_x


# 输入时间戳判断班组
def Banzu(data):
    a = 115200
    a2 = int(data) % a
    if a2 >= 0 and a2 < 28800:
        banzu = "甲班"
    elif a2 >= 28800 and a2 < 57600:
        banzu = "乙班"
    elif a2 >= 57600 and a2 < 86400:
        banzu = "丙班"
    elif a2 >= 86400 and a2 < 115200:
        banzu = "丁班"
    return banzu

# 班次筛选，通过时间段，看是夜白中的哪个班次
def Banci(hours):
    if hours >= 0 and hours < 8:
        banci = "夜班"
    elif hours >= 8 and hours < 16:
        banci = "白班"
    elif hours >= 16 and hours < 24:
        banci = "中班"
    return banci


def gangpi (a,EID,kuming,kuming2):
    while 1:
        # 查看要插入的数据库中最后一笔数据的时间
        sql0 = "SELECT * FROM " + kuming2 + " order by End desc limit 1"
        # print("sql0=",sql0)
        arr1 = readMysql(POOL, sql0)           # 对本地数据库进行链接
        # print("arr1=",arr1)
        if len(arr1) == 0:
            time3 = '2022-06-01 00:00:00'       # 如果将要插入的数据库为空，手动设定一个开始时间
        else:
            time3 = arr1[:,1][0]              # 根据程序所得下一次开始的时间
        # print("time3 : ",time3)
        time3_quzheng = time_quzheng(str(time3) )    # 时间向上取整
        # print(a,"time3 : ",time3)
        # print(a,"time3_quzheng : ",time3_quzheng)
        # 处理成用来确定 EID 的时间范围
        time4 = datetime.datetime.strptime(str(time3_quzheng), "%Y-%m-%d %H:%M:%S")
        Begin = (time4 + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        End =(time4 + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        # print(a,Begin , End)





        End_array = time.strptime(End, "%Y-%m-%d %H:%M:%S")  # 转换成时间数组
        End_timestamp = time.mktime(End_array)  # 转换为时间戳

        while 1:
            now_timestamp = time.time()  # 获取当前时间戳
            if End_timestamp > now_timestamp:  # 结束时间与当前时间比对，大于的话，结束循环
                print(a,"此次结束，等待五分钟进行下一次判定！",now_timestamp)
                time.sleep(300)
                break




            shuju = diaoqushuju(EID,Begin,End)
            # print("shuju = ",shuju)
            gang = shujuchuli(shuju,'50')
            # print(gang)
            Actual = int(max(gang))                     # 钢坯实际数量
            print(a,"钢坯实际数量:",Actual)

            time2 = datetime.datetime.strptime(time_begin(shuju,Actual), "%Y-%m-%d %H:%M:%S")
            # 最大值的时间（前一段数据的结尾以及后一段数据的开始）
            # print(time3,time2)

            # 查看gangpiNumber 数据库
            sql0 = "SELECT * FROM " + kuming+ " where timeID between ' " + str(time3) + " ' and ' " +  str(time2) + " ' "
            # print("sql0=",sql0)
            arr0 = readMysql(POOL, sql0)
            # print("arr0=",arr0)


            # 班次班组
            Begin_array = time.strptime(Begin, "%Y-%m-%d %H:%M:%S")  # 转换成时间数组
            Begin_timestamp = time.mktime(Begin_array)  # 转换为时间戳
            Banci1 = Banci(int(Begin_array[3]))
            # print("班次：", Banci1)
            Banzu1 = Banzu(Begin_timestamp)
            # print("班组：", Banzu1)


            # 捞取的数据为空的话，赋值为零进行插入
            if len(arr0) == 0:
                charu = []
                Calculated = 0
                Difference = 0
                # Actual = 0
                Accuracy = 0
                time2_gai = datetime.datetime.strptime(str(time2), "%Y-%m-%d %H:%M:%S")
                time2 = (time2_gai + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                print(a, "时间范围：", time3, " ~ ", time2)
                charu.extend([time3, time2, Calculated, Actual, Difference, Accuracy,Banci1,Banzu1])
                insertdata = "INSERT INTO  " + kuming2 + "(Begin,End,Calculated,Actual,Difference,Accuracy,Banci,Banzu)values(%s,%s,%s,%s,%s,%s,%s,%s)"
                func(insertdata, charu)
            # 捞取的数据正常的话，进行插入数据的计算
            else:
                id = arr0[:, 0]  # ID
                # print(id)
                Calculated = len(id)
                # print("程序计算数量：",Calculated)
                Difference = Actual - Calculated        # 差值
                # print("差值：",Difference)
                if Calculated <  Actual :
                    Accuracy = Calculated / Actual * 100        # 准确率进行判断差值
                elif Calculated == Actual:
                    Accuracy = Calculated / Actual * 100
                elif Calculated > Actual:
                    Accuracy = Actual / Calculated * 100
                Accuracy = round(Accuracy, 2)
                Accuracy = str(Accuracy)+ "%"
                # print("准确率：",Accuracy)
                print(a,"时间范围：", time3, " ~ ", time2)
                # 插入数据
                charu = []
                charu.extend([time3, time2, Calculated, Actual, Difference, Accuracy,Banci1,Banzu1])
                insertdata = "INSERT INTO  " + kuming2+ "(Begin,End,Calculated,Actual,Difference,Accuracy,Banci,Banzu)values(%s,%s,%s,%s,%s,%s,%s,%s)"
                func(insertdata, charu)

                # print("*****************************************************************")
                # Begin       开始时间
                # End         结束时间
                # Calculated  程序计算数量
                # Actual      钢坯实际数量
                # Difference  差值
                # Accuracy    准确率


            # 处理成下一班次的开始和结束时间
            Begin = datetime.datetime.strptime(str(Begin), "%Y-%m-%d %H:%M:%S")
            Begin = (Begin + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            # print(Begin)
            End = datetime.datetime.strptime(str(End), "%Y-%m-%d %H:%M:%S")
            End = (End + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            # print(End)
            End_array = time.strptime(End, "%Y-%m-%d %H:%M:%S") # 转换成时间数组
            End_timestamp = time.mktime(End_array)              # 转换为时间戳


            Begin_2 = datetime.datetime.strptime(str(Begin), "%Y-%m-%d %H:%M:%S")
            Begin_3 = (Begin_2 + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")    # 交接班时间
            Begin_4 = (Begin_2 + datetime.timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S")    # 交接班时间前一个小时
            Begin_4_array = time.strptime(Begin_4, "%Y-%m-%d %H:%M:%S")                 # 转换成时间数组
            Begin_4_timestamp = time.mktime(Begin_4_array)                               # 转换为时间戳

            time3 = time2                           # 上一次的结束时间赋值给下一次的开始时间
            time3_array = time.strptime(str(time3), "%Y-%m-%d %H:%M:%S")
            time3_timestamp = time.mktime(time3_array)

            if  time3_timestamp >= Begin_4_timestamp  :          # 防止提前停产导致时间节点衔接错误
                time3 = time2                                   # 如果大于交接班时间一个小时，那么正常
            elif time3_timestamp < Begin_4_timestamp:           # 如果小于，那么开始时间取固定时间
                time3 = Begin_3

def barroll():
    gangpi('barroll',['bfa0bff2'], 'barroll.gangpiNumber', 'barroll.billet_checking')  # eid,调取数据的库名，要插入的库名

def newbar():
    gangpi('newbar',['657df568'], 'newbar.gangpiNumber', 'newbar.billet_checking')  # eid,调取数据的库名，要插入的库名

def fullbarroll():
    gangpi('fullbarroll',['9fe9215c'], 'fullbarroll.gangpiNumber', 'fullbarroll.billet_checking')  # eid,调取数据的库名，要插入的库名



a = threading.Thread(target=barroll)
b = threading.Thread(target=newbar)
# c = threading.Thread(target=fullbarroll)
a.start()
b.start()
# c.start()

