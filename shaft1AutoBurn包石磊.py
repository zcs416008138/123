# coding:utf-8 用内存作为默认的作业存储器
 #此程序是用于130吨锅炉采集数据程序创建于20200710日
import datetime
import time
from HslCommunication import SiemensS7Net
from HslCommunication import SiemensPLCS
import numpy as np
import pymysql
from DBUtils.PooledDB import PooledDB

#180平智能燃烧，其中用到的有OPC模块，1，需要安装库文件：pip install cryptography==2.4.2 --only-binary=:all:,
import sys
sys.path.insert(0, "..")
from opcua import Client,ua
#import matplotlib.pyplot as plt
import threading
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
from datetime import datetime
from HslCommunication import *
import numpy as np
import time




heart1s = False
timeHeart1s = 0
global timeNow

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
    host= '10.0.106.19',
    port=3306,
    user='furnace',
    password='furnace',
    database='shaft8a',
    charset='utf8'
)





# 将数据库里面的数据全部读取出来，然后写成矩阵形式返回。
def readMysqlToArry( mysql1, length):
    conn = POOL.connection()
    cursor = conn.cursor()
    # print("mysql1:", mysql1)
    try:
        cursor.execute(mysql1)
        ccc = []
        for x in cursor.fetchmany(size=length):
            ccc.append(list(x))
        # 将数据库里面读取出来的数据bbb全部写成矩阵形式。
        arr1 = np.array(ccc)
        conn.commit()
        print("读取数据库成功")
    except Exception as r:
        conn.rollback()
        print("读取数据库失败")
        print("故障码：", r)
        conn.close()
    finally:
        conn.close()
    return arr1

#总阀压力控制
def mainValveControl(presureSet, actPresure, valveAct,avg1,addtime1):
    global timeNow
    valve1 = valveAct
    mainVTime = timeNow
    if presureSet > actPresure:
        if presureSet - actPresure >= 2000 and presureSet - avg1 >= 1800:
            valve1 = valveAct + 3
            mainVTime = mainValveTime(addtime1)
        elif presureSet - actPresure >= 1000 and presureSet - avg1 >= 800:
            valve1 = valveAct + 2
            mainVTime = mainValveTime(addtime1)

    elif presureSet < actPresure:
        if actPresure - presureSet >= 2000 and actPresure - avg1 >= 1800:
            valve1 = valveAct - 3
            mainVTime = mainValveTime(addtime1)
        elif actPresure - presureSet >= 1000 and actPresure - avg1 >= 1000:
            valve1 = valveAct - 2
            mainVTime = mainValveTime(addtime1)
    return valve1,mainVTime




#阀门控制程序： 流量设定值，流量实际值，流量3秒平均值，调整步宽，当前阀门开度给定值，加的时间秒数
def valveAuto(set,act,avg,step,presentValve,addtime):
    global timeNow
    valveSet = presentValve
    timeSingle = timeNow
    #####如果阀门的开度是大于5的，但是实际值是0，那么就保持当前阀门开度不动。
    #如果实际阀门开度大于5，但是实际的流量却小于10（也就是流量不正常）那么这次就不进行调节，还是按照原来的阀门给定给出去。
    if presentValve > 5 and act < 100:
        # 首先读取当前阀门阀位设定值：
        valveSet = presentValve
        timeSingle = mainValveTime(addtime)

    else:
        if set > act:
            #首先读取当前阀门阀位设定值：
            valveSet = presentValve
            #设定压力如果大于实际压力将阀门开度加大。
            if (set - act > step) and (set - avg > 0.9*step):
                valveSet = presentValve + 2
                timeSingle = mainValveTime(addtime)
            elif (set - act > 0.5*step) and (set - avg > 0.45*step):
                valveSet = presentValve + 1
                timeSingle = mainValveTime(addtime)

            #设定压力小于实际压力将阀门开度减小
        elif set < act:
            if (act - set > step) and (avg - set > 0.9*step):
                valveSet = presentValve - 2
                timeSingle = mainValveTime(addtime)
            elif (act - set > 0.5*step) and (avg - set > 0.45*step):
                valveSet = presentValve - 1
                timeSingle = mainValveTime(addtime)
    return valveSet, timeSingle


#温度控制     实际温度  设定温度  调节温度范围, 设定的煤气流量, 流量增减量， 轮询周期s
def tempAdjust(actTemp, setTemp,  fanwei,        setGasFlow,     liuliangAdd, addtime1):
    global timeNow
    nextTime = timeNow
    if actTemp > setTemp + fanwei:
        setGasFlow = setGasFlow - liuliangAdd
        nextTime = mainValveTime(addtime1)
    elif actTemp < setTemp - fanwei:
        setGasFlow = setGasFlow + liuliangAdd
        nextTime = mainValveTime(addtime1)
    return setGasFlow, nextTime




#阀门检测周期确定。
def mainValveTime(addSecond):
    global  timeNow
    nextTime = timeNow + addSecond
    return nextTime

def maxminvalve(data,max,min):
    data1 = data
    if data>=max:
        data1 = max
    elif data<=min:
        data1 = min
    return data1

#把string格式转换为timestamp，
#time3='20200821123423'转换为时间戳 t1= 1653461032.0
def stringDateTimeToTimeStamp(timedata):
    time0 = str(timedata)
    time1 = time0[0:14]
    t1 = time.mktime(time.strptime(time1, '%Y%m%d%H%M%S'))
    #print("t1=", t1)
    return t1


#检测从数据库读取出来的数据时间，如果时间和当前时间差8秒，那么认为数据库的数据异常，断开控制连接
def checkMysqlDataFault(timeFrmSql):
    timeFrmSql01Timestamp = stringDateTimeToTimeStamp(timeFrmSql)
    timeNow0 = int(time.time())
    if timeFrmSql01Timestamp < int(timeNow0) - 8:
        print("数据库连接中断")
        connectMysql = 0
    else:
        connectMysql = 1
    return connectMysql





 # 煤气阀门调节程序
    #       实际流量、设定流量、3秒平均流量、差值范围   、阀位实际值  阀位当前给定值       当前时间
def flowAdjust(gas_F, gasSet, gasAvg3s, gasFlowRange1, valveActual, gasMainValveGiven, timeNow):
    timeGas = timeNow
    valvefault = 0
    gasValveSet = gasMainValveGiven
    # 防止阀门损坏，然后报警
    # if abs(gasMainValveGiven - valveActual)>=4:
    #     gasValveSet = gasMainValveGiven
    #     valvefault=1  #阀门异常
    if valveActual > 5 and gas_F < 500:
        gasValveSet = gasMainValveGiven
        valvefault = 1  # 流量异常
    else:
        if gas_F > gasSet + gasFlowRange1 and gasAvg3s > gasSet + gasFlowRange1:
            gasValveSet = gasMainValveGiven - 1
            print("关小1个阀门开度")
            timeGas = timeNow + 5

        if gas_F < gasSet - gasFlowRange1 and gasAvg3s < gasSet - gasFlowRange1:
            gasValveSet = gasMainValveGiven + 1
            print("开大1个阀门开度")
            timeGas = timeNow + 5
    return gasValveSet, timeGas, valvefault


#阀门开度限制程序
def valveLimt(valveset,high,low):
    valve = valveset
    if valveset>=high:
        valve = high
    elif valveset<= low:
        valve = low
    return valve


time1s = 0        #总的按照一秒一扫描
firstScanSouth = 0   #初次扫描
time60 = 0         #60秒检测周期
timeGasFlow = 0
timeAirFlow = 0
time1 = 0     #30秒温度循环检测
burnMode = 0    #烧炉模式   0为正常流量燃烧， 1为升温模式， 2为减温模式

while True:
    timeNow = int(time.time())
    timeID0 = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 日期时间，来源 比特量化
    if timeNow >= time1s:

        print("timeNow=",timeNow)
        timetest1 = time.time()
#将竖炉公共的数据从数据库读取出来
        sql01Main = "SELECT * FROM shaft8a.shaftmain order by timeID DESC limit 1200"
        arr01Main = readMysqlToArry(sql01Main, 1200)    #读取本地数据库函数。

        #将最新数据转换为数组。
        listNowMain = list(arr01Main[0])
        #print("listNowMain=", listNowMain)
        timeIDMain = listNowMain[0]
        gasPressure = listNowMain[1]
        airPressure = listNowMain[2]
        coolAirPress = listNowMain[3]
        coolAirFlow = listNowMain[4]
        dryBedTemA = listNowMain[5]
        dryBedTemB = listNowMain[6]
        exhaustGasTemA = listNowMain[7]
        exhaustGasTemB = listNowMain[8]
        coolBeltTemA = listNowMain[9]
        coolBeltTemB = listNowMain[10]
        isAuto = listNowMain[11]



#将竖炉单独的数据从数据库读取出来。
        sql01 = "SELECT * FROM shaft8a.shaftzone where zoneID=1  order by timeID DESC limit 100"
        arr01 = readMysqlToArry(sql01, 100)  # 读取本地数据库函数。
        listNow01 = arr01[0]
        #print("listNow01=",listNow01)
        timeID = listNow01[0]              #时间戳
        zoneID = listNow01[1]              #zoneID
        airFlow = listNow01[2]             #南助燃空气流量
        gasFlow = listNow01[3]             #南煤气流量
        furnacePress = listNow01[4]        #南燃烧室压力
        valveGivenAir = listNow01[5]       #助燃空气阀门给定
        valveGivenGas = listNow01[6]       #南煤气给定
        valveActualAir = listNow01[7]      #南助燃空气阀门实际值
        valveActualGas = listNow01[8]      #南煤气阀门实际值
        furnaceTemA = listNow01[9]         #南燃烧室温度
        fireZoneTemA = listNow01[10]
        fireZoneTemB = listNow01[11]
        guideWallTemA = listNow01[12]      #东导风墙出口温度
        guideWallTemB = listNow01[13]      #东导风墙入口温度
        tempGiven = listNow01[14]          #给定温度


        #判断数据库是否连接中断
        connectMysqlMain = checkMysqlDataFault(timeIDMain)    #检测从MAIN函数里面读取出来的数据开时间戳是否正常
        connectMysql01 = checkMysqlDataFault(timeID)          #检测从shaftZone里面读取出来的数据，看是否正常
        print("connectMysqlMain=", connectMysqlMain, connectMysql01)

        print("valveGivenGas=",valveGivenGas)




#数据预处理块

        # gasDivideTemp = sum(arr01[:, 3]) / sum(arr01[:, 9])  # 求10分钟平均每度需要的煤气流量
        # # print("zonghe=",gasDivideTemp*tempGiven[0])
        # gasHighLimit = round(float(gasDivideTemp) * 1.15 * float(tempGiven), 2)  # 每度流量的上限
        # gasLowLimit = round(float(gasDivideTemp) * 0.85 * float(tempGiven), 2)  # 梅毒流量的下线
        # print("煤气流量上限=", gasHighLimit)
        # print("煤气流量下限=", gasLowLimit)


        gasFlowAvg3s = sum(arr01[:, 3][0:4]) / 4  #
        airFlowAvg3s = sum(arr01[:, 2][0:4]) / 4  #
        TemAAvg4s = sum(arr01[:, 9][0:4]) / 4  #
        tempCha = (sum(arr01[:, 9][0:5]) - sum(arr01[:, 9][60:65]))/5     #温度差，当前5秒的温度和减去

        tempRange = 5         #温度调节第一阶梯
        tempRange2 = 10       #温度调节第二阶梯
        gasFlowRange = 120    #煤气流量调节阶梯
        airFlowRange = 120    #空气流量调节阶梯



        print("gasFlowAvg3s=", gasFlowAvg3s)
        print("airFlowAvg3s=", airFlowAvg3s)
        print("furnaceTemAAvg4s=", TemAAvg4s)






        # 首先判断数据库是否有异常，如果有异常，那么就不调节了
        # 如果是手动模式，或者是和数据库连接异常的时候，那么把实际值赋值给设定值
        if isAuto == 0 or (connectMysqlMain + connectMysql01) != 2:
            gasFlowSet = gasFlow  # 煤气流量计给定值
            airFlowSet = float(gasFlowSet) * 1.14  # 空气流量给定值
            airValveSet = valveGivenAir  # 空气阀门开度给定
            gasValveSet = valveGivenGas  # 煤气阀门开度给定
            firstScanSouth = 0



        # 如果在自动模式时候，那么开始自动烧炉程序
        elif isAuto == 1:
            # 初次扫描，将阀门之类的数据赋值。
            if firstScanSouth == 0:  #
                gasFlowSet = gasFlow  # 煤气流量计给定值
                airFlowSet = float(gasFlowSet) * 1.14  # 空气流量给定值
                airValveSet = valveGivenAir  # 空气阀门开度给定
                gasValveSet = valveGivenGas  # 煤气阀门开度给定
                firstScanSouth == 1

#在此判断是烧炉模式，0为正常，1为加温，2为减温模式
        tempGivenList = arr01[:, 14]  #温度给定数组
        if tempGivenList[-1] != tempGivenList[-2]:
            if tempGivenList[-1] > furnaceTemA:
                burnMode = 1    #如果设定值比实际值大，那么是升温模式
                maxGasFlowSet = 6400
                minGasFlow = 5500
                airGasRatio = 1.08
                gasFlowSet = maxGasFlowSet
                airFlowSet = gasFlowSet * airGasRatio

            elif tempGivenList[-1] < furnaceTemA:
                burnMode = 2  # 如果设定值比实际值小，那么是减温模式
                maxGasFlowSet = 4800
                minGasFlow = 4400
                airGasRatio = 1.2
                gasFlowSet = maxGasFlowSet
                airFlowSet = gasFlowSet * airGasRatio


 #用来判断什么时候升温或者降温模式结束，如果是升温模式，如果实际值比给定值大了，那么恢复正常模式
        if burnMode == 1:
            if furnaceTemA >= tempGiven:
                burnMode = 0
                maxGasFlowSet = 5400
                minGasFlow = 4800
                airGasRatio = 1.14
                gasFlowSet = maxGasFlowSet
                airFlowSet = gasFlowSet * airGasRatio



        #如果是减温模式，实际比设定要小了，恢复正常模式
        elif burnMode == 2:
            if furnaceTemA <= tempGiven:
                burnMode = 0
                maxGasFlowSet = 5400
                minGasFlow = 4800
                airGasRatio = 1.14
                gasFlowSet = maxGasFlowSet
                airFlowSet = gasFlowSet * airGasRatio






#开始温度控制程序
            # 如果到了下一个检测温度的时间周期：那么开始检测和执行调整煤气设定值
            # 每30秒检测一个温度周期。
        if burnMode == 0: #正常模式
            #如果煤气压力在16KP到24Kp之间的时候煤气流量最大5400.其他时候煤气流量最大6000.
            if  gasPressure >=16:
                maxGasFlowSet = 5400
                minGasFlow = 4800
                airGasRatio = 1.14
            else:
                maxGasFlowSet = 6000
                minGasFlow = 4800
                airGasRatio = 1.14

        if timeNow >= time60:
            #如果实际温度设定值比实际值大，那么减流量100
            if furnaceTemA >= tempGiven + 3:
                gasFlowSet = gasFlowSet - 100
            elif  furnaceTemA <= tempGiven-3:
                gasFlowSet = gasFlowSet + 100

            #空气流量设置
            airFlowSet = float(gasFlowSet) * airGasRatio


        #流量比对上下线限定
        if gasFlowSet >= maxGasFlowSet:
            gasFlowSet = maxGasFlowSet
        elif gasFlowSet <= minGasFlow:
            gasFlowSet = minGasFlow


            #流量设置控制阀门



#以下是煤气和空气阀门控制程序


        if isAuto == 1:
            print("煤气流量给定=", gasFlowSet)
            if timeNow >= timeGasFlow:
                print("lljjjjj")
                (gasValveSet, timeGasFlow, gasValveFault) = flowAdjust(gasFlow, gasFlowSet, gasFlowAvg3s, gasFlowRange, valveActualGas, valveGivenGas, timeNow)
                print("gasvalveset = ",gasValveSet)
            #空气流量控制
            if timeNow >= timeAirFlow:
                (airValveSet, timeAirFlow, airValveFault) = flowAdjust(airFlow, float(gasFlowSet) * airGasRatio, airFlowAvg3s, airFlowRange, valveActualAir, valveGivenAir, timeNow)



#阀门开度限幅程序
        gasValveSetEnd = valveLimt(gasValveSet, 80, 6)  # 煤气阀位限制
        airValveSetEnd = valveLimt(airValveSet, 80, 6)  # 空气阀位限制


        print("burnMode=", burnMode)
        print("gasFlowSet=", gasFlowSet)
        print("gasValveSetEnd,airValveSetEnd=",gasValveSetEnd, airValveSetEnd)



#以下将数据写入PLC内部

        # 往PLC里面写入数据
        # 写心跳信号程序,如果数据库时间没有问题
        if connectMysqlMain + connectMysql01 == 2:
            if heart1s == False :
                heart1s = True
            elif heart1s == True :
                heart1s = False
        else:
            print("数据库时间差和实际的时间相差8秒")
        print("heart1s:", heart1s)





        print("isauto ===",isAuto)
        #将心跳信号和实际的经过处理的阀位值全部写入PLC内部
        if connectMysqlMain + connectMysql01 == 2:
            if __name__ == "__main__":
                try:
                    siemens = SiemensS7Net(SiemensPLCS.S300, "192.168.0.2")
                    print("haha")
                    if siemens.ConnectServer().IsSuccess == False:
                        print("connect falied")
                    else:
                        if isAuto == 0:
                            siemens.WriteFloat("DB1.136", valveActualGas)  # 煤气阀门开度设定
                            siemens.WriteFloat("DB1.152", valveActualAir)  # 空气阀门开度设定
                            siemens.WriteBool("M152.0", heart1s)           #心跳信号
                        else:
                            # real array read write test
                            siemens.WriteFloat("DB1.136", gasValveSetEnd)    #煤气阀门开度设定
                            siemens.WriteFloat("DB1.152", airValveSetEnd)         #空气阀门开度设定
                            siemens.WriteBool("M152.0", heart1s)

                    siemens.ConnectClose()
                except Exception as e:
                    print("e=", e)
        print("==================================================")
        time1s = timeNow + 1
    time.sleep(0.1)

