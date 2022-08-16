import requests, json
import numpy as np
import pandas as pd
import time

np.set_printoptions(linewidth=400)


def sanbi( eid0):
    data ={
        "id": [0],
        "type": "all",
        # "ms": 200000,
        "count": 10
    }
    data["id"]=eid0
    # print("data=",data)
    url1 = "http://e.ai:8083/latest-service/sensor/recently/query"

    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res1 = requests.post(url=url1, data=json.dumps(data), headers=headers)  # 调用数据
    # print(res1)
    data0 = res1.text
    # print(data0)
    # print("data0=", data0)
    return data0


def readexcel(exceladress, sheet):
    global senddict
    # df = pd.read_excel(exceladress,keep_default_na=False)
    df = pd.read_excel(exceladress, sheet_name=sheet, keep_default_na=False)
    df2 = df.values
    eid = df2[0:,1]
    # print(eid)
    return eid


def xunhuan(list,n):
    for i in range(len(list3)):  # 表v_list0
        list4 = list3[i]
        list5 = list4['datas']
        list8 = list5[n]
        listv = list8['v']
        list.append(listv)

def diaoqushuju():
    timenow2 = int(time.time())
    time1 = 0
    while True:
        timenow = int(time.time())
        if timenow >= time1:
            time1 = timenow + 1
            list1 = readexcel("./EID.xlsx", "Sheet1")
            # print(list1)
            list2 = []
            for i in list1:  # 调取表格内数据
                list2.append(str(i))
            list_hanshu = list2
            data1 = sanbi(list_hanshu)
            # print('data1类型',type(data1))
            list_dict = json.loads(data1)
            list2.insert(0, 'timeStamp')  # 表头
            list2.insert(0, 'timeID')
            # print(list2)
            # print('list_dict:',list_dict)
            global list3
            list3 = list_dict['data']
            # print('list3:',list3)
            list6 = []

            v_list0 = []
            v_list1 = []
            v_list2 = []
            v_list3 = []
            v_list4 = []
            v_list5 = []
            v_list6 = []
            v_list7 = []
            v_list8 = []
            v_list9 = []

            listtime = []
            listshuju = []  # 所有eid是list3
            names = locals()
            # print(list3)
            for i in range(len(list3)):  # list5是其中一个eid，list6是所有eid
                list4 = list3[i]
                list5 = list4['datas']
                list6.append(list5)

            for i in range(len(list5)):  # 加入列表中的时间以及时间戳
                list8 = list5[i]
                listID = list8['timeID']
                listStamp = list8['timeStamp']
                names['v_list' + str(i)].append(listID)
                names['v_list' + str(i)].append(listStamp)
                # print(names['v_list' + str(i)])


            xunhuan(v_list0, 0)
            xunhuan(v_list1, 1)
            xunhuan(v_list2, 2)
            xunhuan(v_list3, 3)
            xunhuan(v_list4, 4)
            xunhuan(v_list5, 5)
            xunhuan(v_list6, 6)
            xunhuan(v_list7, 7)
            xunhuan(v_list8, 8)
            xunhuan(v_list9, 9)


            listkong = []
            listkong.insert(0, list2)
            listkong.insert(1, v_list0)
            listkong.insert(2, v_list1)
            listkong.insert(3, v_list2)
            listkong.insert(4, v_list3)
            listkong.insert(5, v_list4)
            listkong.insert(6, v_list5)
            listkong.insert(7, v_list6)
            listkong.insert(8, v_list7)
            listkong.insert(9, v_list8)
            listkong.insert(10, v_list9)
            # listkong.insert(11,list01)
            # print(listkong)
            listmain = np.matrix(listkong)
            print(listmain)
            # print(type(listmain))
            # print(listmain[:,2])            # 调取对应列数据


            print("程序运行时间为:", int(time.time()) - timenow2)

            time.sleep(0.1)

diaoqushuju()