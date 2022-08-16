# coding:utf-8 用内存作为默认的作业存储器
 #此程序是用于棒材的智能燃烧程序
import datetime
import sys
sys.path.insert(0, "..")
from opcua import Client,ua
import time
from HslCommunication import SiemensS7Net
from HslCommunication import SiemensPLCS
import numpy as np
import pymysql
from DBUtils.PooledDB import PooledDB


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
    host='127.0.0.1',
    port=3306,
    user='furnace',
    password='furnace',
    database='barroll',
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


# 总阀压力控制      #设定压力    实际压力 ， 给定阀门开度，实际阀门开度，平均压力， 时间跨度
def mainValveControl(presureSet, actPresure, valveGiven, valveAct, avg1, addtime1):
    global timeNow
    valve1 = valveGiven
    mainVTime = timeNow
    print("进入总阀控制程序")
    # 首先判断目前的阀位的给定和反馈是否相差几个，如果差值大于3，那么停止新的给定。
    if abs(valveGiven - valveAct) > 3:
        valve1 = valveGiven
        mainVTime = timeNow
        print("总阀给定和实际差3个以上，停止调节阀门")
    # 如果阀门开着，但是煤气没有压力或者压力反馈不正常，那么不再调节。
    elif valveGiven > 10 and actPresure < 3:
        valve1 = valveGiven
        mainVTime = timeNow
        print("总阀压力不正常，停止调节阀门")
    else:
        print("正常调节总阀")
        if presureSet > actPresure:
            print("设定大于实际压力")
            if presureSet - actPresure >= 1 and presureSet - avg1 >= 0.9:
                valve1 = valveGiven + 3
                mainVTime = mainValveTime(addtime1)
                print("总阀开3个")
            elif presureSet - actPresure >= 0.55 and presureSet - avg1 >= 0.5:
                valve1 = valveGiven + 2
                mainVTime = mainValveTime(addtime1)
                print("总阀开2个")
            elif presureSet - actPresure >= 0.2 and presureSet - avg1 >= 0.2:
                valve1 = valveGiven + 1
                mainVTime = mainValveTime(addtime1)
        elif presureSet < actPresure:
            print("设定小于实际压力")
            if actPresure - presureSet >= 1.2 and avg1 - presureSet >= 1:
                valve1 = valveGiven - 3
                mainVTime = mainValveTime(addtime1)
                print("总阀关3个")
            elif actPresure - presureSet >= 0.8 and avg1 - presureSet >= 0.8:
                valve1 = valveGiven - 2
                mainVTime = mainValveTime(addtime1)
                print("总阀关2个")
            elif actPresure - presureSet >= 0.4 and avg1 - presureSet >= 0.4:
                valve1 = valveGiven - 1
                mainVTime = mainValveTime(addtime1)
                print("总阀关1个")
    return valve1, mainVTime




#阀门控制程序： 流量设定值，流量实际值，流量3秒平均值，调整步宽，当前阀门开度给定值，加的时间秒数
def valveAuto(set,act,avg,step,presentValve,addtime):
    global timeNow
    valveSet = presentValve
    timeSingle = timeNow
    #####如果阀门的开度是大于5的，但是实际值是0，那么就保持当前阀门开度不动。
    #如果实际阀门开度大于5，但是实际的流量却小于10（也就是流量不正常）那么这次就不进行调节，还是按照原来的阀门给定给出去。
    #流量异常不调节
    if presentValve > 7 and act < 1000:
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


def datetimeToTimeStamp(datetime0):
    timeReadSql = int(time.mktime(datetime0.timetuple()))
    return timeReadSql


# 读取出来的数据求3秒的平均值
def avgCaulate(data0):
    datareturn = (data0[0] + data0[1] + data0[2]) / 3
    return datareturn



#往KEPWARE的地址里面写入数据

#def WriteToKep(gasvalve,airvalve,heart):
def WriteToKep(setdata):
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
            #print("tag2", tagset.get_value())
        def setBOOLvalue(bianliang,  valueset):
            # bianliang:在KEPWARE里面的变量点名称
            # type0:要往PLC写入的变量的数据类型（类型必须对应，否则无法写入）
            # valueset:要往变量里面写入的值
            tagset = client.get_node(bianliang)
            dv = ua.DataValue(ua.Variant(valueset, ua.VariantType.Boolean))
            tagset.set_value(dv)
            #print("tag2", tagset.get_value())




        setvalue("ns=2;s=furnace.furnace1.autoburnset.junreAirValveSet", setdata[0])  # 均热段空气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.junreGasValveSet", setdata[1])  # 均热段煤气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.junreAirSmokValveSet", setdata[2])  # 均热段空烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.junreGasSmokValveSet", setdata[3])  # 均热段煤烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.jiareAirValveSet", setdata[4])  # 加热段空气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.jiareGasValveSet", setdata[5])  # 加热段煤气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.jiareAirSmokValveSet", setdata[6])  # 加热段空烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.jiareGasSmokValveSet", setdata[7])  # 加热段煤烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.yureAirValveSet", setdata[8])  # 预热段空气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.yureGasValveSet", setdata[9])  # 预热段煤气总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.yureAirSmokValveSet", setdata[10])  # 预热段空烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.yureGasSmokValveSet", setdata[11])  # 预热段煤烟总阀开度设定
        setvalue("ns=2;s=furnace.furnace1.autoburnset.mainGasValveSet", setdata[12])  # 煤气总管阀门开度设定
        setBOOLvalue("ns=2;s=furnace.furnace1.autoburnset.heartSingle", setdata[13])  # 自动烧火以太网通讯检测心跳信号

    finally:
    # 断开连接
        client.disconnect()


time1s = 0   #总的按照一秒一扫描
time1gas = 0
time1air = 0
time2gas = 0
time2air = 0
time3gas = 0
time3air = 0
timeyure = 0
timejiare = 0
timejunre = 0
timeMainValve = 0
firstScan = 0
firstScanTemp = 0
timePaiyanControl = 0
timePaiyan = 0



#阀门控制程序用的
#预热段
yureAirTempMax = []
yureAirTempMin = []
yureAirTempAvg = []

yureGasTempMax = []
yureGasTempMin = []
yureGasTempAvg = []

#加热段
jiareAirTempMax = []
jiareAirTempMin = []
jiareAirTempAvg = []

jiareGasTempMax = []
jiareGasTempMin = []
jiareGasTempAvg = []

#均热段
junreAirTempMax = []
junreAirTempMin = []
junreAirTempAvg = []

junreGasTempMax = []
junreGasTempMin = []
junreGasTempAvg = []




while True:
    log = open('fullbarline.txt', 'a')
    time001 = float(time.time())
    timeNow = int(time.time())
    #timeID0 = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 日期时间，来源 比特量化
    if timeNow >= time1s:
        try:
            print("timeNow=",timeNow)
            timetest1 = time.time()
            #将加热炉数据从本地数据库读取出来。
            sql = "SELECT * FROM barroll.autoburn order by timeID desc limit 120;"
            arr = readMysqlToArry(sql, 120)    #读取本地数据库函数。
            timetest2 = time.time()
            print("执行时间：",timetest2 - timetest1)
            #print("arr222=",arr[0:10])

            #将最新数据转换为数组。
            listNow1 = list(arr[0])
            print("lisntno9=",listNow1)

            #print("lsitnow1=", arr[0])

            #listAvg = list((arr[0][2:] + arr[1][2:] + arr[2][2:])/3)     #求最近3笔数据的平均值
            #读取数据库的timeID信息，如果和当前timeID差8秒以上，则报错数据库读取失败,将connectMysql置1
            timeFrmSql0 = datetimeToTimeStamp(listNow1[1])
            print("timeFrmSql0:", timeFrmSql0)
            print("timeNow:    ", timeNow)
            #判断数据库是否连接中断
            if timeFrmSql0 < timeNow - 8:
                print("数据库连接中断")
                connectMysql = 0
            else:
                connectMysql = 1


            #读取出来的数据进行处理
            tempYure = listNow1[111]  # 前段炉顶温度（预热段）
            tempJiare = listNow1[39]  # 中段炉顶温度（加热段）
            tempJunre = listNow1[73]  # 后段炉顶温度（均热段）
            gasPressure = listNow1[13]  # 煤气总管压力
            flowZoneAirYure = listNow1[107]  # 前段空气流量（预热段）
            flowZoneAirJiare = listNow1[35]  # 中段空气流量（加热段）
            flowZoneAirJunre = listNow1[69]  # 后段空气流量（均热段）
            valveActualAirYure = listNow1[113]  # 前段空气调节阀反馈（预热段）
            valveActualGasYure = listNow1[90]  # 前段煤气调节阀反馈（预热段）
            valveActualAirSmokeYure = listNow1[114]  # 前段空烟调节阀反馈（预热段）
            valveActualGasSmokeYure = listNow1[115]  # 前段煤烟调节阀反馈（预热段）
            valveActualAirJiare = listNow1[41]  # 中段空气调节阀反馈（加热段）
            valveActualGasJiare = listNow1[136]  # 中段煤气调节阀反馈（加热段）
            valveActualAirSmokeJiare = listNow1[42]  # 中段空烟调节阀反馈（加热段）
            valveActualGasSmokeJiare = listNow1[43]  # 中段煤烟调节阀反馈（加热段）
            valveActualAirJunre = listNow1[75]  # 后段空气调节阀反馈((均热段）
            valveActualGasJunre = listNow1[137]  # 后段煤气调节阀反馈（均热段）
            valveActualAirSmokeJunre = listNow1[76]  # 后段空烟调节阀反馈（均热段）
            valveActualGasSmokeJunre = listNow1[77]  # 后段煤烟调节阀反馈（均热段）
            gasPressValveActual = listNow1[12]  # 总管煤气调节阀反馈
            gasCompensationFlowYure = listNow1[108]  # 前煤气补偿后流量
            gasCompensationFlowJiare = listNow1[36]  # 中煤气补偿后流量
            gasCompensationFlowJunre = listNow1[70]  # 后端煤气补偿后流量
            #print("gasCompensationFlowYure=",gasCompensationFlowYure)
            gasPressValveGiven = listNow1[135]  # 煤气总管阀门开度设定
            valveGivenGasYure = listNow1[134]  # 预煤调节阀门开度（预热段）设定
            valveGivenAirYure = listNow1[133]  # 预空调节阀门开度（预热段）设定
            valveGivenGasJiare = listNow1[132]  # 加煤调节阀门开度（加热段）设定
            valveGivenAirJiare = listNow1[131]  # 加空调节阀门开度（加热段）设定
            valveGivenGasJunre = listNow1[130]  # 均煤调节阀门开度（均热段）设定
            valveGivenAirJunre = listNow1[129]  # 均空调节阀门开度（均热段）设定

            valveGivenGasSmokeYure = listNow1[138]  # 预煤烟调节阀门开度（预热段）设定
            valveGivenAirSmokeYure = listNow1[141]  # 预空烟调节阀门开度（预热段）设定
            valveGivenGasSmokeJiare = listNow1[139]  # 加煤烟调节阀门开度（加热段）设定
            valveGivenAirSmokeJiare = listNow1[142]  # 加空烟调节阀门开度（加热段）设定
            valveGivenGasSmokeJunre = listNow1[140]  # 均煤烟调节阀门开度（均热段）设定
            valveGivenAirSmokeJunre = listNow1[143]  # 均空烟调节阀门开度（均热段）设定

           # print("kongqilist=",listNow1[138:144])
            mainValvePresureSet = listNow1[18]  # 煤气总管压力给定
            gasGiverYureSet = listNow1[110]  # 预热段煤气留量给定
            print("gasGiverYureSet=",gasGiverYureSet)
            airGasRatioYure = listNow1[92]  # 预热段空煤比给定
            #TempGivenYure = listNow1[99]  # 预热段温度给定1111111111111111111111111111111111
            gasGiverJiareSet = listNow1[38]  # 加热段煤气留恋给定
            airGasRatioJiare = listNow1[20]  # 加热段空煤比给定
            #TempGivenJiare = listNow1[102]  # 加热段温度给定2222222222222222222222222222222222
            gasGiverJunreSet = listNow1[72]  # 均热段煤气流量给定
            airGasRatioJunre = listNow1[56]  # 均热段空煤比给定
            #TempGivenJunre = listNow1[105]  # 均热段温度给定33333333333333333333333333333333
            furnaceAutoManual = listNow1[9]  # 炉体手动自动温度切换
            mainValveAutoHand = listNow1[128]  # 总阀手自动切换



            airMainTem1 = listNow1[2]  # 1#助燃风机温度检测A
            airMainTem2 = listNow1[3]  # 1#助燃风机温度检测B
            airPressure = listNow1[4]  # 空气总管压力检测
            airSmokeEntryPressure = listNow1[5]  # 空烟入口压力检测
            airSmokeFanTemA = listNow1[6]  # 空烟风机温度检测A
            airSmokeFanTemB = listNow1[7]  # 空烟风机温度检测B
            airSmokeMainTem = listNow1[8]  # 空烟总管温度检测
            furnacePressure = listNow1[10]  # 炉膛压力检测
            gasMainTem = listNow1[11]  # 高炉煤气温度检测
            gasSmokeEntryPressure = listNow1[14]  # 煤烟入口压力检测
            gasSmokeFanTemA = listNow1[15]  # 煤烟风机温度检测A
            gasSmokeFanTemB = listNow1[16]  # 煤烟风机温度检测B
            gasSmokeMainTem = listNow1[17]  # 煤烟总管温度检测
            jiareairSmokeMainZoneTem = listNow1[19]  # 加热段空烟总管温度检测
            jiaredownTemp = listNow1[21]  # 加热段下部炉温检测
            jiaredownTempD = listNow1[22]  # 预热热段下部炉温检测D
            jiareeastAirSmokeTem1 = listNow1[23]  # 加热段东1号空烟温度
            jiareeastAirSmokeTem2 = listNow1[24]  # 加热段东2号空烟温度
            jiareeastAirSmokeTem3 = listNow1[25]  # 加热段东3号空烟温度
            jiareeastAirSmokeTem4 = listNow1[26]  # 加热段东4号空烟温度
            jiareeastAirSmokeTem5 = listNow1[27]  # 加热段东5号空烟温度
            jiareeastAirSmokeTem6 = listNow1[28]  # 加热段东6号空烟温度
            jiareeastGasSmokeTem1 = listNow1[29]  # 加热段东1号煤烟温度
            jiareeastGasSmokeTem2 = listNow1[30]  # 加热段东2号煤烟温度
            jiareeastGasSmokeTem3 = listNow1[31]  # 加热段东3号煤烟温度
            jiareeastGasSmokeTem4 = listNow1[32]  # 加热段东4号煤烟温度
            jiareeastGasSmokeTem5 = listNow1[33]  # 加热段东5号煤烟温度
            jiareeastGasSmokeTem6 = listNow1[34]  # 加热段东6号煤烟温度
            jiaregasSmokeMainZoneTem = listNow1[37]  # 加热段煤烟总管温度检测
            jiareupTempB = listNow1[40]  # 均热段上部炉温检测B
            jiarewestAirSmokeTem1 = listNow1[44]  # 加热段西1号空烟温度
            jiarewestAirSmokeTem2 = listNow1[45]  # 加热段西2号空烟温度
            jiarewestAirSmokeTem3 = listNow1[46]  # 加热段西3号空烟温度
            jiarewestAirSmokeTem4 = listNow1[47]  # 加热段西4号空烟温度
            jiarewestAirSmokeTem5 = listNow1[48]  # 加热段西5号空烟温度
            jiarewestAirSmokeTem6 = listNow1[49]  # 加热段西6号空烟温度
            jiarewestGasSmokeTem1 = listNow1[50]  # 加热段西1号煤烟温度
            jiarewestGasSmokeTem2 = listNow1[51]  # 加热段西2号煤烟温度
            jiarewestGasSmokeTem3 = listNow1[52]  # 加热段西3号煤烟温度
            jiarewestGasSmokeTem4 = listNow1[53]  # 加热段西4号煤烟温度
            jiarewestGasSmokeTem5 = listNow1[54]  # 加热段西5号煤烟温度
            junreairSmokeMainZoneTem = listNow1[55]  # 均热段空烟总管温度检测
            junredownTemp = listNow1[57]  # 均热段下部炉温检测
            junredownTempD = listNow1[58]  # 均热段下部炉温检测D
            junreeastAirSmokeTem1 = listNow1[59]  # 均热段东1号空烟温度
            junreeastAirSmokeTem2 = listNow1[60]  # 均热段东2号空烟温度
            junreeastAirSmokeTem3 = listNow1[61]  # 均热段东3号空烟温度
            junreeastAirSmokeTem4 = listNow1[62]  # 均热段东4号空烟温度
            junreeastAirSmokeTem5 = listNow1[63]  # 均热段东5号空烟温度
            junreeastGasSmokeTem1 = listNow1[64]  # 均热段东1号煤烟温度
            junreeastGasSmokeTem2 = listNow1[65]  # 均热段东2号煤烟温度
            junreeastGasSmokeTem3 = listNow1[66]  # 均热段东3号煤烟温度
            junreeastGasSmokeTem4 = listNow1[67]  # 均热段东4号煤烟温度
            junreeastGasSmokeTem5 = listNow1[68]  # 均热段东5号煤烟温度
            junregasSmokeMainZoneTem = listNow1[71]  # 均热段煤烟总管温度检测
            junreupTempB = listNow1[74]  # 加热段上部炉温检测B
            junrewestAirSmokeTem1 = listNow1[78]  # 均热段西1号空烟温度
            junrewestAirSmokeTem2 = listNow1[79]  # 均热段西2号空烟温度
            junrewestAirSmokeTem3 = listNow1[80]  # 均热段西3号空烟温度
            junrewestAirSmokeTem4 = listNow1[81]  # 均热段西4号空烟温度
            junrewestAirSmokeTem5 = listNow1[82]  # 均热段西5号空烟温度
            junrewestGasSmokeTem1 = listNow1[83]  # 加热段西1号煤烟温度
            junrewestGasSmokeTem2 = listNow1[84]  # 加热段西2号煤烟温度
            junrewestGasSmokeTem3 = listNow1[85]  # 加热段西3号煤烟温度
            junrewestGasSmokeTem4 = listNow1[86]  # 加热段西4号煤烟温度
            junrewestGasSmokeTem5 = listNow1[87]  # 加热段西5号煤烟温度
            junrewestGasSmokeTem6 = listNow1[88]  # 加热段西6号煤烟温度
            nitPressure = listNow1[89]  # 氮气压力检测
            yureairSmokeMainZoneTem = listNow1[91]  # 预热段空烟总管温度检测
            yuredownTemp = listNow1[93]  # 预热段下部炉温检测
            yuredownTempD = listNow1[94]  # 加热段下部炉温检测D
            yureeastAirSmokeTem1 = listNow1[95]  # 预热段东1号空烟温度
            yureeastAirSmokeTem2 = listNow1[96]  # 预热段东2号空烟温度
            yureeastAirSmokeTem3 = listNow1[97]  # 预热段东3号空烟温度
            yureeastAirSmokeTem4 = listNow1[98]  # 预热段东4号空烟温度
            yureeastAirSmokeTem5 = listNow1[99]  # 预热段东5号空烟温度
            yureeastAirSmokeTem6 = listNow1[100]  # 预热段东6号空烟温度
            yureeastGasSmokeTem1 = listNow1[101]  # 预热段东1号煤烟温度
            yureeastGasSmokeTem2 = listNow1[102]  # 预热段东2号煤烟温度
            yureeastGasSmokeTem3 = listNow1[103]  # 预热段东3号煤烟温度
            yureeastGasSmokeTem4 = listNow1[104]  # 预热段东4号煤烟温度
            yureeastGasSmokeTem5 = listNow1[105]  # 预热段东5号煤烟温度
            yureeastGasSmokeTem6 = listNow1[106]  # 预热段东6号煤烟温度
            yuregasSmokeMainZoneTem = listNow1[109]  # 预热段煤烟总管温度检测
            yureupTempB = listNow1[112]  # 预热段上部炉温检测B
            yurewestAirSmokeTem1 = listNow1[116]  # 预热段西1号空烟温度
            yurewestAirSmokeTem2 = listNow1[117]  # 预热段西2号空烟温度
            yurewestAirSmokeTem3 = listNow1[118]  # 预热段西3号空烟温度
            yurewestAirSmokeTem4 = listNow1[119]  # 预热段西4号空烟温度
            yurewestAirSmokeTem5 = listNow1[120]  # 预热段西5号空烟温度
            yurewestAirSmokeTem6 = listNow1[121]  # 预热段西6号空烟温度
            yurewestGasSmokeTem1 = listNow1[122]  # 预热段西1号煤烟温度
            yurewestGasSmokeTem2 = listNow1[123]  # 预热段西2号煤烟温度
            yurewestGasSmokeTem3 = listNow1[124]  # 预热段西3号煤烟温度
            yurewestGasSmokeTem4 = listNow1[125]  # 预热段西4号煤烟温度
            yurewestGasSmokeTem5 = listNow1[126]  # 预热段西5号煤烟温度
            yurewestGasSmokeTem6 = listNow1[127]  # 预热段西6号煤烟温度

            yureHXLeftTime = listNow1[144]  # 预热段换向剩余时间


            yureAirSmokeTempList = listNow1[95:101] + listNow1[116:122]     #预热段空烟温度
            yureGasSmokeTempList = listNow1[101:107] + listNow1[122:128]    #预热段煤烟温度

            jiareAirSmokeTempList = listNow1[23:29] + listNow1[44:50]      # 加热段空烟温度
            jiareGasSmokeTempList = listNow1[29:35] + listNow1[50:55]      # 加热段煤烟温度

            junreAirSmokeTempList = listNow1[64:69] + listNow1[78:83]      # 均热段空烟温度
            junreGasSmokeTempList = listNow1[64:69] + listNow1[83:89]      # 均热段煤烟温度

            # yureEastlistTemp = listNow1[95:107]     #预热段东侧的温度list
            # yureWestlistTemp = listNow1[116:128]    #预热段西侧的温度list
            # jiareEastlistTemp = listNow1[23:35]     #加热段东侧的温度list
            # jiareWestlistTemp = listNow1[44:55]     #加热段西侧的温度list
            # junreEastlistTemp =  listNow1[59:69]    #均热段东侧的温度list
            # junreWestlistTemp = listNow1[78:89]     #均热段西侧的温度list



            #以下是求取平均值
            # print("avgflowZoneAirJiare=",arr[:,13])
            avggasPressure = avgCaulate(arr[:, 13])  # 高炉煤气压力平均值
            avgflowZoneAirJiare = avgCaulate(arr[:, 35])  # 加热段空气流量平均值
            avggasCompensationFlowJiare = avgCaulate(arr[:, 36])  # 加热段煤气流量检测平均
            avgflowZoneAirJunre = avgCaulate(arr[:, 69])  # 均热段空气流量检测平均
            avggasCompensationFlowJunre = avgCaulate(arr[:, 70])  # 均热段煤气流量检测平均值
            avgflowZoneAirYure = avgCaulate(arr[:, 107])  # 预热段空气流量检测平均
            avggasCompensationFlowYure = avgCaulate(arr[:, 108])  # 预热段煤气流量检测平均

            print("预热段,煤气流量，空气流量，煤气阀门给定，空气阀门给定", gasCompensationFlowYure,flowZoneAirYure,valveGivenGasYure,valveGivenAirYure)
            print("加热段,煤气流量，空气流量，煤气阀门给定，空气阀门给定", gasCompensationFlowJiare, flowZoneAirJiare, valveGivenGasJiare,valveGivenAirJiare)
            print("均热段,煤气流量，空气流量，煤气阀门给定，空气阀门给定,", gasCompensationFlowJunre, flowZoneAirJunre, valveGivenGasJunre,valveGivenAirJunre)
            print("mainvalue=", timeMainValve)





    #初次扫描，数据进行赋值
            if firstScan == 0:
                mainValveSet = gasPressValveGiven
                yuregasValveSet = valveGivenGasYure
                yureAirValveSet = valveGivenAirYure
                jiareGasValveSet = valveGivenGasJiare
                jiareAirValveSet = valveGivenAirJiare
                junreGasValveSet = valveGivenGasJunre
                junreAirValveSet = valveGivenAirJunre
                gasGiverYure = gasGiverYureSet
                gasGiverJiare = gasGiverJiareSet
                gasGiverJunre = gasGiverJunreSet
                firstScan = 1

            print("timeNow,main,time1gas,time1air,time2gas,time2air,time3gas,time3air:", timeNow, timeMainValve, time1gas, time1air, time2gas, time2air, time3gas, time3air)

    #温度和流量模式切换程序
            #如果是流量模式将画面设定值给给定
            if furnaceAutoManual == b'\x01':
                print("开始启用流量模式==")
                gasGiverYure = gasGiverYureSet
                gasGiverJiare = gasGiverJiareSet
                gasGiverJunre = gasGiverJunreSet
            #如果是温度模式，将当前流量值赋值给给定流量
            elif furnaceAutoManual == 2:
                if firstScanTemp == 0:
                    gasGiverYure = gasCompensationFlowYure
                    gasGiverJiare = gasCompensationFlowJiare
                    gasGiverJunre = gasCompensationFlowJunre
                    firstScanTemp = 1

                # #预热段温度控制
                # if timeNow > timeyure:
                #     gasGiverYure,timeyure = tempAdjust(tempYure, TempGivenYure, 5, gasGiverYure, 1500, 60)
                #
                # #加热段温度控制
                # if timeNow > timejiare:
                #     gasGiverjiare, timejiare = tempAdjust(tempJiare, TempGivenJiare, 5, gasGiverjiare, 1500, 60)
                #
                # #均热段温度控制
                # if timeNow > timejunre:
                #     gasGiverjunre, timejunre = tempAdjust(tempJunre, TempGivenJunre, 5, gasGiverjunre, 600, 60)

            print("gasGiverYure1=", gasGiverYure)
            #如果数据库正常更新，那么就进行计算
            print("connectMysql=", connectMysql)
            if connectMysql == 1:

                # 阀门控制程序： 流量设定值，流量实际值，流量3秒平均值，调整步宽，当前阀门开度给定值，加的时间秒数
                def valveAuto(set, act, avg, step, presentValve, addtime):
                    global timeNow
                    valveSet = presentValve
                    timeSingle = timeNow
                    #####如果阀门的开度是大于5的，但是实际值是0，那么就保持当前阀门开度不动。
                    # 如果实际阀门开度大于5，但是实际的流量却小于10（也就是流量不正常）那么这次就不进行调节，还是按照原来的阀门给定给出去。
                    # 流量异常不调节
                    if presentValve > 7 and act < 2000:
                        # 首先读取当前阀门阀位设定值：
                        valveSet = presentValve
                        timeSingle = mainValveTime(addtime)
                    else:
                        if set > act:
                            # 首先读取当前阀门阀位设定值：
                            valveSet = presentValve
                            # 设定压力如果大于实际压力将阀门开度加大。
                            if (set - act > step) and (set - avg > 0.9 * step):
                                valveSet = presentValve + 2
                                timeSingle = mainValveTime(addtime)
                            elif (set - act > 0.5 * step) and (set - avg > 0.45 * step):
                                valveSet = presentValve + 1
                                timeSingle = mainValveTime(addtime)
                            # 设定压力小于实际压力将阀门开度减小
                        elif set < act:
                            if (act - set > step) and (avg - set > 0.9 * step):
                                valveSet = presentValve - 2
                                timeSingle = mainValveTime(addtime)
                            elif (act - set > 0.5 * step) and (avg - set > 0.45 * step):
                                valveSet = presentValve - 1
                                timeSingle = mainValveTime(addtime)
                    return valveSet, timeSingle



        #总管阀门控制
                if timeNow >= timeMainValve and yureHXLeftTime> 0 and yureHXLeftTime< 35 :
                    #(mainValveSet, timeMainValve) = valveAuto(mainValvePresureSet, gasPressure, avggasPressure, 2, gasPressValveGiven, 8)
                    (mainValveSet, timeMainValve) = mainValveControl(mainValvePresureSet, gasPressure, gasPressValveGiven, gasPressValveActual, avggasPressure,5)
                    print("总阀控制参数：总管压力设定，总管实际压力，阀门开度给定值，阀门开度实际值，压力平均值，时间，总管阀门开度设定", mainValvePresureSet, gasPressure, gasPressValveGiven, gasPressValveActual, avggasPressure, timeMainValve, mainValveSet)
                #预热段煤气阀门控制
                if timeNow >= time1gas:
                    print("gasGiverYure2=", gasGiverYure)
                    (yuregasValveSet,time1gas) = valveAuto(gasGiverYure, gasCompensationFlowYure, avggasCompensationFlowYure, 1000, valveGivenGasYure, 6)
                    #print("预热段煤气参数：煤气给定，实际煤气流量，阀门实际开度,阀门设定值,time1gas,预热煤气阀门开度设定", gasGiverYure, gasCompensationFlowYure,valveGivenGasYure,yuregasValveSet,time1gas,yuregasValveSet)
                #预热段空气阀门控制
                if timeNow >= time1air:
                    (yureAirValveSet,time1air) = valveAuto(gasGiverYure*airGasRatioYure, flowZoneAirYure, avgflowZoneAirYure, 1000, valveGivenAirYure, 6)
                    #print("预热段空气参数：空气流量给定，实际空气流量，阀门实际开度,阀门设定值,预热空气阀门开度设定", gasGiverYure*airGasRatioYure, flowZoneAirYure, valveGivenAirYure, yureAirValveSet, time1air,yureAirValveSet)


                if timeNow >= time2gas:
                # 加热段煤气阀门控制
                    (jiareGasValveSet, time2gas) = valveAuto(gasGiverJiare, gasCompensationFlowJiare,avggasCompensationFlowJiare, 1000, valveGivenGasJiare, 6)
                    #print("加热段煤气参数：煤气给定，实际煤气流量，阀门实际开度,阀门设定值,时间，计算结果阀门设定值", gasGiverJiare, gasCompensationFlowJiare, valveGivenGasJiare,
                    #  jiareGasValveSet,time2gas,jiareGasValveSet)
                #加热段空气阀门控制
                if timeNow >=time2air:
                    (jiareAirValveSet, time2air) = valveAuto(gasGiverJiare*airGasRatioJiare, flowZoneAirJiare, avgflowZoneAirJiare, 1000, valveGivenAirJiare, 6)
                    #print("加热段空气参数：空气流量给定，实际空气流量，阀门实际开度,阀门设定值,时间，计算结果阀门设定值", gasGiverJiare*airGasRatioJiare, flowZoneAirJiare, valveGivenAirJiare,
                    #  jiareAirValveSet,time2air,jiareAirValveSet)


                #均热煤气阀门控制
                if timeNow >= time3gas:
                    (junreGasValveSet, time3gas) = valveAuto(gasGiverJunre, gasCompensationFlowJunre, avggasCompensationFlowJunre, 1000, valveGivenGasJunre, 6)
                    # print("均热段煤气参数：煤气给定，实际煤气流量，阀门实际开度,阀门设定值，时间，计算结果设定值", gasGiverJunre, gasCompensationFlowJunre, valveGivenGasJunre,
                    #       junreGasValveSet, time3gas,junreGasValveSet)
                #均热锻空气阀门控制
                if timeNow >= time3air:
                    (junreAirValveSet, time3air) = valveAuto(gasGiverJunre * airGasRatioJunre, flowZoneAirJunre, avgflowZoneAirJunre, 1000, valveGivenAirJunre, 6)
                    # print("均热段空气参数：空气流量给定，实际空气流量，阀门实际开度,阀门设定值，时间，计算结果设定值", gasGiverJunre * airGasRatioJunre, flowZoneAirJunre,
                    #       valveGivenAirJunre, junreAirValveSet, time3air, junreAirValveSet)
                valveset = [mainValveSet, yuregasValveSet, yureAirValveSet, jiareGasValveSet, jiareAirValveSet, junreGasValveSet, junreAirValveSet]
                # print("当前开度：  总，1gas,1air,2gas,2air,3gas,3air=", listNow1[83:90])
                # print("修改后流量，总，1gas,1air,2gas,2air,3gas,3air=", valveset)



        #以下是排烟阀控制程序
                if timeNow >= timePaiyan:
                    #首先初始化数据，计算上一个120秒各个排烟阀的温度最大值最小值
                    yureAirSmokeTempList = listNow1[95:101] + listNow1[116:122]  # 预热段空烟温度
                    yureGasSmokeTempList = listNow1[101:107] + listNow1[122:128]  # 预热段煤烟温度

                    jiareAirSmokeTempList = listNow1[23:29] + listNow1[44:50]  # 加热段空烟温度
                    jiareGasSmokeTempList = listNow1[29:35] + listNow1[50:55]  # 加热段煤烟温度

                    junreAirSmokeTempList = listNow1[64:69] + listNow1[78:83]  # 均热段空烟温度
                    junreGasSmokeTempList = listNow1[64:69] + listNow1[83:89]  # 均热段煤烟温度

                    # print("yureAirSmokeTempList=", max(yureAirSmokeTempList), len(yureAirSmokeTempList))
                    # print("yureAirSmokeTempList=", yureAirSmokeTempList, len(yureAirSmokeTempList))




            #阀门开度限制：
            mainValveSet1 = maxminvalve(mainValveSet, 95, 8)
            yuregasValveSet1 =  maxminvalve(yuregasValveSet, 90, 8)
            yureAirValveSet1 =  maxminvalve(yureAirValveSet, 90, 8)
            jiareGasValveSet1 =  maxminvalve(jiareGasValveSet, 90, 8)
            jiareAirValveSet1 =  maxminvalve(jiareAirValveSet, 90, 8)
            junreGasValveSet1 =  maxminvalve(junreGasValveSet, 90, 5)
            junreAirValveSet1 = maxminvalve(junreAirValveSet, 90, 8)
            yureMeiYanVset = valveGivenGasSmokeYure
            yureKongYanVset = valveGivenAirSmokeYure
            jiareMeiYanVset = valveGivenGasSmokeJiare
            jiareKongYanVset = valveGivenAirSmokeJiare
            junreMeiYanVset = valveGivenGasSmokeJunre
            junreKongYanVset = valveGivenAirSmokeJunre


            valveset1 = [junreAirValveSet1,junreGasValveSet1,junreKongYanVset,  junreMeiYanVset,
                         jiareAirValveSet1,jiareGasValveSet1, jiareKongYanVset, jiareMeiYanVset,
                         yureAirValveSet1,yuregasValveSet1, yureKongYanVset, yureMeiYanVset,
                         mainValveSet1]
            print("valveset1===========================================================================================", valveset1)
#往PLC里面写入数据
        # 写心跳信号程序
            if gasPressure > 2 and connectMysql==1:
                if heart1s == False and timeNow >= timeHeart1s:
                    heart1s = True
                    timeHeart1s = timeNow + 1
                if heart1s == True and timeNow >= timeHeart1s:
                    heart1s = False
                    timeHeart1s = timeNow + 1
            else:
                print("煤气总管压力小于2000pa或者数据库时间差和实际的时间相差8秒")
            print("heart1s:", heart1s)


#
# # 将心跳信号和实际的经过处理的阀位值全部写入PLC内部

            if __name__ == "__main__":
                try:
                    siemens = SiemensS7Net(SiemensPLCS.S300, "140.80.0.4")
                    print("haha")
                    if siemens.ConnectServer().IsSuccess == False:
                        print("connect falied")
                    else:
                        # real array read write test
                        siemens.WriteFloat("DB1006.0", valveset1)
                        siemens.WriteBool("DB1006.56.0", heart1s)
                    siemens.ConnectClose()
                except Exception as e:
                    print("e=", e)

        except Exception as e:
            print("e2=", e)
            print("==================================================")
        time1s = timeNow + 1
        print("总用时长=", float(time.time())-time001)
    time.sleep(0.1)



