import matplotlib.pyplot as plt
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import numpy as np
from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits import axisartist


#此程序可以根据需要画多个曲线图。PLT 多个数据， plt多个图对比分析
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
    host='10.0.104.20',
    port=3306,
    user='furnace',
    password='furnace',
    database='sinter',
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



leng1 = 170
#此数据的写入是从刘永的JAVA程序写入的数据。
#从本地数据库读取数据，然后首先校验数据的时间戳和心跳信号，如果有问题，则进行提示，并且停止智能燃烧
sqlread ="SELECT * FROM sinter.sinterkep order by timeID DESC limit "+str(leng1)
dataRead = readMysqlToArry(sqlread,leng1)
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
gasFlowSet = dataRead[:,8]            #煤气流量给定PYTHON给PLC






#添加标题
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Curve of Temperature Change with Time')

#plt.savefig('./plt_png/test1.3.png')
plt.show()

#






def dataClean(data0,tempset):
    datareturn = []
    for x in range(int(len(data0)/10)):
        # print("kkkkk=",type(np.mean(data0[x*10:x*10+10])))
        # print("tempset=",tempset)
        if np.mean(data0[x*10:x*10+10])>=tempset:
            datareturn.append(max(data0[x*10:x*10+10]))
        elif  np.mean(data0[x*10:x*10+10])< tempset:
            datareturn.append(min(data0[x * 10:x * 10 + 10]))
    return datareturn


def timechange(time00):
    datareturn = []
    for x in range(int(len(time00) / 10)):
        datareturn.append(time00[x*10])
    return datareturn



X1 = dataClean(gasFlow, tempGiven[0])
X2 = dataClean(tempA, tempGiven[0])
X3 = dataClean(gasFlowSet,tempGiven[0])
X4 = dataClean(mainGasPress,tempGiven[0])
X5 = dataClean(mode,tempGiven[0])

timex = timechange(timeID)








print("gasflow=",gasFlow)
print("X1=", X1)







# #生成数据
# import random
# import numpy as np
# #随机产生20个1-50/30/20之间的整数(不包含50，30，20)
# y1 = np.random.randint(1,50,20)
# y2 = np.random.randint(1,30,20)
# y3 = np.random.randint(1,15,20)
#
# x = np.arange(20)
# plt.figure(1, figsize=(8,6), dpi=100)

#第一个子图，3代表三行，1代表1列，1代表第一个图
plt.subplot(5,1,1)
plt.plot(timex, X1, '-', label='gasFlow: Mean=%.2f'%np.mean(X1))
plt.xticks(timex)
#plt.yticks(np.arange(0,50,10))
plt.legend()

#第一个子图，3代表三行，1代表1列，2代表第二个图
plt.subplot(5,1,2) # 这一点可以略写的，当三个数都小于10
plt.plot(timex, X2, 'b', ls='-', label='tempA: Mean=%.2f'%np.mean(X2))
plt.xticks(timex)
#plt.yticks(np.arange(0,30,10))
plt.legend()

#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,3)
plt.plot(timex, X3, 'r-', label='gasFlowSet: Mean=%.2f'%np.mean(X3))
plt.xticks(timex)
#plt.yticks(np.arange(0,20,5))
plt.legend()


#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,4)
plt.plot(timex, X4, 'b-', label='mainGasPress: Mean=%.2f'%np.mean(X4))
plt.xticks(timex)
#plt.yticks(np.arange(0,20,5))
plt.legend()


#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,5)
plt.plot(timex, X5, 'b-', label='mode: Mean=%.2f'%np.mean(X5))
plt.xticks(timex)
#plt.yticks(np.arange(0,20,5))
plt.legend()







# #第一个子图，3代表三行，1代表1列，3代表第三个图
# plt.subplot(5,1,5)
# plt.plot(timex, mode, 'b-', label='mode: Mean=%.2f'%np.mean(X5))
# plt.xticks(timex)
# #plt.yticks(np.arange(0,20,5))
# plt.legend()


#展示
plt.show()