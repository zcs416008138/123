import requests, json
import datetime
import pymysql
import time
import calendar
import os
import logging
import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from win32com.client import Dispatch
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


def diaoqushuju(eid0,cur,pre):
    url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"   #秒级数据区间查询
    #url = "http://e.ai:8083/data-governance/sensor/batch/hour/avg"

    #url ="http://e.ai:8083/data-governance/sensor/batch/minite/avg"
    data = {
        "id":eid0,            #在此处填写要查询的eid
        "beginTime": pre,       #在此处填写要查询的开始时间
        "endTime": cur,          #在此处填写要查询的结束时间
        "limit": 9000000,                            #最大数据量
        "orderBy": "desc"}#desc倒序排列，asc正序排列
    #print("data=",data)
    # print("开始从数据库里面读取文件，需要较长时间，请耐心等待")
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
    #print("result=", res.text)  # 打印出结果
    data0 = res.text
    data1 =  json.loads(data0)
    # print("data0=",data0)
    # data11 = json.loads(data0)  # 将json数据转化为字典数据。
    # print(data11)
    return data1


def shujuchuli(shuju,h):      #      将1h内的3600笔数据取平均
    # print('数据=',shuju)
    # print(type(shuju))
    datalist = shuju
    ll1 = datalist['data']
    # print(ll1)
    # print(ll1[0])
    ll2 = ll1[0]
    # print(ll2)
    ll3 = ll2['datas']
    # print(len(ll3))
    a = 0.00
    for i in range(len(ll3)):
        ll4 = ll3[i]
        # print(ll4)
        ll5 = ll4[h]
        ll5 = ll5.replace(',','')
        ll5 = float(ll5)
#         # print(ll5)
        a += ll5
    b = a/3600
    c = round(b,2)
    # print("3600笔平均数为：",c)
    return c


def Burner_dispose(Burner):
    # print(Burner)
    ll1 = Burner['data']
    # print('ll1:', ll1)
    ll2 = ll1[0]
    # print('ll2:',ll2)
    ll3 = ll2['datas']
    return ll3


def feiqishuju(aaa,bbb):
    shuzhu = []
    for i in range(len(aaa)):
        if aaa[i]['14'] == '0.00':
            for j in range(len(bbb)):
                if aaa[i]['timeID'] == bbb[j]['timeID']:
                    shuzhu.append(float(bbb[j]['4']))
    a = sum(shuzhu)
    b = int(len(shuzhu))
    ccc = a / b
    return ccc


def value(val_co,val_h2):           # 计算1h内平均热值以及空燃比
    heat_value = (val_co * 3046 + val_h2 * 2580) / 100 * 4.184       # *4.184将千卡换算为千焦
    lilun_k = (val_co * 0.5 + val_h2 * 0.5) / 0.21 / 100
    excess_air_coefficient = 1.2    # 空气过剩系数
    air_fuel_ratio = lilun_k * excess_air_coefficient
    # heat_value = round(heat_value,2)
    # air_fuel_ratio = round(air_fuel_ratio,2)
    return [heat_value, air_fuel_ratio]


# 插入数据
def func(insertdata, data):
    conn = POOL2.connection()
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


shujuFalse = 0
while True:
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")         # 获取当前时间
        cur = (datetime.datetime.now() + datetime.timedelta(seconds=-10)).strftime("%Y-%m-%d %H:%M:%S")                 # 获取当前时间前10秒
        pre = (datetime.datetime.now() + datetime.timedelta(hours=-1,seconds=-10)).strftime("%Y-%m-%d %H:%M:%S")        # 获取cur一个小时之前的时间
        print('现在时间为：',now)
        print('调取的时间区间为：',pre,'~',cur)          # 调取的时间相对于现在提前10秒（否则调取的数据参差不齐，无法对照）


        NO4bf_co = ['6e7e9a99']     # 4号高炉co浓度
        NO4bf_co = shujuchuli((diaoqushuju(NO4bf_co,cur,pre)),'9')
        NO4bf_h2 = ['b1687620']     # 4号高炉h2浓度
        NO4bf_h2 = shujuchuli((diaoqushuju(NO4bf_h2,cur,pre)),'9')
        NO5bf_co = ['7358300b']     # 5号高炉co浓度
        NO5bf_co = shujuchuli((diaoqushuju(NO5bf_co,cur,pre)),'9')
        NO5bf_h2 = ['d0ae0913']     # 5号高炉h2浓度
        NO5bf_h2 = shujuchuli((diaoqushuju(NO5bf_h2,cur,pre)),'9')

        list4_value_air = value(NO4bf_co,NO4bf_h2)
        list5_value_air = value(NO5bf_co,NO5bf_h2)
        # print('4#高炉热值以及空燃比：',list4_value_air)
        # print('5#高炉热值以及空燃比：',list5_value_air)

        NO4_gas_flow = ['660bac10']      # 4号高炉煤气流量
        NO4_gas_flow = shujuchuli((diaoqushuju(NO4_gas_flow,cur,pre)),'2')
        NO5_gas_flow = ['de29ffd4']      # 5号高炉煤气流量
        NO5_gas_flow = shujuchuli((diaoqushuju(NO5_gas_flow,cur,pre)),'2')
        heat_value = NO4_gas_flow / (NO4_gas_flow + NO5_gas_flow) * list4_value_air[0] +  NO5_gas_flow / (NO4_gas_flow + NO5_gas_flow) * list5_value_air[0]
        air_fuel_ratio = NO4_gas_flow / (NO4_gas_flow + NO5_gas_flow) * list4_value_air[1] +  NO5_gas_flow / (NO4_gas_flow + NO5_gas_flow) * list5_value_air[1]
        # print('平均热值为：',heat_value,'KJ/m3')
        # print('平均空燃比为：',air_fuel_ratio)

        gas_flow_all = ['265a6509']     # 煤气总管流量
        gas_flow_all = shujuchuli((diaoqushuju(gas_flow_all,cur,pre)),'2')

        Burn_exothermic = gas_flow_all * heat_value     # 燃料燃烧的化学热
        Burn_exothermic = round(Burn_exothermic,2)
        # print('燃烧放热为：',Burn_exothermic,'KJ')


        Billet = ['9e01f4db']       # 过钢根数
        Billet = diaoqushuju(Billet,cur,pre)
        ll1 = Billet['data']
        ll2 = ll1[0]
        ll3 = ll2['datas']
        for i in range(len(ll3)):           # 将数据处理，因为是倒叙排列，所以第一个数据减去最后一个数据加1就是过钢根数
            if i == 0:
                ll4 = ll3[i]
                # print(ll4)
                ll5 = ll4['50']
                ll5 = ll5.replace(',', '')
                ll5 = float(ll5)
                a = ll5
                # print('a=',a)
            elif i == len(ll3)-1:
                ll4 = ll3[i]
                # print(ll4)
                ll5 = ll4['50']
                ll5 = ll5.replace(',', '')
                ll5 = float(ll5)
                b = ll5
                # print('b=',b)
        if a == b:
            Billet_number = 0
        else:
            Billet_number = a - b + 1        # 1个小时过钢根数
        print('过钢根数为：',int(Billet_number),'根')


        '''
        钢坯质量（后续根据钢坯长度进行计算）：307200cm3 * 7.85g/cm3 = 2411520 g
        烧损暂定：1%      每根烧损为：2411520g * 1% = 24115.20 g
        铁的摩尔质量：56g/mol  每根为：24115.2g / 56g/mol = 430.63 mol
        2Fe + O2 = 2FeO   3Fe + 2O2 = Fe3O4   4Fe + 3O2 = 2Fe2O3
        FeO标准摩尔生成焓：-271.96kJ/mol
        Fe3O4标准摩尔生成焓：-1118.38kJ/mol
        Fe2O3标准摩尔生成焓：-824.25 kJ/mol
        FeO:Fe3O4:Fe2O3 = 95:4:1
        FeO:   430.63mol * 95 / 109 / 1 = 375.31 mol    ;   375.31mol * 271.96KJ/mol = 102069.31 KJ
        Fe3O4: 430.63mol * 12 / 109 / 3 = 15.8 mol      ;   15.8mol * 1118.38KJ/mol = 17670.40 KJ
        Fe2O3: 430.63mol * 2 / 109 / 2 = 3.95 mol       ;   3.95mol * 824.25KJ/mol = 3255.79 KJ
        一根钢坯氧化放热为：102069.31 + 17670.40 + 3255.79 = 122995.5 KJ 
        '''


        if Billet_number == 0:
            print('过钢根数为0，数据不录入，请等待~')
        else:
            Oxidative_exothermic = Billet_number * 122995.5  # 每根钢坯氧化放热量
            All_exothermic = Burn_exothermic + Oxidative_exothermic  # 放热总量
            Burn_proportion = Burn_exothermic / All_exothermic * 100  # 燃烧放热量占比
            Burn_proportion = round(Burn_proportion, 2)
            Oxidative_proportion = Oxidative_exothermic / All_exothermic * 100  # 氧化放热量占比
            Oxidative_proportion = round(Oxidative_proportion, 2)
            print('燃烧放热为：',Burn_exothermic,'KJ','占放热总量：',Burn_proportion,'%')
            print('氧化放热为：',Oxidative_exothermic,'KJ','占放热总量：',Oxidative_proportion,'%')


            #查看gangpiNumber 数据库
            sql0 = "SELECT * FROM newbar.gangpiNumber order by timeID desc limit " + str(int(Billet_number))
            # print("sql0=",sql0)
            arr0 = readMysql(POOL, sql0)
            recentId = arr0[:,2]    # 一个小时钢坯入炉温度
            # print(len(recentId))
            # print(recentId)

            sql0 = "SELECT * FROM newbar.gangpiNumber where timeOutFuc is not null order by timeID desc limit " + str(int(Billet_number))
            arr0 = readMysql(POOL, sql0)
            tempOutFunc = arr0[:,8]     # 一个小时出炉温度
            # print(len(tempOutFunc))
            # print(tempOutFunc)
            Furnace_temperature = recentId.sum()        # 入炉温度和
            Oven_temperature = tempOutFunc.sum()        # 出炉温度和
            Furnace_temperature = round(Furnace_temperature,2)
            Oven_temperature = round(Oven_temperature,2)
            # print('入炉温度和：',Furnace_temperature,'出炉温度和：',Oven_temperature)
            '''
            钢坯比热容 460J/(Kg*°C)
            '''
            Billet_absorbs_heat = (Oven_temperature - Furnace_temperature) * 460 * 2411.52 / 1000       # 计算钢坯吸热
            Billet_absorbs_heat_proportion = Billet_absorbs_heat / All_exothermic * 100     # 钢坯吸热占比
            Billet_absorbs_heat_proportion = round(Billet_absorbs_heat_proportion,2)
            Billet_absorbs_heat = round(Billet_absorbs_heat,2)
            print('钢坯吸热：',Billet_absorbs_heat,'KJ','钢坯吸热占比：',Billet_absorbs_heat_proportion,'%')

            bf_co = NO4_gas_flow / (NO4_gas_flow + NO5_gas_flow) * NO4bf_co +  NO5_gas_flow / (NO4_gas_flow + NO5_gas_flow) * NO5bf_co      # 平均co，h2浓度
            bf_h2 = NO4_gas_flow / (NO4_gas_flow + NO5_gas_flow) * NO4bf_h2 +  NO5_gas_flow / (NO4_gas_flow + NO5_gas_flow) * NO5bf_h2

            # 调取加热炉内各个烧嘴的eid数据
            west_11_Burner = ['58a07b2e']                                                        # 进气排烟状态
            west_11_Burner = Burner_dispose(diaoqushuju(west_11_Burner,cur,pre))
            # print('一段西侧第一组烧嘴进气/排烟状态:',west_11_Burner)
            west_11_Burner_air = ['63821adc']                                                    # 空气烧嘴冷端温度
            west_11_Burner_air = Burner_dispose(diaoqushuju(west_11_Burner_air,cur,pre))
            # print('一段西侧第一组空气烧嘴冷端:',west_11_Burner_air)
            west_11_Burner_gas = ['202b9816']                                                     # 煤气烧嘴冷端温度
            west_11_Burner_gas = Burner_dispose(diaoqushuju(west_11_Burner_gas,cur,pre))
            # print('一段西侧第一组煤气烧嘴冷端:',west_11_Burner_gas)

            west_12_Burner = ['def4de2a']
            west_12_Burner = Burner_dispose(diaoqushuju(west_12_Burner,cur,pre))
            west_12_Burner_air = ['8e973abc']
            west_12_Burner_air = Burner_dispose(diaoqushuju(west_12_Burner_air,cur,pre))
            west_12_Burner_gas = ['358d4bf7']
            west_12_Burner_gas = Burner_dispose(diaoqushuju(west_12_Burner_gas,cur,pre))

            west_13_Burner = ['c9439dd4']
            west_13_Burner = Burner_dispose(diaoqushuju(west_13_Burner,cur,pre))
            west_13_Burner_air = ['74258211']
            west_13_Burner_air = Burner_dispose(diaoqushuju(west_13_Burner_air,cur,pre))
            west_13_Burner_gas = ['3b581e5d']
            west_13_Burner_gas = Burner_dispose(diaoqushuju(west_13_Burner_gas,cur,pre))

            west_14_Burner = ['e9a1cc09']
            west_14_Burner = Burner_dispose(diaoqushuju(west_14_Burner,cur,pre))
            west_14_Burner_air = ['09b2dc53']
            west_14_Burner_air = Burner_dispose(diaoqushuju(west_14_Burner_air,cur,pre))
            west_14_Burner_gas = ['aeb40393']
            west_14_Burner_gas = Burner_dispose(diaoqushuju(west_14_Burner_gas,cur,pre))

            east_11_Burner = ['5250a4db']
            east_11_Burner = Burner_dispose(diaoqushuju(east_11_Burner,cur,pre))
            east_11_Burner_air = ['5ff911f3']
            east_11_Burner_air = Burner_dispose(diaoqushuju(east_11_Burner_air,cur,pre))
            east_11_Burner_gas = ['5762e43d']
            east_11_Burner_gas = Burner_dispose(diaoqushuju(east_11_Burner_gas,cur,pre))

            east_12_Burner = ['52bd4167']
            east_12_Burner = Burner_dispose(diaoqushuju(east_12_Burner,cur,pre))
            east_12_Burner_air = ['99b33c98']
            east_12_Burner_air = Burner_dispose(diaoqushuju(east_12_Burner_air,cur,pre))
            east_12_Burner_gas = ['440200a2']
            east_12_Burner_gas = Burner_dispose(diaoqushuju(east_12_Burner_gas,cur,pre))

            east_13_Burner = ['4184cce6']
            east_13_Burner = Burner_dispose(diaoqushuju(east_13_Burner,cur,pre))
            east_13_Burner_air = ['4a30e83a']
            east_13_Burner_air = Burner_dispose(diaoqushuju(east_13_Burner_air,cur,pre))
            east_13_Burner_gas = ['31a09b2b']
            east_13_Burner_gas = Burner_dispose(diaoqushuju(east_13_Burner_gas,cur,pre))

            east_14_Burner = ['7e08b105']
            east_14_Burner = Burner_dispose(diaoqushuju(east_14_Burner,cur,pre))
            east_14_Burner_air = ['cb9a7def']
            east_14_Burner_air = Burner_dispose(diaoqushuju(east_14_Burner_air,cur,pre))
            east_14_Burner_gas = ['3d723df3']
            east_14_Burner_gas = Burner_dispose(diaoqushuju(east_14_Burner_gas,cur,pre))

            west_21_Burner = ['bb8b2be1']
            west_21_Burner = Burner_dispose(diaoqushuju(west_21_Burner,cur,pre))
            west_21_Burner_air = ['927d78fa']
            west_21_Burner_air = Burner_dispose(diaoqushuju(west_21_Burner_air,cur,pre))
            west_21_Burner_gas = ['2f612f25']
            west_21_Burner_gas = Burner_dispose(diaoqushuju(west_21_Burner_gas,cur,pre))

            west_22_Burner = ['c940acc7']
            west_22_Burner = Burner_dispose(diaoqushuju(west_22_Burner,cur,pre))
            west_22_Burner_air = ['5fdb1213']
            west_22_Burner_air = Burner_dispose(diaoqushuju(west_22_Burner_air,cur,pre))
            west_22_Burner_gas = ['32f129cb']
            west_22_Burner_gas = Burner_dispose(diaoqushuju(west_22_Burner_gas,cur,pre))

            west_23_Burner = ['a7dd0c34']
            west_23_Burner = Burner_dispose(diaoqushuju(west_23_Burner,cur,pre))
            west_23_Burner_air = ['83462f93']
            west_23_Burner_air = Burner_dispose(diaoqushuju(west_23_Burner_air,cur,pre))
            west_23_Burner_gas = ['d3ee3f14']
            west_23_Burner_gas = Burner_dispose(diaoqushuju(west_23_Burner_gas,cur,pre))

            west_24_Burner = ['883686bd']
            west_24_Burner = Burner_dispose(diaoqushuju(west_24_Burner,cur,pre))
            west_24_Burner_air = ['6672a324']
            west_24_Burner_air = Burner_dispose(diaoqushuju(west_24_Burner_air,cur,pre))
            west_24_Burner_gas = ['13304517']
            west_24_Burner_gas = Burner_dispose(diaoqushuju(west_24_Burner_gas,cur,pre))

            east_21_Burner = ['72cb9845']
            east_21_Burner = Burner_dispose(diaoqushuju(east_21_Burner,cur,pre))
            east_21_Burner_air = ['1114afbb']
            east_21_Burner_air = Burner_dispose(diaoqushuju(east_21_Burner_air,cur,pre))
            east_21_Burner_gas = ['80fa1286']
            east_21_Burner_gas = Burner_dispose(diaoqushuju(east_21_Burner_gas,cur,pre))

            east_22_Burner = ['1ac67e23']
            east_22_Burner = Burner_dispose(diaoqushuju(east_22_Burner,cur,pre))
            east_22_Burner_air = ['3880489d']
            east_22_Burner_air = Burner_dispose(diaoqushuju(east_22_Burner_air,cur,pre))
            east_22_Burner_gas = ['fec7a68b']
            east_22_Burner_gas = Burner_dispose(diaoqushuju(east_22_Burner_gas,cur,pre))

            east_23_Burner = ['3e28f927']
            east_23_Burner = Burner_dispose(diaoqushuju(east_23_Burner,cur,pre))
            east_23_Burner_air = ['0e265e73']
            east_23_Burner_air = Burner_dispose(diaoqushuju(east_23_Burner_air,cur,pre))
            east_23_Burner_gas = ['016b4a74']
            east_23_Burner_gas = Burner_dispose(diaoqushuju(east_23_Burner_gas,cur,pre))

            east_24_Burner = ['20b99c4c']
            east_24_Burner = Burner_dispose(diaoqushuju(east_24_Burner,cur,pre))
            east_24_Burner_air = ['f2b7b640']
            east_24_Burner_air = Burner_dispose(diaoqushuju(east_24_Burner_air,cur,pre))
            east_24_Burner_gas = ['dd41477c']
            east_24_Burner_gas = Burner_dispose(diaoqushuju(east_24_Burner_gas,cur,pre))

            west_31_Burner = ['9f02c496']
            west_31_Burner = Burner_dispose(diaoqushuju(west_31_Burner,cur,pre))
            west_31_Burner_air = ['4d1d2e64']
            west_31_Burner_air = Burner_dispose(diaoqushuju(west_31_Burner_air,cur,pre))
            west_31_Burner_gas = ['b4795206']
            west_31_Burner_gas = Burner_dispose(diaoqushuju(west_31_Burner_gas,cur,pre))

            west_32_Burner = ['5a837c3a']
            west_32_Burner = Burner_dispose(diaoqushuju(west_32_Burner,cur,pre))
            west_32_Burner_air = ['30733538']
            west_32_Burner_air = Burner_dispose(diaoqushuju(west_32_Burner_air,cur,pre))
            west_32_Burner_gas = ['d301635f']
            west_32_Burner_gas = Burner_dispose(diaoqushuju(west_32_Burner_gas,cur,pre))

            east_31_Burner = ['7b75cd95']
            east_31_Burner = Burner_dispose(diaoqushuju(east_31_Burner,cur,pre))
            east_31_Burner_air = ['19f71256']
            east_31_Burner_air = Burner_dispose(diaoqushuju(east_31_Burner_air,cur,pre))
            east_31_Burner_gas = ['813eb0c0']
            east_31_Burner_gas = Burner_dispose(diaoqushuju(east_31_Burner_gas,cur,pre))

            east_32_Burner = ['fbeb23cd']
            east_32_Burner = Burner_dispose(diaoqushuju(east_32_Burner,cur,pre))
            east_32_Burner_air = ['05e6742d']
            east_32_Burner_air = Burner_dispose(diaoqushuju(east_32_Burner_air,cur,pre))
            east_32_Burner_gas = ['228f0b7a']
            east_32_Burner_gas = Burner_dispose(diaoqushuju(east_32_Burner_gas,cur,pre))

            west_11_air = feiqishuju(west_11_Burner,west_11_Burner_air)     # 一段西侧第一组空气烧嘴冷端 1H内平均温度（只计算排烟状态）
            west_11_gas = feiqishuju(west_11_Burner,west_11_Burner_gas)      # 一段西侧第一组煤气烧嘴冷端 1H内平均温度（只计算排烟状态）
            west_12_air = feiqishuju(west_12_Burner,west_12_Burner_air)
            west_12_gas = feiqishuju(west_12_Burner,west_12_Burner_gas)
            west_13_air = feiqishuju(west_13_Burner,west_13_Burner_air)
            west_13_gas = feiqishuju(west_13_Burner,west_13_Burner_gas)
            west_14_air = feiqishuju(west_14_Burner,west_14_Burner_air)
            west_14_gas = feiqishuju(west_14_Burner,west_14_Burner_gas)

            east_11_air = feiqishuju(east_11_Burner,east_11_Burner_air)
            east_11_gas = feiqishuju(east_11_Burner,east_11_Burner_gas)
            east_12_air = feiqishuju(east_12_Burner,east_12_Burner_air)
            east_12_gas = feiqishuju(east_12_Burner,east_12_Burner_gas)
            east_13_air = feiqishuju(east_13_Burner,east_13_Burner_air)
            east_13_gas = feiqishuju(east_13_Burner,east_13_Burner_gas)
            east_14_air = feiqishuju(east_14_Burner,east_14_Burner_air)
            east_14_gas = feiqishuju(east_14_Burner,east_14_Burner_gas)

            west_21_air = feiqishuju(west_21_Burner,west_21_Burner_air)
            west_21_gas = feiqishuju(west_21_Burner,west_21_Burner_gas)
            west_22_air = feiqishuju(west_22_Burner,west_22_Burner_air)
            west_22_gas = feiqishuju(west_22_Burner,west_22_Burner_gas)
            west_23_air = feiqishuju(west_23_Burner,west_23_Burner_air)
            west_23_gas = feiqishuju(west_23_Burner,west_23_Burner_gas)
            west_24_air = feiqishuju(west_24_Burner,west_24_Burner_air)
            west_24_gas = feiqishuju(west_24_Burner,west_24_Burner_gas)

            east_21_air = feiqishuju(east_21_Burner,east_21_Burner_air)
            east_21_gas = feiqishuju(east_21_Burner,east_21_Burner_gas)
            east_22_air = feiqishuju(east_22_Burner,east_22_Burner_air)
            east_22_gas = feiqishuju(east_22_Burner,east_22_Burner_gas)
            east_23_air = feiqishuju(east_23_Burner,east_23_Burner_air)
            east_23_gas = feiqishuju(east_23_Burner,east_23_Burner_gas)
            east_24_air = feiqishuju(east_24_Burner,east_24_Burner_air)
            east_24_gas = feiqishuju(east_24_Burner,east_24_Burner_gas)

            west_31_air = feiqishuju(west_31_Burner,west_31_Burner_air)
            west_31_gas = feiqishuju(west_31_Burner,west_31_Burner_gas)
            west_32_air = feiqishuju(west_32_Burner,west_32_Burner_air)
            west_32_gas = feiqishuju(west_32_Burner,west_32_Burner_gas)

            east_31_air = feiqishuju(east_31_Burner,east_31_Burner_air)
            east_31_gas = feiqishuju(east_31_Burner,east_31_Burner_gas)
            east_32_air = feiqishuju(east_32_Burner,east_32_Burner_air)
            east_32_gas = feiqishuju(east_32_Burner,east_32_Burner_gas)

            Average_exhaust_gas_temperature = (west_11_air + west_11_gas + west_12_air + west_12_gas + west_13_air + west_13_gas + west_14_air + west_14_gas +
                                               east_11_air + east_11_gas + east_12_air + east_12_gas + east_13_air + east_13_gas + east_14_air + east_14_gas +
                                               west_21_air + west_21_gas + west_22_air + west_22_gas + west_23_air + west_23_gas + west_24_air + west_24_gas +
                                               east_21_air + east_21_gas + east_22_air + east_22_gas + east_23_air + east_23_gas + east_24_air + east_24_gas +
                                               west_31_air + west_31_gas + west_32_air + west_32_gas + east_31_air + east_31_gas + east_32_air + east_32_gas ) / 40         # 排烟烧嘴平均温度
            Average_exhaust_gas_temperature = round(Average_exhaust_gas_temperature,2)
            # print('排烟烧嘴平均温度：',Average_exhaust_gas_temperature,'°C')

            Air_flow1 = ['a9a815f9']                                        # 三段空气流量
            Air_flow1 = shujuchuli((diaoqushuju(Air_flow1,cur,pre)),'2')
            Air_flow2 = ['c4053444']
            Air_flow2 = shujuchuli((diaoqushuju(Air_flow2,cur,pre)),'2')
            Air_flow3 = ['7122896f']
            Air_flow3 = shujuchuli((diaoqushuju(Air_flow3,cur,pre)),'2')
            Air_flow_all = Air_flow1 + Air_flow2 + Air_flow3                # 空气流量总和
            # print(Air_flow_all)
            Exhaust_gas_volume = Air_flow_all + gas_flow_all - (gas_flow_all * bf_co + gas_flow_all * bf_h2) / 2 /100        # 废气体积
            # print('废气体积：',Exhaust_gas_volume)
            n2_volume = Air_flow_all * 0.78 + gas_flow_all * (bf_co + bf_h2) / 100          # 废气中n2的体积
            co2_volume = Exhaust_gas_volume - n2_volume                                     # 废气中co2的体积
            # n2  1.026KJ/(Kg*°C)   1.25Kg/m3            co2  0.9043KJ/(Kg*°C)  1.96Kg/m3
            Exhaust_gas_heat = n2_volume * 1.25 * (Average_exhaust_gas_temperature - 25) + co2_volume * 1.96 * (Average_exhaust_gas_temperature - 25)       # 常温算25° ， 废气带走热量
            Exhaust_gas_heat = round(Exhaust_gas_heat,2)
            Exhaust_gas_heat_proportion = Exhaust_gas_heat / All_exothermic * 100           # 废气带走的热量占比
            Exhaust_gas_heat_proportion = round(Exhaust_gas_heat_proportion,2)
            print('废气带走的热量:',Exhaust_gas_heat,'KJ','废气带走的热量占比：',Exhaust_gas_heat_proportion,'%')


            Steam_flow = ['23c16bc3']                                           # 蒸汽流量
            Steam_flow = shujuchuli((diaoqushuju(Steam_flow,cur,pre)),'2')
            Drum_pressure = ['db425286']
            Drum_pressure = shujuchuli((diaoqushuju(Drum_pressure,cur,pre)),'3')
            # print('蒸汽流量：',Steam_flow,'t/h','汽包压力：',Drum_pressure,'Mpa')
            if Drum_pressure > 0.45 and Drum_pressure <= 0.475:         # 蒸汽在不同压强下的焓值
                Steam_enthalpy_value = 2743.8
            elif Drum_pressure > 0.475 and Drum_pressure <= 0.55:
                Steam_enthalpy_value = 2748.5
            elif Drum_pressure > 0.55 and Drum_pressure <= 0.6:
                Steam_enthalpy_value = 2756.4
            Water_heat = (Steam_enthalpy_value - 105.38) * Steam_flow * 1000    # 水的焓值105.38
            Water_heat = round(Water_heat,2)
            Water_heat_proportion = Water_heat / All_exothermic * 100     # 水冷散热占比
            Water_heat_proportion = round(Water_heat_proportion,2)
            print('水冷散热：',Water_heat,'Kj','水冷散热占比：',Water_heat_proportion,'%')


            # 炉体宽14.24m , 长31.16m , 高5.024m , 炉墙温度70°C , 炉顶温度100°C
            # 出钢口面积0.535*0.59 = 0.31565m2，扒渣口面积0.83*0.7 = 0.581m2，装料口面积12.9*0.42 = 5.418m2，共计6.31465m2
            Furnace_wall_area = (14.24 + 31.16) * 2 * 5.024 - 6.31465       # 炉墙面积（去掉孔洞）
            Furnace_roof_area = 14.24 * 31.16                               # 炉顶面积
            Furnace_wall_heat = Furnace_wall_area * 3.6 * 10 * (70 - 25)
            Furnace_roof_heat = Furnace_roof_area * 3.6 * 10 * (100 - 25)
            Furnace_heat = Furnace_wall_heat + Furnace_roof_heat
            Furnace_heat = round(Furnace_heat,2)
            Furnace_heat_proportion = Furnace_heat / All_exothermic * 100     # 炉体散热占比
            Furnace_heat_proportion = round(Furnace_heat_proportion,2)
            print('炉体散热：',Furnace_heat,'Kj','炉体散热占比：',Furnace_heat_proportion,'%')

            # 表面对流传热系数h取150 Oven_temperature
            Hole_overflow = 150 * 6.31465 * (Oven_temperature / Billet_number - 25) * 3600 / 1000       # 孔洞溢气
            # print(Hole_overflow)
            # 黑度按0.5算
            Radiant_heat = 0.5 * 5.67 / (10**8) * ((343.15**4) * Furnace_wall_area + Furnace_roof_area * (373.15**4)) * 3600 / 1000    # 辐射散热
            # print(Radiant_heat)
            Hole_overflow_Radiant_heat = Hole_overflow + Radiant_heat
            Hole_overflow_Radiant_heat = round(Hole_overflow_Radiant_heat,2)
            Hole_overflow_Radiant_heat_proportion = Hole_overflow_Radiant_heat / All_exothermic * 100     # 水冷散热占比
            Hole_overflow_Radiant_heat_proportion = round(Hole_overflow_Radiant_heat_proportion,2)
            print('孔洞溢气，辐射热：',Hole_overflow_Radiant_heat,'Kj','占比：',Hole_overflow_Radiant_heat_proportion,'%')

            Other_heat_loss = 100 - Billet_absorbs_heat_proportion - Exhaust_gas_heat_proportion - Water_heat_proportion - Furnace_heat_proportion - Hole_overflow_Radiant_heat_proportion
            Other_heat_loss = round(Other_heat_loss,2)
            Other_heat = Other_heat_loss * All_exothermic / 100
            Other_heat = round(Other_heat,2)
            print('其他热损失：',Other_heat,'Kj','占比：',Other_heat_loss,'%')

            # 查看数据库   获取当时钢坯型号
            # sql0 = "SELECT * FROM newbar.gangpiNumber order by outstd1 desc limit 1"            # 按照出炉时间排列，取最新的一笔数据
            sql0 = "SELECT timeID,nbmill_milio_mill05_guigexinghao_VALUE as guige FROM newbar.rulugenzong where timeID =  ' " + str(cur) + " ' "
            # print("sql0=",sql0)
            arr1 = readMysql(POOL, sql0)
            guige = arr1[:, 1]  # 钢坯型号
            guige = int(guige[0])       # 转换格式
            # print(len(guige))
            # print(guige)
            #
            # shuju = []
            # shuju.extend([pre,cur,guige,Billet_number,Burn_exothermic,Burn_proportion,Oxidative_exothermic,Oxidative_proportion,Billet_absorbs_heat,Billet_absorbs_heat_proportion,Exhaust_gas_heat,
            #              Exhaust_gas_heat_proportion,Water_heat,Water_heat_proportion,Furnace_heat,Furnace_heat_proportion,Hole_overflow_Radiant_heat,Hole_overflow_Radiant_heat_proportion,
            #              Other_heat,Other_heat_loss])
            # # print(shuju)
            # # print(n1)
            # insertdata = "INSERT INTO cone1(pre,cur,guige,Billet_number,Burn_exothermic,Burn_proportion,Oxidative_exothermic,Oxidative_proportion,Billet_absorbs_heat,Billet_absorbs_heat_proportion,Exhaust_gas_heat,Exhaust_gas_heat_proportion,Water_heat,Water_heat_proportion,Furnace_heat,Furnace_heat_proportion,Hole_overflow_Radiant_heat,Hole_overflow_Radiant_heat_proportion,Other_heat,Other_heat_loss)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            # func(insertdata, shuju)
    except Exception as e:
        print("e = ",e)
        shujuFalse += 1
        print("shujuFalse = ",shujuFalse)

    time.sleep(180)