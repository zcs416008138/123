import requests, json
import numpy as np
import pandas as pd



def sanbi(eid0):
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
    for i in range(len(list_data)):  # 表v_list0
        list_v = list_data[i]['datas'][n]['v']      # list_v是所需要的值
        list.append(list_v)

def hanshu():
    list_biaoge = readexcel("./新棒材加热炉(读取).xlsx", "Sheet1")    # 调取表格内数据
    # print(list_biaoge)
    list_biaotou = []
    for i in list_biaoge:         # 转变格式
        list_biaotou.append(str(i))
    # print('list_biaotou=',list_biaotou)

    list_hanshu = list_biaotou
    list_all = sanbi(list_hanshu)              # 根据eid调取数据
    # print(list_all)
    # print('list_all类型',type(list_all))
    list_all = json.loads(list_all)        # 转换格式
    list_biaotou.insert(0, 'timeStamp')  # 添加表头
    list_biaotou.insert(0, 'timeID')
    # print(list_biaotou)
    global list_data
    list_data= list_all['data']
    # print('list_data:',list_data)


    v_list0 = []            # 设立空表
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
    list6 = []
    names = locals()
    # print(list3)
    for i in range(len(list_data)):  # list5是其中一个eid，list6是所有eid
        list5 = list_data[i]['datas']
        list6.append(list5)
    # print('list5：',list5)
    # print('list6:',list6)

    for i in range(len(list5)):  # 加入列表中的时间以及时间戳(所有eid时间相同，所以只取list5中的时间即可)
        list_timeID = list5[i]['timeID']
        list_timeStamp = list5[i]['timeStamp']
        listtime.append(list_timeID)
        listtime.append(list_timeStamp)
        names['v_list' + str(i)] = listtime
        listtime = []
    # print('listtime_all:',listtime_all)


    listkong = []
    listkong.insert(0, list_biaotou)
    for i in range(10):                                 # 将处理好的数据依次添加到listkong
        xunhuan(names['v_list' + str(i)], i)
        listkong.insert(i+1, names['v_list' + str(i)])

    list_juzhen = np.matrix(listkong)                   # listkong转换为矩阵
    # print(list_juzhen)


    list_juzhen_wubiaotou = np.delete(list_juzhen,0,0)            # 删掉矩阵表头
    # print(list_juzhen_wubiaotou)
    new_dict = {}                           # 字典
    for i in range(len(list_biaotou)):      # 将矩阵数据倒入字典
        names['list' + str(i)] = []
        for j in range(10):
            names['list' + str(i)].append(list_juzhen_wubiaotou[j,i])
        new_dict[list_biaotou[i]] = names['list' + str(i)]
    # print('new_dict:',new_dict)
    return(list_juzhen,new_dict)


list_juzhen,new_dict = hanshu()
print(list_juzhen)
print(new_dict)
