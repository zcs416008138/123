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
    host='10.0.106.19',
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



leng1 = 80000
sqlread ="SELECT * FROM shaft8a.shaftzone where zoneID= 1 order by timeID DESC limit "+str(leng1) # 南为1
dataRead1 = readMysqlToArry(sqlread,leng1)

timeID = dataRead1[:,0]                    #时间戳
south_gasFlow = dataRead1[:,3]             #南煤气流量
south_furnaceTemA = dataRead1[:,9]         #南燃烧室温度
south_tempGiven = dataRead1[:,14]          #南给定温度


sqlread ="SELECT * FROM shaft8a.shaftmain order by timeID DESC limit "+str(leng1)
dataRead2 = readMysqlToArry(sqlread,leng1)

isAuto = dataRead2[:,11]

sqlread ="SELECT * FROM shaft8a.shaftzone where zoneID= 2 order by timeID DESC limit "+str(leng1) # 北为2
dataRead1 = readMysqlToArry(sqlread,leng1)

north_gasFlow = dataRead1[:,3]             #北煤气流量
north_furnaceTemA = dataRead1[:,9]         #北燃烧室温度
north_tempGiven = dataRead1[:,14]          #北给定温度





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



X1 = dataClean(south_gasFlow, 5000)
X2 = dataClean(south_furnaceTemA, south_tempGiven[0])
X3 = dataClean(north_gasFlow,5000)
X4 = dataClean(north_furnaceTemA,north_tempGiven[0])
X5 = dataClean(isAuto,0.5)

timex = timechange(timeID)


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
plt.plot(timex, X1, '-', label='south_gasFlow=%.2f'%np.mean(X1))
plt.xticks(timex)
#plt.yticks(np.arange(0,50,10))
plt.legend()

#第一个子图，3代表三行，1代表1列，2代表第二个图
plt.subplot(5,1,2) # 这一点可以略写的，当三个数都小于10
plt.plot(timex, X2, 'b', ls='-', label='south_furnaceTemA=%.2f'%np.mean(X2))
plt.xticks(timex)
#plt.yticks(np.arange(0,30,10))
plt.legend()

#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,3)
plt.plot(timex, X3, 'r-', label='north_gasFlow=%.2f'%np.mean(X3))
plt.xticks(timex)
#plt.yticks(np.arange(0,20,5))
plt.legend()


#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,4)
plt.plot(timex, X4, 'b-', label='north_furnaceTemA=%.2f'%np.mean(X4))
plt.xticks(timex)
#plt.yticks(np.arange(0,20,5))
plt.legend()


#第一个子图，3代表三行，1代表1列，3代表第三个图
plt.subplot(5,1,5)
plt.plot(timex, X5, 'b-', label='isAuto=%.2f'%np.mean(X5))
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