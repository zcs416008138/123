import requests
import json

#秒级区间查询
def miaojiqujian():
     url = "http://e.ai:8083/data-governance/sensor/batch/seconds/all"
     data={
     "id":["e7e588f0"],
     "beginTime":"2022-03-03 08:00:00",
     "endTime":"2022-03-03 09:00:00",
     "limit":5000,
     "orderBy":"desc"}
     headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
     res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
     print("result=", res.text)  # 打印出结果
     data0 = res.text
     data11 = json.loads(data0)  # 将json数据转化为字典数据。
     return data11



datalist = miaojiqujian()
ll1 = datalist['data']
# print(ll1)
# print(ll1[0])
ll2 = ll1[0]
# print(ll2)
ll3 = ll2['datas']
# print(len(ll3))
a = 0.00
for i in range(len(ll3)):
    ll4= ll3[i]
    ll5 = ll4['4']
    ll5 = ll5.replace(',','')
    ll5 = float(ll5)
    # print(ll5)
    a += ll5
b = a/3600
print("3600笔平均数为：",b)
