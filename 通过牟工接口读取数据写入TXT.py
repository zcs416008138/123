import requests, json
import threading
import time


#秒级区间查询开始到结束时间，查询一个区间段的多比数据
def miaojiqujian(eid):
    url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"
    data = {
	"id":[eid],
	"beginTime":"2022-03-10 00:00:00",
	"endTime":"2022-04-25 00:00:00",
    "limit":9999999,
    "orderBy":"desc"
    }
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据

    data0 = res.text
    data11 = json.loads(data0)  # 将json数据转化为字典数据。
    #print("data11=", data11)  # 打印出结果
    return data11


eids =["ede2b961","0b7fa433","0b3187f1","265a6509","3b93a86a","f4e97339","aaeca8a8","e7e588f0","35297c30","a9a815f9","c4053444","7122896f","1325f51c","070cd895","060dc2cd","7e292f40","3c536058","1b6aa326","30100120064","90077214","e88d76b8","ab7fb76b","016b4a74","05e6742d","09b2dc53","0e265e73","1114afbb","13304517","19f71256","202b9816","228f0b7a","2f612f25","30733538","31a09b2b","32f129cb","358d4bf7","3880489d","3b581e5d","3d723df3","440200a2","4a30e83a","4d1d2e64","5762e43d","5fdb1213","5ff911f3","63821adc","6672a324","74258211","80fa1286","813eb0c0","83462f93","8e973abc","927d78fa","99b33c98","aeb40393","b4795206","cb9a7def","d301635f","d3ee3f14","dd41477c","f2b7b640","fec7a68b"]


for x in eids:
    time0 = time.time()
    result = miaojiqujian(x)
    f2 = open('C:\\Users\\Z\\Desktop\\给西门子导出的数据\\' + x + '.txt', 'r+')
    f2.read()
    f2.write(str(result))
    f2.close()

    timeend = time.time()
    print("执行时间：", timeend - time0, "秒")
    time.sleep(1)

