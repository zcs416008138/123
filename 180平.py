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
    user='furnace',
    password='furnace',
    database='sinter',
    charset='utf8'
)

#建立连接MYSQL程序,将数据写入数据库
def func(POOL,insertdata, data):
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


#总阀门控制程序  设定值，实际值，3秒平均值，调整步宽，下次时间，当前阀门设定值，计算后阀门设定值,下次时间，加的时间秒数
def valveAuto(set,act,avg,step,presentValve,addtime):
    global timeNow
    valveSet = presentValve
    timeSingle = timeNow

    if set > act:
        #首先读取当前阀门设定值：
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

# 将日期格式转换为时间戳
def timeStampTransfer(data):
    result = []
    for x in data:
        if x!=None:
            time1 = time.mktime(x.timetuple())
            result.append(time1)
    return result

# 将日期格式转换为时间戳
def dateToTimestamp(data):
    time1 = time.mktime(data.timetuple())
    return time1
#把string格式转换为timestamp，
#time3='20200821123423'转换为时间戳 t1= 1653461032.0
def stringDateTimeToTimeStamp(timedata):
    time0 = str(timedata)
    time1 = time0[0:14]
    t1 = time.mktime(time.strptime(time1, '%Y%m%d%H%M%S'))
    #print("t1=", t1)
    return t1

#从kepware读取数据，然后写入mysql，每秒写一次
def readFromKep():
    time0 = 0
    client = Client("opc.tcp://127.0.0.1:49320", timeout=1000)
    client.connect()
    print("chengogng")
    while True:
        timenow = int(time.time())


        if timenow>=time0:
            #handler = SubHandler()
            #获取点位数据
            #调用示例：aa1 = getvalue("ns=2;s=aa.bb.read.a1")
            def getvalue(abc):
                tag0 = client.get_node(abc).get_value()
                return tag0



            #写入点位数据
            #例子：setvalue("ns=2;s=aa.bb.read.a1", "UInt16", 201)
            # #往KEP里面写入数据
            # for x in range(1,11):
            #     setvalue("ns=2;s=aa.bb.write.c"+str(x), "UInt16", x+200)
            def setvalue(bianliang,type0,valueset):
                #bianliang:在KEPWARE里面的变量点名称
                #type0:要往PLC写入的变量的数据类型（类型必须对应，否则无法写入）
                #valueset:要往变量里面写入的值
                tagset = client.get_node(bianliang)
                dv = ua.DataValue(ua.Variant(valueset, ua.VariantType.UInt16))
                tagset.set_value(dv)
                print("tag2", tagset.get_value())


            #读取数据
            try:
                list0 = []
                #获取数据的数量
                for m in range(1,54):
                    value0 = getvalue("ns=2;s=aa.bb.read.a"+str(m))
                    #print("tpye(valu0=",type(value0))
                    list0.append(value0)
                    #print("va1=", value0)




                listFinal = []  #现将list1清空
                #print("list0=",list0)
                listFinal = [float(x) for x in list0]
                #listFinal= list0
                timeID = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S') ) # 含微秒的日期时间，来源 比特量化
                listFinal.insert(0,timeID)
                print("listFinal=",listFinal)
                print("len=",len(listFinal))
                insertdata = """INSERT INTO sinter( timeID,gasPressure,airPressure,gasFlow,airFlow,chamberPressure,tempA,tempB,gasValveActual,gasValveGiven,\
                                                    airValveActual,airValveGiven,tempGiven,mode,airGasRatioGiven,gasFlowGivenMax,gasFlowGivenMin,gasTemp,mainGasPress,smokePress,\
                                                    smokeTemp,exhaustGasTemp1,exhaustGasTemp2,exhaustGasTemp3,sinterTemp,boxPressure1,boxPressure2,boxPressure3,boxPressure5,boxPressure7,\
                                                    boxPressure9,boxPressure11,boxPressure13,boxPressure15,boxPressure17,boxPressure19,boxPressure20,boxPressure21,boxPressure22,boxTemp1,\
                                                    boxTemp2,boxTemp3,boxTemp5,boxTemp7,boxTemp9,boxTemp11,boxTemp13,boxTemp15,boxTemp17,boxTemp19,\
                                                    boxTemp20,boxTemp21,boxTemp22,heart)
                                                    values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                            %s,%s,%s,%s)
                            """
                 #将数据插入数据库
                try:
                    func(POOL,insertdata, listFinal)
                except Exception as e:
                    print("error is :", e)

            except Exception as e:
                print("e=",e)
            time0 = timenow + 1
            time.sleep(0.1)
#往KEPWARE的地址里面写入数据
#def WriteToKep(gasvalve,airvalve,heart):
def WriteToKep( gasvalve,gasFlowSet0):
    client = Client("opc.tcp://127.0.0.1:49320", timeout=1000)
    client.connect()
    print("chengogng")


    try:
        # handler = SubHandler()
        # 获取点位数据
        # 调用示例：aa1 = getvalue("ns=2;s=aa.bb.read.a1")


        def getvalue(abc):
            tag0 = client.get_node(abc).get_value()
            return tag0


        # 写入点位数据
        # 例子：setvalue("ns=2;s=aa.bb.read.a1", "UInt16", 201)
        # #往KEP里面写入数据
        # for x in range(1,11):
        #     setvalue("ns=2;s=aa.bb.write.c"+str(x), "UInt16", x+200)
        def setvalue(bianliang,  valueset):
            # bianliang:在KEPWARE里面的变量点名称
            # type0:要往PLC写入的变量的数据类型（类型必须对应，否则无法写入）
            # valueset:要往变量里面写入的值
            tagset = client.get_node(bianliang)
            dv = ua.DataValue(ua.Variant(valueset, ua.VariantType.Float))
            tagset.set_value(dv)
            print("tag2", tagset.get_value())


        setvalue("ns=2;s=sinter180.analog.autoburn.gasValveGiven",  gasvalve)  # 写入煤气阀门开度值
        #setvalue("ns=2;s=sinter180.analog.autoburn.airValveGiven",  airvalve)  # 写入空气阀门开度值
        #setvalue("ns=2;s=sinter180.analog.autoburn.gasValveGiven",  heart)  # 写入心跳信号
        #setvalue("ns=2;s=sinter180.analog.autoburn.testwritekongranbi", heart)  # 写入心跳信号
        setvalue("ns=2;s=sinter180.analog.autoburn.gasFlowSet", gasFlowSet0)  # 煤气流量设定值


    finally:
    # 断开连接
        client.disconnect()


time1s = 0 #整个程序的循环周期
time10 = 0  #温度控制的快速控制周期
timeGas = 0

#heart0 = 0      #
sqlDataFault = 0   #从数据库里面读取出来的时间戳正常
time1 = 0          #检测炉膛温度的周期


sqlDataFaultList = []   #读取数据信号list
firstscan =0  #初次启动程序
heartSingle =0  #心跳信号
timeheart = 0 #心跳时间信号

gasFlowStand0 = 0
timeyacha = 0


#开始写智能燃烧程序
while True:
    timestart = float(time.time())
    timeNow = int(time.time())
    if timeNow > time1s:

        #此数据的写入是从刘永的JAVA程序写入的数据。
        #从本地数据库读取数据，然后首先校验数据的时间戳和心跳信号，如果有问题，则进行提示，并且停止智能燃烧
        sqlread ="SELECT * FROM sinter.sinterkep order by timeID DESC limit 600"
        dataRead = readMysqlToArry(sqlread,600)
        #print("dataRead", dataRead)

        #将数据赋值
        timeID = dataRead[:, 1]                 #时间戳
        gasFlow = dataRead[:, 7]                #煤气流量
        airFlow = dataRead[:, 2]                #空气流量
        tempA = dataRead[:, 14]                  #炉膛温度A
        tempB = dataRead[:, 15]                  #炉膛温度B
        gasValveActual = dataRead[:, 9]        #煤气阀门实际开度
        gasValveGiven = dataRead[:, 10]         #煤气阀门给定值
        airValveActual = dataRead[:, 5]       #空气阀门实际值
        airValveGiven = dataRead[:, 6]        #空气阀门给定值
        tempGiven = dataRead[:, 16]            #温度给定
        mode = dataRead[:, 13]                 #手动自动模式
        airGasRatioGiven = dataRead[:, 3]     #空燃比给定
        mainGasPress = dataRead[:,12]          #煤气压力




        # print("gasFlow=", gasFlow[0])
        # print("airFlow=", airFlow[0])
        # print("tempA=", tempA[0])
        # print("gasValveActual=", gasValveActual[0])
        # print("gasValveGiven=", gasValveGiven[0])
        # print("airValveActual=", airValveActual[0])
        # print("airValveGiven=", airValveGiven[0])
        # print("tempGiven=", tempGiven[0])
        # print("mode=", mode[0])
        # print("airGasRatioGiven=", airGasRatioGiven[0])
        # print("mainGasPress=", mainGasPress[0])





        #设定温度调节值的上下界范围
        tempRange = 8   #设定温度的第一层温度范围，较小
        tempRange2 = 17   #设定温度的第二层温度范围，较大。
        timeGasFlow = 0
        timeAirFlow = 0

        gasDivideTemp = sum(gasFlow)/sum(tempA)   #求10分钟平均每度需要的煤气流量
        #print("zonghe=",gasDivideTemp*tempGiven[0])
        gasHighLimit = round(float(gasDivideTemp)*1.15 *float(tempGiven[0]) ,2)                  #每度流量的上限
        gasLowLimit = round(float(gasDivideTemp)*0.85 *float(tempGiven[0]),2)                   #梅毒流量的下线
        print("煤气流量上限=",gasHighLimit)
        print("煤气流量下限=", gasLowLimit)
        gasActualAvg3s = sum(gasFlow[0:4])/4   #4秒煤气平均值
        airActualAvg3s = sum(airFlow[0:4])/4    #4秒空气平均值





        print("每个温度对应流量=",gasDivideTemp)


        print("调节前煤气阀门开度实际,空气阀门开度实际=",gasValveActual[0],airValveActual[0])
        print("调节前煤气阀门开度设定,空气阀门开度设定=", gasValveGiven[0], airValveGiven[0])



        #获取当前时间和数据库时间进行做对比，如果时间相差5秒，那么认为网络新数据已经不插入数据库了。那么进行报警
        #timeReadSql = stringDateTimeToTimeStamp(timeID[0])  #数据库读取的最新一笔数据的时间
        timeReadSql = int(time.mktime(timeID[0].timetuple()))
        timecha = timeNow - int(timeReadSql)
        print("timecha=", timecha)
        if timecha >6:
            sqlDataFault = 1

        else:
            sqlDataFault = 0


        #此段保持sqlDataFaultlist的长度，用于后面检测网络断开和连接的趋势
        if len(sqlDataFaultList)<10:
            sqlDataFaultList.insert(0,sqlDataFault)
        if len(sqlDataFaultList)>=10:
            sqlDataFaultList.pop(-1)
        print("sqlDataFaultList=",sqlDataFaultList)

        #如果从SQL数据库读取数据异常，那么就将初始扫描设置为1，这样就可以在数据恢复之后重新扫描初始化数据
        if sqlDataFault == 1:
            firstscan = 0


       #如果数据库数据正常，并且系统已经启动超过5秒，那么开始智能燃烧
        if sqlDataFault == 0 and len(sqlDataFaultList)>5:
            tempCha = tempA[0] - tempA[9]  # 点火温度差值

            pressCha = mainGasPress[0] - mainGasPress[30]     #总管煤气压力差


            if sqlDataFault==0:         #如果从SQL数据库读取出来的数据没有异常
                #初次开启程序扫描，将煤气空气流量设定值设置成当前流量
                if firstscan == 0:
                    gasFlowSet = gasFlow[0]
                    airFlowSet = airFlow[0]
                    gasValveSet = gasValveGiven[0]
                    airValveSet = airValveGiven[0]
                    firstscan = 1


                #如果是手动模式那么将煤气空气流量的给定值设置成实际值。
                if mode[0] == 0:
                    gasFlowSet = gasFlow[0]
                    airFlowSet = airFlow[0]
                    gasValveSet = gasValveGiven[0]
                    airValveSet = airValveGiven[0]


                print("gasFlowSet111111111111111111111111111=",gasFlowSet)
                print("airFlowSet=", airFlowSet)


##########################################################################00000
                print("moshi===================",mode[0])
                #如果是自动模式，并且煤气流量正常是大于10的,那么开始调节
                if mode[0] ==1 and gasFlow[0]>10:
                    print("设定温度=",tempGiven[0])
                    print("实际温度=",tempA[0])

                    print("tempcha===============",tempCha)




                    #如果到了下一个检测温度的时间周期：那么开始检测和执行调整煤气设定值
                    #每30秒检测一个温度周期。
                    if timeNow >= time1:
                        #开始根据温度的差值进行流量调节
                        # 如果在温度范围上线以外，并且3秒温升大于-1，那么减煤气

                        if  tempA[0]>(tempGiven[0] + tempRange) and tempA[0]<(tempGiven[0] + tempRange2) and tempCha >= -1:
                            #gasFlowSet = gasFlow[0] - 300
                            gasFlowSet = gasFlowSet - 100
                            print("实际温度大，煤气量减小100，tempCha>=-1")
                            time1 = timeNow + 30

                        # 如果实际温度小于设定温度，并且设定温度范围外，并且温度比前3秒的值要小于2(就是煤气每3秒升温小于2）那么开始加煤气
                        if tempA[0] < tempGiven[0] - tempRange and tempA[0] > tempGiven[0] - tempRange2 and tempCha <= 1:
                            #gasFlowSet = gasFlow[0] + 300
                            gasFlowSet = gasFlowSet + 100
                            print("实际温度小，煤气量加大100,tempCha<=1")
                            time1 = timeNow + 30

                    #检测压力，将压力也作为复合调节的条件来控制煤气流量
                    if timeNow > timeyacha:
                        print("pressCha = ", pressCha)
                        if pressCha > 0:
                            adgust0 = (pressCha * gasFlowSet) *0.052

                            print("压差值大于0，需要调整",adgust0)
                            timeyacha = timeNow +30
                        if pressCha <0:
                            adgust1 = (pressCha * gasFlowSet) * 0.042
                            print("压差值小于0，需要调整", adgust1)
                            timeyacha = timeNow + 30



                    #每10秒检测一个周期。特殊情况，如果温度超出设定值上下范围40度，那么启动再加一层的快速调节程序
                    if timeNow >= time10:
                        # 开始根据温度的差值进行流量调节
                        # 如果在温度范围上线以外，并且3秒温升大于-1，那么减煤气
                        if tempA[0] > (tempGiven[0] + tempRange2):
                            if tempCha >= 2:
                                gasFlowSet = gasFlowSet - 200
                                print("进入快速周期 实际温度大,温度差大于2，煤气量减小200，tempCha>=2")
                                time10 = timeNow + 10
                            elif tempCha >0:
                                gasFlowSet = gasFlowSet - 120
                                print("进入快速周期 实际温度大，煤气量减小200，tempCha>=-1")
                                time10 = timeNow + 10

                        # 如果实际温度小于设定温度，并且设定温度范围外，并且温度比前3秒的值要小于2(就是煤气每3秒升温小于2）那么开始加煤气
                        elif tempA[0] < tempGiven[0] - tempRange2 :#原来大于1
                            if tempCha <=-2:
                                gasFlowSet = gasFlowSet + 200
                                print("进入快速周期实际温度小，煤气量加大100,tempCha<=2")
                                time10 = timeNow + 10
                            elif tempCha < 0:
                                gasFlowSet = gasFlowSet + 100
                                print("进入快速周期实际温度小，煤气量加大100,tempCha<=-0.5")
                                time10 = timeNow + 10



                    #如果在第一个range的区间内，如果温度的变化tempcha 的值大于等于2.那么就将设定值减少
                        if  tempA[0]<=(tempGiven[0] + tempRange)  and  tempA[0]>=(tempGiven[0] - tempRange):
                            if tempCha >=2:
                                gasFlowSet = gasFlowSet - 120
                                time10 = timeNow + 10
                                print("在一号区间内温度变化率大于等于2，设定流量减少100")
                            elif tempCha <=-2:
                                gasFlowSet = gasFlowSet + 120
                                time10 = timeNow + 10
                                print("在一号区间内温度变化率小于等于-2，设定流量增加100")





                    #此段程序为了限制流量的上下限
                    if gasFlowSet>gasHighLimit:
                        gasFlowSet = gasHighLimit
                        print("煤气流量设定值达到上限")
                    elif gasFlowSet < gasLowLimit:
                        gasFlowSet = gasLowLimit
                        print("煤气流量设定值达到上限")


                    #下段开始调节阀门控制程序。
                    # 根据煤气流量来控制阀门。
                    #if gasFlowSet == gasFlowStand0:




                    #          实际流量  设定流量  差值范围       阀位实际值  阀位当前给定值    当前时间
                    def flowAdjust(gas_F,gasSet, gasAvg3s,  gasFlowRange1,valveActual,gasMainValveGiven,timeNow):
                        timeGas = timeNow
                        valvefault = 0
                        gasValveSet = gasMainValveGiven
                        #防止阀门损坏，然后报警
                        # if abs(gasMainValveGiven - valveActual)>=4:
                        #     gasValveSet = gasMainValveGiven
                        #     valvefault=1  #阀门异常
                        if valveActual>5 and gas_F<500:
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
                        return gasValveSet,timeGas, valvefault



                    #煤气阀门调节程序
                    gasFlowRange = 300
                    #print("煤气流量=", gasFlow[0])
                    print("煤气流量给定=", gasFlowSet)
                    # print("煤气流量范围=", gasFlowRange)
                    # print("煤气阀门给定=", gasValveGiven[0])
                    if timeNow > timeGasFlow:
                        (gasValveSet, timeGasFlow, gasValveFault) = flowAdjust(gasFlow[0], gasFlowSet,gasActualAvg3s, gasFlowRange, gasValveActual[0],gasValveGiven[0], timeNow)

                    aifFlowRange = 500

                    # print("空气流量=",airFlow[0])
                    print("空气流量给定=",float(gasFlowSet)*float(airGasRatioGiven[0]))
                    # print("空气流量范围=",aifFlowRange)
                    # print("空气阀门给定=",airValveGiven[0] )
                    #空气阀门调节程序
                    # if timeNow > timeAirFlow:
                    #     (airValveSet, timeAirFlow, airValveFault) =flowAdjust(airFlow[0], float(gasFlowSet)*float(airGasRatioGiven[0]),airActualAvg3s,aifFlowRange, airValveActual[0], airValveGiven[0], timeNow)


                    #心跳程序
                    #如果从数据库里面读取数据正常,空气阀正常     煤气阀正常
                    if sqlDataFault == 0  and   gasValveFault!=1 and timeNow != timeheart:  #airValveFault!=1 and
                        print("kkkkkkkkkkkk")
                        if heartSingle == 0:
                            heartSingle = 1
                        else:
                            heartSingle = 0
                        timeheart = timeNow + 1


                    #阀门开度限制程序
                    def valveLimt(valveset,high,low):
                        valve = valveset
                        if valveset>=high:
                            valve = high
                        elif valveset<= low:
                            valve = low
                        return valve




                    #阀位限制：
                    gasValveSetEnd = valveLimt(gasValveSet,80,10)   #煤气阀位限制
                   # airValveSetEnd = valveLimt(airValveSet,80,10)   #空气阀位限制



                    print("煤气流量设定值gasFlowSet=",gasFlowSet)
                    #print("需要写入的信号_煤气阀位给定，空气阀位给定，心跳信号=",gasValveSetEnd,airValveSetEnd,heartSingle)
                    print("需要写入的信号_煤气阀位给定，，心跳信号=", gasValveSetEnd,  heartSingle)

                    print("空气/煤气阀门/sql异常=",gasValveFault,sqlDataFault)
                    # print("煤气阀门异常=", gasValveFault)
                    # print("sql异常=", sqlDataFault)

                    #WriteToKep(gasValveSetEnd,airValveSetEnd)
                    WriteToKep(gasValveSetEnd, gasFlowSet)
                    print("总用时间==========================================",float(time.time())-timestart)
        time1s = timeNow + 1
    time.sleep(0.1)




















