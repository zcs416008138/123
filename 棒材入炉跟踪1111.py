# coding:utf-8 用内存作为默认的作业存储器
import time
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import numpy as np
import threading
from numpy import *
import requests
import json

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
    database='barroll',
    charset='utf8'
)


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
        print("读取数据库成功")
    except Exception as r:
        conn.rollback()
        print("读取数据库失败")
        print("故障码：", r)
        conn.close()
    finally:
        conn.close()
    return arryData


def writeToMysql(POOL1, insertdata, data):
    conn = POOL1.connection()
    # 创建游标
    cursor = conn.cursor()
    try:
        cursor.execute(insertdata, (data))
        conn.commit()
        print("插入成功func")
    except Exception as rs:
        conn.rollback()
        print("插入失败func")
        print("funcfault=", rs)
        conn.close()
    finally:
        conn.close()


# 找出数列里面0-1和1-0的序列号并返回次数
def find01_10(arry):
    arry01 = []
    arry10 = []
    i = 0
    for x in range(0, len(arry) - 1):
        if arry[x] == b'\x00' and arry[x + 1] == b'\x01':
            arry01.append(x)
        if arry[x] == b'\x01' and arry[x + 1] == b'\x00':
            arry10.append(x)
    print("arr01=", arry01)
    print("arr10=", arry10)

    for m in range(0, len(arry01)):
        if arry10[m] - arry01[m] > 5:
            i = i + 1
    return i


# 输入时间戳判断班次
def judgeBanci(data):
    a = 115200
    a2 = int(data) % a
    if a2 >= 0 and a2 < 28800:
        banci = "甲班"
    elif a2 >= 28800 and a2 < 57600:
        banci = "乙班"
    elif a2 >= 57600 and a2 < 86400:
        banci = "丙班"
    elif a2 >= 86400 and a2 < 115200:
        banci = "丁班"
    return banci


# 班次筛选，通过时间段，看是夜白中的哪个班次
def checkBanci(hours):
    if hours >= 0 and hours < 8:
        banci = "夜班"
    elif hours >= 8 and hours < 16:
        banci = "白班"
    elif hours >= 16 and hours < 24:
        banci = "中班"
    return banci


# 将日期格式转换为时间戳
def timeStampTransfer(data):
    result = []
    for x in data:
        if x != None:
            time1 = time.mktime(x.timetuple())
            result.append(time1)
        else:
            result.append(0)
    return result


# 将日期格式转换为时间戳
def dateToTimestamp(data):
    time1 = time.mktime(data.timetuple())
    return time1


# 往数据库里面插入数据
def updateToMysql(mysqlinsert, POOLconnect):
    conn = POOLconnect.connection()
    # 创建游标
    cursor = conn.cursor()
    try:
        cursor.execute(mysqlinsert)
        conn.commit()
        print("插入成功func")
    except Exception as rs:
        conn.rollback()
        print("插入失败func")
        print("funcfault=", rs)
        conn.close()
    finally:
        conn.close()


# 找出数据更新到第几个了。看不是None的数据是第几个
def findNotNone(datalist):
    for junreNum in range(len(datalist)):
        if datalist[junreNum] != None:
            print(junreNum)
            break
    return junreNum


# 找出数据更新到第几个了。看不是None的数据是第几个
def findNone(datalist):
    for junreNum in range(len(datalist)):
        if datalist[junreNum] == None:
            print(junreNum)
            break
    return junreNum


# 牟工的秒级区间查询接口
# 牟工的秒级区间查询接口
def miaojiqujianbangcai(data):
    table = ["18", "51", "9", "5", "6", "8", "2", "23", "24", "13", "5", "6", "11", "20", "25", "19", "3", "50", "22",
             "21", "26", "16", "10", "14", "4", "12", "15", "17", "7"]
    url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"  # 秒级数据区间查询
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
    # print("result=", res.text)  # 打印出结果
    data0 = res.text
    data11 = json.loads(data0)  # 将json数据转化为字典数据。
    datalist = data11['data']
    dataall = []  # 总的数量

    # 数据解析，把数据的值读取出来
    for x in range(len(datalist)):
        # print("lendatalist=",len(datalist))
        dat = []
        dattime = []
        # dat.append(datalist[x]["Eid"])
        # dattime.append(datalist[x]["Eid"])
        for y in datalist[x]["datas"]:
            # print("datalist[x]",datalist[x]["datas"])
            # print("y=",y)
            dattime.append(y['timeID'])
            for m in table:
                try:
                    value = y[m]
                    dat.append(value)

                except Exception as e:
                    pass
        dataall.append(dat)
        # dataall.append(dattime)
    # print("dataall=",dataall)
    # print("datalist=", datalist)
    # 温度传感器只有一个的时候返回3个数据，第一个温度，第二，第三个是空气和煤气流量
    if len(dataall) == 3:
        dataReturn = dataall
        return dataReturn
    # 如果温度数据有两个，那么需要判断这个温度数据是否正常，如果不正常那么返回正常的那个，如果都正常那么返回平均值
    elif len(dataall) == 4:
        # 如果两个温度传感器全部都是不等于0，全部正常，那么返回平均值
        list0 = []
        list1 = []
        datatemp = []

        #         print("list0==",list0)
        #         print("list1==",list1)
        #         print("list0[0]==",list0[0])
        #         print("list1[0]==",list1[0])

        # 现将读取出来数据的第一个和第二个进行去除逗号，然后转换成FLOAT型的
        for x in dataall[0]:
            list0.append(float(x.replace(",", "")))
        for x in dataall[1]:
            list1.append(float(x.replace(",", "")))
        print("len(list0)=", len(list0))
        print("len(list1)=", len(list1))
        if len(list0) == 0 and len(list1) == 0:
            datatemp = [0, 0]

        elif len(list0) == 0 and len(list1) != 0:
            datatemp = list1[0]

        elif len(list0) != 0 and len(list1) == 0:
            if type(list0[0]) is not list:
                datatemp = [list0[0]]
            else:
                datatemp = list0[0]

        # 如果两个温度传感器都正常那么取平均值，
        elif list0[0] != 0 and list1[0] != 0:
            for x in range(min(len(list0), len(list1))):
                datatemp.append((list0[x] + list1[x]) / 2)
        # 如果第一个异常，第二个正常，那么取第二个值
        elif list0[0] == 0 and list1[0] != 0:
            datatemp = list1[0]
        # 如果第一个正常，第二个异常，那么取第二个值
        elif list0[0] != 0 and list1[0] == 0:
            datatemp = list0[0]
        # 如果两个都不正常，那么取第一个
        elif list0[0] == 0 and list1[0] == 0:
            datatemp = list0[0]
        dataReturn = [datatemp, dataall[2], dataall[3]]
        return dataReturn


# 求数组的平均值
def avg(list0):
    if list0 != []:
        list1 = []

    if list0 != [] and type(list0[0]) is str:
        for x in list0:
            aa = x.replace(",", "")
            list1.append(float(aa))
        avg0 = round(sum(list1) / len(list1), 3)
    elif list0 != [] and type(list0[0]) is float:
        avg0 = round(sum(list0) / len(list0), 3)
    elif list0 != [] and type(list0[0]) is int:
        avg0 = round(sum(list0) / len(list0), 3)
    elif list0 == []:
        avg0 = 0

    return avg0


#入炉使劲和出炉时间都是出炉辊道正转从1到0状态，出炉热检也检测到信号之后的时间
#计算入炉钢坯数量和温度插入82数据库barroll.gangpiNumber。同时区分是哪个班组的，和他是夜中白班中的哪一个
def inFurnaceBillet():
    global POOL
    try:
        # 从数据库里面读取出来原来的最近一笔的钢坯号。
        sql0 = "SELECT * FROM barroll.gangpiNumber order by timeID desc limit 1;"
        arr0 = readMysql(POOL, sql0)
        recentTime = arr0[0][1]  # 获取最新一笔数据库的时间值
        recentId = arr0[0][3]  # 读取出来的数据ID号
        actId = arr0[0][0]  # 当前ID号
        #print("recentTime", recentTime)
        # 从数据库读取处原始数据
        sql ="SELECT id,timeID,  outsidefurnace_outsidefurnace_RTruluFwd_VALUE as ruluRtFwd," \
              " tempfurnace_tempfurnace_tempInfurnace_VALUE as tempinfunc," \
              "tempmill_millTemp_tempoutfurnace_VALUE as outTemp," \
              "outsidefurnace_outsidefurnace_chugangreverse_VALUE as chugangfwd, " \
              "outsidefurnace_outsidefurnace_chufwd_VALUE    as chugangrev, " \
              "outsidefurnace_outsidefurnace_TreverseQ1_VALUE as Treve1," \
              "outsidefurnace_outsidefurnace_TfwdQ1_VALUE as Tq1fwd," \
              "mill_mill01_mill02_cMillStart_VALUE as cmillstart ," \
              "mill_mill01_mill02_chuluHavStel_VALUE as chuluHveStel, " \
              "mill_mill01_mill03_std1mis_VALUE as std1hstel, " \
               "mill_mill01_mill02_chuluFwd_VALUE  " \
              "FROM barroll.rulugenzong where timeID > " + "\'" + str(recentTime) + "\'" + "order by timeID asc limit 80000;"
        print("sql111111=",sql)
        # 调取数据，将数据从数据库里面读取出来。
        result1 = readMysql(POOL, sql)

        # print("result:", result1)
        id = list(result1[:, 0])  # id号
        timeID = list(result1[:, 1])  # timeID
        rt3_4Fwd = list(result1[:, 2])  # 入炉3-4辊道正转
        tempInFunc = list(result1[:, 3])  # 入炉温度
        tempOutFunc = list(result1[:, 4])  # 出炉温度
        ChuFwd = list(result1[:, 5])  # 出钢机前进
        ChuReverse = list(result1[:, 6])  # 出钢机后退
        T_reverse = list(result1[:, 7])  # 推刚机后退
        T_fwd = list(result1[:, 8])  # 推刚机前进
        #T_PositonPs = list(result1[0:, 9])  # 推刚机原位开关
        cMillrun = list(result1[0:, 9])  # 粗轧区运行信号
        #ChuAuto = list(result1[0:, 10])  # 出钢机自动
        rt5hmd = list(result1[0:, 10])  # 出炉辊道热检信号
        std01Hstel = list(result1[0:, 11])  # 1H含钢信号
        chulu1run = list(result1[0:, 12])  # 1H含钢信号
        # print(len(timeID))
        # print(timeID[0])
        # print("timeID0=", timeID[0], " ", "timeID-1=", timeID[-1])
        # print("id0=", id[0], " ", "id[-1]=", id[-1])

        chugangFWD0_1 = []
        chugangFWD1_0 = []

        T_reverse1_0 = []
        T_reverse0_1 = []

        rt5hmd0_1 = []
        rt5hmd1_0 = []

        # 方法：找出每次推刚机向前推的时候的index,然后将上次推的时候的温度值记录下来。
        for x in range(0, len(T_reverse) - 5):
            # 找出出钢机前进时候由0-1和由1-0时候的index.
            if ChuFwd[x] == b'\x00' and ChuFwd[x + 1] == b'\x01' and ChuFwd[x + 2] == b'\x01':
                chugangFWD0_1.append(x)
            if ChuFwd[x] == b'\x01' and ChuFwd[x+1] == b'\x01' and ChuFwd[x+2] == b'\x01' and ChuFwd[x + 3] == b'\x00' and rt5hmd[x + 2] == b'\x01' and chugangFWD0_1 != [] :
                chugangFWD1_0.append(x)

            # 找出推刚机后退时候由1-0、的点
            if T_reverse[x] == b'\x01' and T_reverse[x + 1] == b'\x01' and T_reverse[x + 2] == b'\x01' and T_reverse[
                x + 3] == b'\x00':
                T_reverse1_0.append(x)



            # 找出出炉辊道由0-1和1-0的数据点，出炉辊道上面的热检的01和10点的时间
            #print("chulu1run[x]=",chulu1run[x])
            if rt5hmd[x] == b'\x00' and rt5hmd[x+1] == b'\x00' and rt5hmd[x + 2] == b'\x01' and rt5hmd[
                x + 3] == b'\x01':  # and ChuAuto == b'\x01':
                rt5hmd0_1.append(x+2)
            if  rt5hmd0_1 != [] and rt5hmd[x] == b'\x01' and rt5hmd[x + 1] == b'\x01' and rt5hmd[
                x + 2] == b'\x00':
                rt5hmd1_0.append(x+2)
        #print("lenchugangFWD0_1=",len(chugangFWD0_1))
        #print("chugangFWD1_0=",chugangFWD1_0)
        print("lenchugangFWD1_0=",len(chugangFWD1_0))
        #print("tuigangjit=",T_reverse1_0)
        print("len(rthmd)=========================================",len(rt5hmd0_1))
    #     print("lenrhmd=",len(rt5hmd1_0))
    #     print("rhmd1_0=",rt5hmd1_0)

    #     for m in
    #     for x in rt5hmd0_1:
            #print(id[x])

        # 找到
        timeID1 = []  # 入钢坯入炉的时候
        tempIn = []  # 入炉钢坯的温度
        idNum = []  # 入炉的钢坯的NUM号
        for m in chugangFWD1_0:
            for x in range(len(T_reverse1_0)):
                if x < len(T_reverse1_0) - 1:
                    #如果出钢机前进信号在两个推刚机的后退信号之间。
                    if m >= T_reverse1_0[x] and m < T_reverse1_0[x + 1]:
                        # print("m=",id[m])
                        # print("T_reverse1_0x=",id[T_reverse1_0[x]])
                        # print("T_reverse1_0x+1=", id[T_reverse1_0[x+1]])
                        timeID1.append(timeID[m])
                        tempIn.append(tempInFunc[T_reverse1_0[x]])
                        idNum.append(id[m])

        if len(tempIn) != 0:
            readGangpiSucc = 1
        else:
            readGangpiSucc = 0
        #print("idnum=",idNum)
        print("lenidnum=",len(idNum))
    #     # 后面加的

        # 从数据库里面读取出来原来的最近一笔的钢坯号。
        # sql0 = "SELECT * FROM barroll.gangpiNumber order by timeID desc limit 1;"
        sql0 = "SELECT * FROM barroll.gangpiNumber order by timeID DESC limit 1;"
        arr0 = readMysql(POOL, sql0)
        recentTime = arr0[0][1]  # 获取最新一笔数据库的时间值
        recentId = arr0[0][3]  # 读取出来的数据ID号
        actId = arr0[0][0]  # 当前ID号
        #print("recentTime", recentTime)


        # 如果有数据，如果第一个数据是0，那么先把0更新，再插入数据
        try:
            if readGangpiSucc == 1:  # 如果读取到钢坯温度数据了，要往数据库里面插入新数据那么就将这个数据更新
                for x in range(len(tempIn)):  # 开始循环写数据
                    hours = int(str(timeID1[x])[10:13])  #找出是什么小时的
                    banci = checkBanci(hours)
                    #将日期格式转换成时间戳
                    time1 = time.mktime(timeID1[x].timetuple())
                    banzu = judgeBanci(time1)   #通过时间来查看是甲乙丙丁哪个班次

                    if recentId == 0:
                        sqldel = "UPDATE  barroll.gangpiNumber SET timeID='" + str(timeID1[x]) + "',tempInFunc = " + str(
                            tempIn[x]) + ",idNumber = " + str(idNum[x]) + ", banzu=" + str(banzu) + ", banci= " + str(banci) + " where id = " + str(actId)
                        updatesql(POOL, sqldel)
                        recentId = 1
                    else:
                        # 插入数据库的data.
                        insertSql = "INSERT INTO gangpiNumber (timeID, tempInFunc, idNumber,banci,banzu) values( %s,%s,%s,%s,%s)"
                        dataInsert = [timeID1[x], tempIn[x], idNum[x], banci,banzu]
                        writeToMysql(POOL, insertSql, dataInsert)
                        print("dataInsert插入的数据是=", dataInsert)
        except  Exception as e:
            print("计算入炉钢坯和插入数据库失败", e)


        # 如果没有读取到钢坯的出钢数据那么执行下面程序,将最新一个钢坯数据的时间戳更新
        try:
            print("开始在末端插入程序")
            if readGangpiSucc == 0:  # 如果从原始数据库里面的数据没有要插入的，那么先查看gangpiNumber 第一个数据是否为0.
                sql0 = "SELECT * FROM barroll.gangpiNumber order by timeID desc limit 1;"

                arr1 = readMysql(POOL, sql0)
                time1 = arr1[0][1]  # 从数据库里面读取出来的第一个时间
                readSqlId = arr1[0][0]  # 从数据库里面读取出来的ID号
                readIdNumber = arr1[0][3]  # 从数据库里面读取出来的第一个ID号
                timeNow = time.time()
                time1StampInsql = int(time.mktime(time1.timetuple()))  # sql里面第一条数据的timestamp
                timeCha = timeNow - time1StampInsql  # 当前时间减去数据库里面的时间戳。
                # print("time1=", time1)
                # print("timeCHA= ", timeCha)
                if arr1[0][3] != 0 and timeCha >= 49000:  # 如果从数据库里面读取出来的第一个数据不是0， 并且当前的时间差和数据库里面的时间差大于49000了，那么把第一个数据插成0
                    # insertSql = "INSERT INTO gangpiNumber (timeID, tempInFunc, idNumber)" \
                    insertSql = "INSERT INTO barroll.gangpiNumber (timeID, tempInFunc, idNumber)" \
                                "values( %s,%s,%s)"
                    dataInsert = [timeID[-1], 0, 0]
                    writeToMysql(POOL, insertSql, dataInsert)
                    #print("cichu charu0")
                elif arr1[0][3] == 0 and timeCha >= 49000:  # 如果原来最后插入的数据是0 并且时间差值大于49000.那么就将原来的数据更新，再插入新的时间
                    # 先将数据库里面0的数据删除。
                    # sqldel = "delete from  gangpiNumber where id = " + str(readSqlId)
                    sqldel = "UPDATE  barroll.gangpiNumber SET timeID='" + str(timeID[-1]) + "',tempInFunc = " + str(
                        0) + ",idNumber = " + str(0) + " where id = " + str(actId)
                    updatesql(POOL, sqldel)
                    #print("原来已经是0，那么更新时间")

        except Exception as e:
            print("错误是：", e)
    except Exception as e:
        print("e1=",e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)

    #print("job1程序运行结束，延迟30秒")
    #time.sleep(40)


# #计算出炉温度数据，此程序用于计算出炉温度
def tempOutFurnace1():
    global POOL
    try:
        print("出路温度开始")
        # 从数据库里面读取出来最新一笔出炉温度的时间
        # 从数据库里面读取出来原来的最近一笔的钢坯号。
        sql0 = "SELECT * FROM barroll.tempOutFunc order by timeID DESC limit 1;"
        arr0 = readMysql(POOL, sql0)
        actId = arr0[0][0]  # 当前ID号
        tempread = arr0[0][2]  # 读取到的第一笔数据温度数据
        recentTime = arr0[0][1]  # 获取最新一笔数据库的时间值
        recentId = arr0[0][3]  # 读取出来的数据ID号

        # print("timeREcent=", recentTime)
        # 如果读取出来的数据是0
        sql = "SELECT id,timeID,  outsidefurnace_outsidefurnace_RTruluFwd_VALUE as ruluRtFwd, " \
              "tempfurnace_tempfurnace_tempInfurnace_VALUE as tempinfunc," \
              "tempmill_millTemp_tempoutfurnace_VALUE as outTemp, " \
              "mill_mill01_mill03_std1mis_VALUE as std1hstel," \
              "mill_mill01_mill03_std2mis_VALUE as std2hstel " \
              "FROM barroll.rulugenzong where timeID > " + "\'" + str(
            recentTime) + "\'" + "order by timeID asc limit 800000;"
        print("sql=", sql)
        # 调取数据，将数据从数据库里面读取出来。
        result1 = readMysql(POOL, sql)

        print("result:", result1)
        id = list(result1[:, 0])  # id号
        timeID = list(result1[:, 1])  # timeID
        rt3_4Fwd = list(result1[:, 2])  # 入炉3-4辊道正转
        tempInFunc = list(result1[:, 3])  # 入炉温度
        tempOutFunc = list(result1[:, 4])  # 出炉温度
        std1haveStel = list(result1[:, 5])  # 1H含钢信号
        std2haveStel = list(result1[:, 6])  # 2H含钢信号
        tempOutFunc2 = tempOutFunc
        outTemp = []

        # print("tempout2====", tempOutFunc2)

        for m2 in range(len(std1haveStel) - 5):
            # print("开始运行入炉温度数据")
            if std1haveStel[m2] == b'\x00' and std1haveStel[m2 + 1] == b'\x01' and std1haveStel[m2 + 2] == b'\x01' and \
                    std1haveStel[m2 + 3] == b'\x01' and std1haveStel[m2 + 4] == b'\x01' and std1haveStel[
                m2 + 5] == b'\x01':  # 检测钢的头部
                outTemp.append(m2 + 5)
            elif outTemp != [] and std1haveStel[m2] == b'\x01' and std1haveStel[m2 + 1] == b'\x01' and std1haveStel[
                m2 + 2] == b'\x01' and std1haveStel[m2 + 3] == b'\x01' and std1haveStel[
                m2 + 4] == b'\x00':  # 检测钢坯的尾部，如果没有先检测出头部，那么就不写入列表
                outTemp.append(m2 + 4)
        # 如果数组长度不能被2整除，那么将最后一个数据去除(最后一个数据就是钢坯的头部数据）
        print("outTemp=", outTemp)
        print("lenoutTemp==================================", len(outTemp))

        # 定义钢坯出炉的第一条信息的初始状态是0
        outTempGangpiStatu = 0
        # 如果出炉温度有数据，并且数据不是2的整数倍，那么数列长度减去1.
        if len(outTemp) != 0 and len(outTemp) % 2 != 0:
            outTemp.pop(-1)
        # 如果读取出来的温度数据是0，那么久将钢坯初始状态定义为0
        if tempread == 0:
            outTempGangpiStatu = 0
        else:
            outTempGangpiStatu = 1

        # 如果出来的列表的长度是0，说明没有数据，那么先查看从数据库里面读取出来的上次存储的数据是否是0，如果是0 ，那么更行时间，如果不是0 ，将数据0写入数据库
        # 如果读取出来的outTemp数据是空的，并且从数据库里面读取出来的温度数据是0，那么更新timeID值。
        if len(outTemp) == 0 and tempread == 0:
            sqlupdate = "UPDATE  barroll.tempOutFunc SET timeID='" + str(timeID[-1]) + "',tempInFunc = " + str(
                0) + ",idNumber = " + str(0) + " where id = " + str(actId)
            updatesql(POOL, sqlupdate)
        # 如果是读取出来的数据第一个是已经是温度数据是0了，那么就更新他的timeID时间
        elif len(outTemp) == 0 and tempread != 0:
            sqlOutTemp = "INSERT INTO barroll.tempOutFunc(timeID, tempOutFunc, idNumber)values( %s,%s,%s)"
            data30 = [timeID[-1], 0, 0]
            writeToMysql(POOL, sqlOutTemp, data30)

        # 如果outTemp不是0，有钢坯数据，那么查看从数据库里面读取出来的钢坯温度数据，如果温度数据是0，那么就更新数据，如果温度不是0，那么就直接插入数据
        # 如果钢坯实际的数据不为0,说明读取到钢坯数据了。
        elif len(outTemp) != 0:
            print("zuihouyige")
            for x in range(0, int(len(outTemp) / 2) - 1):
                timeID3 = timeID[outTemp[2 * x]]  # 头部时候的时间
                idnumber3 = id[outTemp[2 * x]]  # 头部时候的时间点的ID号
                tempOutfunc4 = mean(tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1]])  # 整根钢坯的平均温度。
                # print(";;;;;;;;;;;;;;;",tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1]])
                # print("outTemp[2 * x]=",outTemp[2 * x])
                # print("outTemp[2 * x + 1]=",outTemp[2 * x + 1])

                maxTempOut0 = max(tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1]])  # 钢坯的最大温度
                minTempOut0 = min(tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1]])  # 钢坯的最小温度
                tempOutfunc3 = round(tempOutfunc4, 2)
                maxTempOut = round(maxTempOut0, 2)
                minTempOut = round(minTempOut0, 2)
                # print("maxTempOut------------------------------------------", maxTempOut)
                # print("minTempOut------------------------------------------", minTempOut)

                # print("tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1] ]=",tempOutFunc2[outTemp[2 * x]:outTemp[2 * x + 1] ])
                # print("headOfTemp=", tempOutFunc2[outTemp[2 * x]:outTemp[2 * x] + 5])
                data3 = [timeID3, float(tempOutfunc3), int(idnumber3), maxTempOut, minTempOut]
                if tempread == 0 and outTempGangpiStatu == 0:
                    sqlupdate = "UPDATE  barroll.tempOutFunc SET timeID='" + str(timeID3) + "',tempInFunc = " + str(
                        tempOutfunc3) + ",idNumber = " + str(idnumber3) + ", maxTempOut= " + str(
                        maxTempOut) + ", minTempOut = " + str(minTempOut) + " where id = " + str(actId)
                    # print("sqlupdate===---+++++++++++++++++++++++----", sqlupdate)
                    updatesql(POOL, sqlupdate)
                    print("更新数据成功1")
                    outTempGangpiStatu = 1

                # 其他情况直接写入数据
                else:
                    # print("else=")
                    sqlOutTemp = "INSERT INTO barroll.tempOutFunc(timeID, tempOutFunc, idNumber,maxTempOut, minTempOut)values( %s,%s, %s,%s,%s)"
                    writeToMysql(POOL, sqlOutTemp, data3)
                    # print("插入数据成功")
    except Exception as e:
        print("e2 = ", e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)
    print("tempOutFurnace1程序运行结束")
    # time.sleep(40)


# 1H轧机的头尾还有电流平均值数据查询写入standstel数据库
def std1HeadTailCurrent():
    global POOL
    try:
        # 从数据库里面读取出来原来的最近一笔的钢坯号。
        sql0 = "SELECT * FROM barroll.standstel where millID = 1 order by timeID desc limit 1;"
        arr0 = readMysql(POOL, sql0)
        actId = arr0[0][0]  # 当前ID号
        recentTime = arr0[0][1]  # 获取最新一笔数据库的时间值
        single = arr0[0][6]  # 读取出来的数据ID号

        #print("recentTime", recentTime)

        # 从数据库里面读取数据，将1H含钢的开始时间，结束时间，1H总轧机时间，平均电流计算出来。
        sql = "SELECT id,timeID,  outsidefurnace_outsidefurnace_RTruluFwd_VALUE as ruluRtFwd," \
              "tempfurnace_tempfurnace_tempInfurnace_VALUE as tempinfunc," \
              "tempmill_millTemp_tempoutfurnace_VALUE as outTemp," \
              "outsidefurnace_outsidefurnace_chugangreverse_VALUE as chugangfwd, " \
              "outsidefurnace_outsidefurnace_chufwd_VALUE    as chugangrev, " \
              "outsidefurnace_outsidefurnace_TreverseQ1_VALUE as Treve1," \
              "outsidefurnace_outsidefurnace_TfwdQ1_VALUE as Tq1fwd," \
              "mill_mill01_mill02_cMillStart_VALUE as cmillstart ," \
              "mill_mill01_mill02_chuluHavStel_VALUE as chuluHveStel, " \
              "mill_mill01_mill03_std1mis_VALUE as std1hstel, " \
              "mill_mill01_mill02_chuluFwd_VALUE , " \
              "mill_mill01_mill02_curentStd1_VALUE , " \
              "mill_mill01_mill02_std2haveStelTime_VALUE , " \
              "mill_mill01_mill02_guige_VALUE  " \
              "FROM barroll.rulugenzong where timeID > " + "\'" + str(recentTime) + "\'" + "order by timeID asc limit 80000;"



        print("sql=", sql)
        # 调取数据，将数据从数据库里面读取出来。
        result1 = readMysql(POOL, sql)

        id = list(result1[:, 0])  # id号
        timeID = list(result1[:, 1])  # timeID
        rt3_4Fwd = list(result1[:, 2])  # 入炉3-4辊道正转
        tempInFunc = list(result1[:, 3])  # 入炉温度
        tempOutFunc = list(result1[:, 4])  # 出炉温度
        ChuFwd= list(result1[:, 5])  # 出钢机前进
        ChuReverse = list(result1[:, 6])  # 出钢机后退
        T_reverse = list(result1[:, 7])  # 推刚机后退
        T_fwd = list(result1[:, 8])  # 推刚机前进
        #T_PositonPs = list(result1[0:, 9])  # 推刚机原位开关
        cMillrun = list(result1[0:, 9])  # 粗轧区运行信号
        #ChuAuto = list(result1[0:, 10])  # 出钢机自动
        rt5hmd = list(result1[0:, 10])  # 出炉辊道热检信号
        std01Hstel = list(result1[0:, 11])  # 1H含钢信号
        chulu1run = list(result1[0:, 12])  # 出炉辊道运行
        current1 = list(result1[0:, 13])  # 1H轧机的电流
        rolltimelist = list(result1[0:, 14])  # 钢坯轧制时间
        guigelist = list(result1[0:, 15])  # 钢坯轧制规格



        # 找打含钢信号的头部和尾部

        std1h0_1 = []
        std1h1_0 = []
        for x in range(len(std01Hstel) - 5):
            if std01Hstel[x] == b'\x00' and std01Hstel[x + 1] == b'\x01':  # and ChuAuto == b'\x01':
                std1h0_1.append(x)
            if std01Hstel[x] == b'\x01' and std01Hstel[x + 1] == b'\x00' and std1h0_1 != []:
                std1h1_0.append(x)

        if len(std1h0_1) > len(std1h1_0):  # 如果检测出来的头部信号比尾部信号多，那么就将尾部信号去掉。
            std1h0_1.pop(-1)
        if len(std1h0_1) % 2 != 0:  # 如果读取出来的数据是不能被2整除
            std1h0_1.pop(-1)  # 数组最后一个头部信号去除
            std1h1_0.pop(-1)  # 数组最后一个头部信号去除

        # 如果读取出来的1H的sigle信号数据是0，那么久将1H初始状态定义为0
        if single == 0:
            std1single = 0
        else:
            std1single = 1

        # 将含钢的时长度求出来写入list
        havstelTime = []
        avgcurrent = []
        for x in range(len(std1h0_1)):
            cha1 = std1h1_0[x] - std1h0_1[x]  # 求每根钢的含钢时间
            havstelTime.append(cha1)

            current = round((sum(current1[std1h0_1[x]: std1h1_0[x]])) / cha1, 2)  # 求含钢电流平均值
            avgcurrent.append(current)

        # 如果出来的列表的长度是0，说明没有数据，那么先查看从数据库里面读取出来的上次存储的数据是否是0，如果是0 ，那么更行时间，如果不是0 ，将数据0写入数据库
        # 如果读取出来的std1h0_1数据是空的，并且从数据库里面读取出来的single标志为是0，那么更新timeID值。
        if len(std1h0_1) == 0 and single == 0:  # 如果从原始数据库里面读取出来的数是0，并且从standstel表里面读取出来的single信号是0.那么更新
            sqlupdate = "UPDATE  barroll.standstel SET timeID='" + str(timeID[-1]) + " where id = " + str(actId)
            updatesql(POOL, sqlupdate)
        # 如果列表std1h0_1 是[]，而读取出来的single!=0.那么就插入一条single为0 的数据
        if len(std1h0_1) == 0 and single != 0 and len(timeID) > 78000:
            sqlstd1 = "INSERT INTO barroll.standstel(timeID, single)values( %s,%s)"
            data30 = [timeID[-1], 0]
            print("data3=", data30)
            writeToMysql(POOL, sqlstd1, data30)

        # 如果从std1h0_1不是空的
        if len(std1h0_1) != 0:
            for x in range(len(std1h0_1)):
                timeIDstd1 = timeID[std1h0_1[x]]  # 钢坯头部的时候的时间
                instd1time = timeID[std1h0_1[x]]  # 钢坯头部时间
                outstd1time = timeID[std1h1_0[x]]  # 钢坯尾部时间
                avgcur = avgcurrent[x]  # 此根钢在1H轧机的平均电流值
                millID = 1  # 机架号
                sigle0 = 1
                rolltime = rolltimelist[x]
                guige = guigelist[x]
                datastd1 = [timeIDstd1, instd1time, outstd1time, float(avgcur), millID, sigle0, rolltime,float(guige)]  # 准备往数据库里面插入的数据
                #print("datastd1=", datastd1)

                # 如果是第一个数据0，那么先把原来的sigle 为0的数据更新了。
                if single == 0 and std1single == 0:
                    sqlupdate = "UPDATE barroll.standstel SET timeID='" + str(timeIDstd1) + "',instd1time = '" + str(
                        instd1time) + "',outstd1time = '" + str(outstd1time) + "',avgcurrent = " + str(
                        avgcur) + ",millID = " + str(1) + ",single = " + str(1) + ",rolltime = " + str(
                        rolltimelist[x]) + ",guige = " + str(guigelist[x]) + " where id = " + str(actId)
                   # print("sqlupdata=", sqlupdate)
                    updatesql(POOL, sqlupdate)
                    #print("更新数据成功")
                    std1single = 1
                # 如果不是0，那么直接将数据插入即可
                else:
                    #print("else = ")
                    sqlstdinsert = "INSERT INTO barroll.standstel(timeID, instd1time, outstd1time, avgcurrent, millID, single,rolltime,guige )values( %s,%s, %s,%s, %s,%s,%s,%s)"
                    writeToMysql(POOL, sqlstdinsert, datastd1)
                    #print("插入数据成功")
    except Exception as e:
        print("e3=",e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)




# 此段程序用于将tempOutFurnace1计算出来的出炉时间给插入到数据库里面，让其跟进钢相对应（表barroll.tempOutFunc里面的数据插入barroll.gangpiNumber）
def insertTempOurFunc_InsertGangPiPosition():
    global POOL
    try:
        # 从数据库gangpiNumber里面读取出来原来的最近一笔的钢坯号。
        sql0 = "SELECT * FROM barroll.gangpiNumber order by timeID desc limit 20000;"
        arr0 = readMysql(POOL, sql0)
        actId = arr0[:, 0]  # 当前ID号
        recentTime = arr0[:, 1]  # 获取最新一笔数据库的时间值
        recentId = arr0[:, 2]  # 钢坯温度
        idNumber = arr0[:, 3]  # 读取出来的数据ID号
        timeInyure = arr0[:, 4]  # 钢坯进加热炉预热段的时间
        timeInJiare = arr0[:, 5]  # 进加热段的时间
        timeInJunre = arr0[:, 6]  # 进均热段的时间
        timeOutFuc = arr0[:, 7]  # 出炉到辊道热检时候的时间
        tempOutFunc = arr0[:, 8]  # 出炉时候的温度
        instd1 = arr0[:, 9]  # 进1H轧机的时间
        outstd1 = arr0[:, 10]  # 出1H轧机的时间
        std1avgcurent = arr0[:, 11]  # 在1H轧机时候的平均电流值

        # 从数据库里面查询处理的出炉温度数据
        Tsql0 = "SELECT * FROM barroll.tempOutFunc order by timeID DESC limit 80000;"
        Tarr0 = readMysql(POOL, Tsql0)
        TactId = Tarr0[:, 0]  # 当前ID号
        TrecentTime = Tarr0[:, 1]  # 获取最新一笔数据库的时间值
        Ttempread = Tarr0[:, 2]  # 读取到的第一笔数据温度数据
        TrecentId = Tarr0[:, 3]  # 读取出来的数据ID号

        # 将DATETIME转换成timestamp
        gangpiTime = timeStampTransfer(recentTime)
        outChuluTemTime = timeStampTransfer(TrecentTime)

        # 找出进均热段数据更新到哪个位置了
        yureNum = findNotNone(timeInyure)
        # 找出出炉温度数据更新到哪个位置了
        outFunNum = findNotNone(timeOutFuc)
        # 找出进1H轧机的数据更新到哪个位置了。
        instd1Num = findNotNone(instd1)

        print("yurenum=", yureNum)
        # 首先将出炉的时间确定下来，让后将钢坯在各段的时间确定下来
        # 将钢坯进预热段,加热段，均热段、出炉时间找出来然后插入gangpiNumber
        for x1 in range(len(recentTime) - 157):
            if actId[x1 + 10] <= actId[0] - yureNum:
                print("insertTempOurFunc_InsertGangPiPosition钢坯位置时间插入完毕")
                break
            sqlyure = "update barroll.gangpiNumber set timeInyure = '" + str(recentTime[x1]) + "'  where id = " + str(
                actId[x1 + 10])
            print("sqlyure111111111111=", sqlyure)
            updatesql(POOL, sqlyure)

            # 将钢坯进加热段时间找出来
            sqljiare = "update barroll.gangpiNumber set timeInJiare = '" + str(recentTime[x1]) + "'  where id = " + str(
                actId[x1 + 58])
            updatesql(POOL, sqljiare)
            print("sqljiare222222222222=", sqljiare)

            # 将钢坯进均热段时间找出来
            sqljunre = "update barroll.gangpiNumber set timeInJunre = '" + str(recentTime[x1]) + "'  where id = " + str(
                actId[x1 + 105])
            updatesql(POOL, sqljunre)
            print("sqljunre=", sqljunre)

            # 将钢坯出炉的时间找出来
            sqloutfunc = "update barroll.gangpiNumber set timeOutFuc = '" + str(
                recentTime[x1]) + "'  where id = " + str(
                actId[x1 + 157])
            updatesql(POOL, sqloutfunc)
            print("sqloutfunc=", sqloutfunc)
            print("x1+10=", x1 + 10)
            print("actId[x1 + 10]=", actId[x1 + 10])
            print("actId[0]=", actId[0])



    #             if actId[x1 + 10] <= actId[0] - yureNum:
    #                 print("insertTempOurFunc_InsertGangPiPosition钢坯位置时间插入完毕")
    #                 break
    except Exception as e:
        print("e=", e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)


global outTempTime
outTempTime = 0
# 将1H轧机的各种数据全部读取出来然后插入gangPiNumber数据库
global comptime
comptime = 0


def insertStd1ToGangPiNumber():
    global comptime
    global POOL
    try:
        # 首先查看1H钢坯的数据，barroll.gangpiNumber里面数据更新到哪个位置了。
        sql1H = "SELECT * FROM barroll.gangpiNumber  where instd1 is not Null order by timeID DESC"
        arry1 = readMysql(POOL, sql1H)
        timeIDneed = arry1[0][1]  # 需要的数据更新到的时间点
        timeinstd1 = arry1[0][9]  # instd1最后一次插入数据的时间。
        print("timeIDneed=", timeIDneed)
        print("timeinstd1=", timeinstd1)

        # 从数据库里面读取出来原来的最近一笔的钢坯号。然后通过出炉的时间来确定入1H轧机的温度
        sql0 = "SELECT * FROM barroll.gangpiNumber  where timeID >= '" + str(
            timeIDneed) + "'  order by timeID ASC limit 80000;"
        print("sql0=", sql0)
        arr0 = readMysql(POOL, sql0)
        actId = arr0[:, 0]  # 当前ID号
        recentTime = arr0[:, 1]  # 获取最新一笔数据库的时间值
        recentId = arr0[:, 2]  # 钢坯温度
        idNumber = arr0[:, 3]  # 读取出来的数据ID号
        timeInyure = arr0[:, 4]  # 钢坯进加热炉预热段的时间
        timeInJiare = arr0[:, 5]  # 进加热段的时间
        timeInJunre = arr0[:, 6]  # 进均热段的时间
        timeOutFuc = arr0[:, 7]  # 出炉到辊道热检时候的时间
        tempOutFunc = arr0[:, 8]  # 出炉时候的温度
        instd1 = arr0[:, 9]  # 进1H轧机的时间
        outstd1 = arr0[:, 10]  # 出1H轧机的时间
        std1avgcurent = arr0[:, 11]  # 在1H轧机时候的平均电流值

        # 从数据库standstel里面读取出来最新的2000笔数据
        # sql0 = "SELECT * FROM barroll.standstel where millID = 1 order by timeID desc limit 1;"
        sql1 = "SELECT * FROM barroll.standstel where timeID >='" + str(timeinstd1) + "' order by timeID ASC limit 80000"
        print("sql1=", sql1)
        S1arr0 = readMysql(POOL, sql1)
        S1actId = S1arr0[:, 0]  # 当前ID号
        S1recentTime = S1arr0[:, 1]  # 获取最新一笔数据库的时间值
        S1instd1time = S1arr0[:, 2]  # 进1H轧机的时间
        S1outstd1time = S1arr0[:, 3]  # 出1H轧机的时间
        S1avgcurrent = S1arr0[:, 4]  # 轧制过程中的平均电流
        S1millID = S1arr0[:, 5]  # 读取出来的数据ID号
        S1single = S1arr0[:, 6]  # 数据信号
        S1rolltime = S1arr0[:, 7]  # 钢件轧制时间
        S1guige = S1arr0[:, 8]  # 轧制的规格
        print("time1=", timeOutFuc)
        print("time2=", S1instd1time)

        timeOutFucNum = timeStampTransfer(timeOutFuc)  # 出炉钢坯的时间
        Sinstd1time0 = timeStampTransfer(S1instd1time)  # 进1H轧机的时间


        for x in range(len(timeOutFucNum)):
            print("x==", x)
            if timeOutFucNum[x] == None:
                pass
            else:
                for y in range(len(Sinstd1time0) - 1):
                    if timeOutFucNum[x] > Sinstd1time0[y] and timeOutFucNum[x] < Sinstd1time0[y + 1]:
                        # 如果这条时间数据没有被插入过：
                        if Sinstd1time0[y + 1] != comptime:
                            print("出炉时间=", timeOutFuc[x])
                            print("进1H时间=", S1instd1time[y + 1])
                            print("出炉时间1=", timeOutFucNum[x])
                            print("进1H时间1=", Sinstd1time0[y + 1])
                            sql1 = "update  barroll.gangpiNumber  set " + "instd1 = '" + str(
                                S1instd1time[y + 1]) + "', outstd1 = '" + str(
                                S1outstd1time[y + 1]) + "', std1avgcurent = " + str(
                                S1avgcurrent[y + 1]) + ", rolltime = " + str(
                                (S1rolltime[y + 1]) * 0.01) + ", guige = " + str(
                                S1guige[y + 1]) + "  where id = " + str(actId[x])
                            # print("sql1=", sql1)
                            comptime = Sinstd1time0[y + 1]  # 将时间赋值。
                            updatesql(POOL, sql1)
                            break
                        elif timeOutFucNum[x] > Sinstd1time0[y]:
                            pass
                            print("时间重复，跳过")

    except Exception as e:
        print("e=",e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)




# # #计算钢坯的预热段，加热段，均热段的平均用的温度流量，各段持续时间等
def caculateGangPiAvg():
    global POOL
    try:
# 查询数据，看哪些数据没有插入新的数据
        sqlnull = "SELECT * FROM barroll.gangpiNumber WHERE yureAvgTemp is not null order by timeID desc limit 10"
        arrynull = readMysql(POOL, sqlnull)
        if arrynull.size == 0:
            sqlnull0 = "SELECT * FROM barroll.gangpiNumber  order by timeID asc limit 10"
            arrynull0 = readMysql(POOL, sqlnull0)
            timenull = arrynull0[0][1]
        else:
            timenull = arrynull[0][1]  # 需要的时间
        sqltimeout = "SELECT * FROM barroll.gangpiNumber where timeOutFuc is not null order by timeID desc limit 10"
        arryout = readMysql(POOL, sqltimeout)
        timeout = arryout[0][7]  # 需要的时间
        # 查看gangpiNumber 数据库
        sql0 = "SELECT * FROM barroll.gangpiNumber where timeID between '"+ str(timenull)+"' and '"+ str(timeout)+"' order by timeID asc limit 300000"
        #sql0 = "SELECT * FROM barroll.gangpiNumber where timeID between '2022-05-30 16:53:50' and '2022-06-01 14:59:12' order by timeID DESC limit 300000"
        print("sql0=", sql0)
        arr0 = readMysql(POOL, sql0)
        actId = arr0[:, 0]  # 当前ID号
        recentTime = arr0[:, 1]  # 获取最新一笔数据库的时间值
        recentId = arr0[:, 2]  # 钢坯温度
        idNumber = arr0[:, 3]  # 读取出来的数据ID号
        timeInyure = arr0[:, 4]  # 钢坯进加热炉预热段的时间
        timeInJiare = arr0[:, 5]  # 进加热段的时间
        timeInJunre = arr0[:, 6]  # 进均热段的时间
        timeOutFuc = arr0[:, 7]  # 出炉到辊道热检时候的时间
        tempOutFunc = arr0[:, 8]  # 出炉时候的温度
        instd1 = arr0[:, 9]  # 进1H轧机的时间
        outstd1 = arr0[:, 10]  # 出1H轧机的时间
        std1avgcurent = arr0[:, 11]  # 在1H轧机时候的平均电流值

        yureContainTime = arr0[:, 16]  # 预热热在炉时间
        jiareContainTime = arr0[:, 17]  # 加热热在炉时间
        junreContainTime = arr0[:, 18]  # 均热热在炉时间
        yureAvgTemp = arr0[:, 19]  # 预热段平均温度
        jiareAvgTemp = arr0[:, 20]  # 加热热在炉时间
        junreAvgTemp = arr0[:, 21]  # 均热热在炉时间
        furnaceContainTime = arr0[:, 22]  # 预热热在炉时间
        timeOrderGangpi = recentTime[0]

        # 一段炉内温度A   一段炉内温度B   一段空气流量      一段煤气流量
        eid1duan = ["ba3a5127", "095fea40", "1a5637c6", "d7e5aaa4"]
        # 二段炉内温度A    二段炉内温度B   二段空气流量      二段煤气流量
        eid2duan = ["84b5aa87", "d9d0a8b7", "6e18a564", "6e8694af"]
        # 三段炉内温度A  三段炉内温度B  三段空气流量      三段煤气流量
        eid3duan = ["f7b81560", "f7decd45", "e5baf567", "3eaa673b"]
        eidlist = [eid1duan, eid2duan, eid3duan]
        # 将各段的参数全部计算出来插入数据库。

        dataTranfer = {
            "id": ["725d59d5"],
            "beginTime": "2021-10-13 08:00:00",
            "endTime": "2021-10-13 08:50:00",
            "limit": 90000000,
            "orderBy": "desc"}  # desc倒序排列，asc正序排列
        for data in arr0:
            #print("lenarr0=", len(arr0))
            # print("arr0==",arr0)
            # 如果出炉时间，不是NONE,那么执行那一步

            if data[7] != None:
                #print("data==",data)
                huaguiContainTime = round((dateToTimestamp(data[4]) - dateToTimestamp(data[1])) / 60, 2)  # 滑轨停留时间
                yureContainTime = round((dateToTimestamp(data[5]) - dateToTimestamp(data[4])) / 60, 2)  # 预热停留时间
                jiareContainTime = round((dateToTimestamp(data[6]) - dateToTimestamp(data[5])) / 60, 2)  # 加热停留时间
                junreContainTime = round((dateToTimestamp(data[7]) - dateToTimestamp(data[6])) / 60, 2)  # 均热停留时间
                furnaceContainTime = round((dateToTimestamp(data[7]) - dateToTimestamp(data[4])) / 60, 2)  # 加热炉停留时间
                # 预热段数据计算
                dataTranfer["id"] = eidlist[0]
                dataTranfer["beginTime"] = str(data[4])
                dataTranfer["endTime"] = str(data[5])
                # print("dataTranfer=",dataTranfer)
                yure1 = miaojiqujianbangcai(dataTranfer)
                # print("yure1=",yure1)
                # print("avggggggg=",avg(yure1[0]))

                # 加热段数据计算
                dataTranfer["id"] = eidlist[1]
                dataTranfer["beginTime"] = str(data[5])
                dataTranfer["endTime"] = str(data[6])
                # print("dataTranfer=",dataTranfer)
                jiare2 = miaojiqujianbangcai(dataTranfer)

                # 均热段数据计算
                dataTranfer["id"] = eidlist[2]
                dataTranfer["beginTime"] = str(data[6])
                dataTranfer["endTime"] = str(data[7])
                # print("dataTranfer=",dataTranfer)
                junre3 = miaojiqujianbangcai(dataTranfer)
                # print("junre3=",junre3)
                # 滑轨停留时间        预热停留时间   加热停留时间      均热停留时间    在炉时间           预热温度      加热温度       均热温度        预热空气     加热空气        均热空气       预热煤气       加热煤气      均热煤气
                feedback0 = [huaguiContainTime, yureContainTime, jiareContainTime, junreContainTime, furnaceContainTime,
                             avg(yure1[0]), avg(jiare2[0]), avg(junre3[0]), avg(yure1[1]), avg(jiare2[1]),
                             avg(junre3[1]), avg(yure1[2]), avg(jiare2[2]), avg(junre3[2])]
                # print("feedback00000000=",feedback0)
                # sqlinsert = ""UPDATE  barroll.gangpiNumber SET timeID='" + str(huaguiContainTime) + "',instd1time = '" + str(instd1time) + "',outstd1time = '" + str(outstd1time) +"',avgcurrent = " + str(avgcur) +",millID = " + str(1) + ",single = " + str(1) +",rolltime = " + str(rolltimelist[x]) +",guige = " + str(guigelist[x])+  " where id = " + str(actId) "
                sqlinsert = "UPDATE  barroll.gangpiNumber SET huaguiContainTime =" + str(
                    huaguiContainTime) + " ,yureContainTime = " + str(yureContainTime) + " ,jiareContainTime = " + str(
                    jiareContainTime) + " ,junreContainTime = " + str(
                    junreContainTime) + " ,furnaceContainTime = " + str(furnaceContainTime) + " ,yureAvgTemp = " + str(
                    avg(yure1[0])) + " ,jiareAvgTemp = " + str(avg(jiare2[0])) + " ,junreAvgTemp = " + str(
                    avg(junre3[0])) + " ,yureAvgAir = " + str(avg(yure1[1])) + " ,jiareAvgAir = " + str(
                    avg(jiare2[1])) + " ,junreAvgAir = " + str(avg(junre3[1])) + " ,yureAvgGas = " + str(
                    avg(yure1[2])) + " ,jiareAvgGas = " + str(avg(jiare2[2])) + " ,junreAvgGas = " + str(
                    avg(junre3[2])) + " where id = " + str(data[0])
                #print("data0=====", data[0])
                #print("sqlinset=", sqlinsert)
                updatesql(POOL, sqlinsert)
                        # break
    except Exception as e:
        print("计算平均值有错误：", e)
        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)


# 将出炉温度插入gangpiNumber
# 找出出炉温度,然后将出炉温度插入相对应的钢坯信号里面。
# 根据1H轧机的含钢信号来确定出炉温度的位置，如果出炉温度的时间在1H和2H之间

# 查询数据，看哪些数据没有插入新的数据
def insertOutTemp():
    global POOL
    timeInstd1Compare = 0
    try:
        sqlnull = "SELECT * FROM barroll.gangpiNumber WHERE tempOutFunc is not null order by timeID desc limit 10"
        arrynull = readMysql(POOL, sqlnull)
        if arrynull.size == 0:
            sqlnull0 = "SELECT * FROM barroll.gangpiNumber  order by timeID asc limit 10"
            arrynull0 = readMysql(POOL, sqlnull0)
            timenull = arrynull0[0][1]
        else:
            timenull = arrynull[0][1]  # 需要的时间

        # 从数据库里面读取出来最新一笔的数据。然后通过1H轧机的含钢信号的咬钢和吐钢时间来确定温度数据。
        sql0 = "SELECT * FROM barroll.gangpiNumber  where timeID >= '" + str(
            timenull) + "'  order by timeID ASC limit 80000;"
        print("sql0=", sql0)
        arr0 = readMysql(POOL, sql0)
        actId = arr0[:, 0]  # 当前ID号
        recentTime = arr0[:, 1]  # 获取最新一笔数据库的时间值
        recentId = arr0[:, 2]  # 钢坯温度
        idNumber = arr0[:, 3]  # 读取出来的数据ID号
        timeInyure = arr0[:, 4]  # 钢坯进加热炉预热段的时间
        timeInJiare = arr0[:, 5]  # 进加热段的时间
        timeInJunre = arr0[:, 6]  # 进均热段的时间
        timeOutFuc = arr0[:, 7]  # 出炉到辊道热检时候的时间
        tempOutFunc = arr0[:, 8]  # 出炉时候的温度
        instd1 = arr0[:, 9]  # 进1H轧机的时间
        outstd1 = arr0[:, 10]  # 出1H轧机的时间
        std1avgcurent = arr0[:, 11]  # 在1H轧机时候的平均电流值

        # 找出出炉温度表tempOUTfunc里面的数据
        Tsql0 = "SELECT * FROM barroll.tempOutFunc  where timeID >= '" + str(
            timenull) + "'  order by timeID ASC limit 80000;"
        print("Tsql0=",Tsql0)
        Tarr0 = readMysql(POOL, Tsql0)
        TactId = Tarr0[:, 0]  # 当前ID号
        TrecentTime = Tarr0[:, 1]  # 获取最新一笔数据库的时间值
        Ttempread = Tarr0[:, 2]  # 读取到的第一笔数据温度数据
        TrecentId = Tarr0[:, 3]  # 读取出来的数据ID号
        maxTempOut = Tarr0[:, 4]  # 温度最大值
        minTempOut = Tarr0[:, 5]  # 温度最小值

        timeInStd1 = timeStampTransfer(instd1)  # 进1H轧机的时间
        timeOutStd1 = timeStampTransfer(outstd1)  # 出1H轧机的时间
        timeOutTemp = timeStampTransfer(TrecentTime)  # 出炉温度的时间

        # 将数据插入
        for x in range(len(timeOutTemp)):
            for y in range(len(timeInStd1)):
                # 不包括数组timeInStd1最后一个数据的时候
                if y < len(timeInStd1) - 1:
                    # 如果出炉温度的时间比1H咬钢时间大，但是又比1H咬钢时间加15秒要小。那么温度匹配。
                    if timeOutTemp[x] > timeInStd1[y] and timeOutTemp[x] < timeOutStd1[y]:
                        # 避免重复插入数据
                        if timeInStd1[y] != timeInstd1Compare:
                            print("timeOutTemp=", timeOutTemp[x])
                            print("timeInStd1[y]=", timeInStd1[y])
                            print("timeOutStd1[y]=", timeOutStd1[y])
                            sql1 = "update  barroll.gangpiNumber  set " + " tempOutFunc = " + str(
                                Ttempread[x]) + ", maxTempOutFunc = " + str(
                                maxTempOut[x]) + ",  minTempOutFunc = " + str(minTempOut[x]) + " where id = " + str(
                                actId[y])

                            print("sql01=", sql1)
                            updatesql(POOL, sql1)
                            timeInstd1Compare = timeInStd1[y]
                            break
                    # 还有一些情况是时间戳为NULL的被替换成0了，那么我们就将时间戳修改下
                    elif timeOutTemp[x] > timeInStd1[y] and timeOutStd1[y + 1] == 0 and timeOutTemp[x] < timeInStd1[y] +20:
                        # 避免重复插入数据
                        if timeInStd1[y] != timeInstd1Compare:
                            print("timeOutTemp=", timeOutTemp[x])
                            print("timeInStd1[y]=", timeInStd1[y])
                            print("timeOutStd1[y]=", timeOutStd1[y])
                            sql1 = "update  barroll.gangpiNumber  set " + " tempOutFunc = " + str(
                                Ttempread[x]) + ", maxTempOutFunc = " + str(
                                maxTempOut[x]) + ",  minTempOutFunc = " + str(minTempOut[x]) + " where id = " + str(
                                actId[y])

                            print("sql02=", sql1)
                            updatesql(POOL, sql1)
                            timeInstd1Compare = timeInStd1[y]
                            break
                # 最后一个数据的插入
                elif y == len(timeInStd1) - 1:
                    if timeOutTemp[x] > timeInStd1[y] and timeOutTemp[x] < timeInStd1[y] + 30:
                        # 最后一个数据的插入。
                        if timeInStd1[y] != timeInstd1Compare:
                            print("timeOutTemp=", timeOutTemp[x])
                            print("timeInStd1[y]=", timeInStd1[y])
                            print("timeOutStd1[y]=", timeOutStd1[y])
                            sql1 = "update  barroll.gangpiNumber  set " + " tempOutFunc = " + str(
                                Ttempread[x]) + ", maxTempOutFunc = " + str(
                                maxTempOut[x]) + ",  minTempOutFunc = " + str(minTempOut[x]) + " where id = " + str(
                                actId[y])

                            print("sql03=", sql1)
                            updatesql(POOL, sql1)
                            timeInstd1Compare = timeInStd1[y]
                            break
        # # 将数据插入
        # for x in range(len(timeOutTemp)):
        #     for y in range(len(timeInStd1) - 1):
        #         # 如果出炉温度的时间比1H咬钢时间大，但是又比1H咬钢时间加15秒要小。那么温度匹配。
        #         if timeOutTemp[x] > timeInStd1[y] and timeOutTemp[x] < timeOutStd1[y + 1]:
        #             # 避免重复插入数据
        #             if timeInStd1[y] != timeInstd1Compare:
        #                 print("timeOutTemp=", timeOutTemp[x])
        #                 print("timeInStd1[y]=", timeInStd1[y])
        #                 print("timeOutStd1[y]=", timeOutStd1[y])
        #                 sql1 = "update  barroll.gangpiNumber  set " + " tempOutFunc = " + str(
        #                     Ttempread[x]) + ", maxTempOutFunc = " + str(
        #                     maxTempOut[x]) + ",  minTempOutFunc = " + str(minTempOut[x]) + " where id = " + str(
        #                     actId[y])
        #
        #                 print("sql1=", sql1)
        #                 updatesql(POOL, sql1)
        #                 timeInstd1Compare = timeInStd1[y]
        #                 break

    except Exception as e:
        print("错误是：", e)

        try:
            if str(e)=="(0, '')":
                print("重新连接1")
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
                    database='barroll',
                    charset='utf8'
                )
        except Exception as e:
            print("又一次的报错：", e)


#主要运行的程序
def mainDef():
    while True:
        try:
            inFurnaceBillet()
            print("inFurnaceBillet结束")
            tempOutFurnace1()
            print("tempOutFurnace1结束")
            std1HeadTailCurrent()
            print("std1HeadTailCurrent结束")
            insertTempOurFunc_InsertGangPiPosition()
            print("insertTempOurFunc_InsertGangPiPosition结束")
            insertStd1ToGangPiNumber()
            print("insertStd1ToGangPiNumber结束")
            caculateGangPiAvg()
            print("caculateGangPiAvg结束")
            insertOutTemp()
            print("insertOutTemp结束")
        except Exception as e:
            print("出现错误错误为：", e)
        print("程序总体运行结束，等待30秒====================================")
        time.sleep(30)


mainDef()