import requests, json
import numpy as np


def sanbi():
    data ={
        "id": [
            "0b7fa433",
            "90077214",
            "265a6509",
            "f4e97339",
            "aaeca8a8",
            "e7e588f0",
            "a9a815f9",
            "1325f51c",
            "c4053444",
            "070cd895",
            "7122896f",
            "060dc2cd",
            "63821adc",
            "8e973abc",
            "74258211",
            "09b2dc53",
            "202b9816",
            "358d4bf7",
            "3b581e5d",
            "aeb40393",
            "5ff911f3",
            "99b33c98",
            "4a30e83a",
            "cb9a7def",
            "5762e43d",
            "440200a2",
            "31a09b2b",
            "3d723df3",
            "927d78fa",
            "5fdb1213",
            "83462f93",
            "6672a324",
            "2f612f25",
            "32f129cb",
            "d3ee3f14",
            "13304517",
            "1114afbb",
            "3880489d",
            "0e265e73",
            "f2b7b640",
            "80fa1286",
            "fec7a68b",
            "016b4a74",
            "dd41477c",
            "4d1d2e64",
            "30733538",
            "19f71256",
            "05e6742d",
            "b4795206",
            "d301635f",
            "813eb0c0",
            "228f0b7a",
            "4e3fa9f8",
            "bbcfad83",
            "060177c5",
            "0b2daf98",
            "b6f89075",
            "50f04fc9",
            "468c4663",
            "4e1a9132",
            "982dfc1b",
            "f7fc45f1",
            "f96b601b",
            "0a152f74",
            "98f38549",
            "0b3187f1",
            "64ab84a6",
            "2bfcb25b",
            "03bd8e14",
            "a1b0f2c7",
            "c6891b2f",
            "3af01a2a",
            "182f286f",
            "f467c7a2",
            "8076ca89",
            "ce791871",
            "b6cfb8eb",
            "9910d26e",
            "ca4c2065",
            "89a001dc",
            "2c1b353c",
            "6b96b141",
            "dbdb2aae",
            "09c8d532",
            "b60f6945",
            "f7c3361f",
            "8aac1cd4",
            "e88d76b8",
            "ab7fb76b",
            "30100120062",
            "30100120063",
            "30100120064",
            "30100120065",
            "cfdec50b",
            "00cfc4b5",
            "be6d88d7",
            "533bd677",
            "5e2c2b86",
            "60f11237",
            "11f86642",
            "2532d766",
            "a114e011",
            "2bc63e8c",
            "6af28561",
            "d7a72717",
            "3888834d",
            "b537ac5e",
            "ae10d8de",
            "85539759",
            "23c16bc3",
            "b37b0f40",
            "1b6aa326",
            "7e292f40",
            "3c536058",
            "64ab16ee",
            "655a1d5a",
            "4024da24",
            "58a07b2e",
            "def4de2a",
            "c9439dd4",
            "e9a1cc09",
            "5250a4db",
            "52bd4167",
            "4184cce6",
            "7e08b105",
            "bb8b2be1",
            "c940acc7",
            "a7dd0c34",
            "883686bd",
            "72cb9845",
            "1ac67e23",
            "3e28f927",
            "20b99c4c",
            "9f02c496",
            "5a837c3a",
            "7b75cd95",
            "fbeb23cd",
            "ccbda122",
            "742b9e81",
            "de4a889d",
            "d3d38652",
            "5c56076b",
            "bae7171f",
            "70761d8f",
            "381113d5",
            "ebb714b7",
            "f72e7cac",
            "d1258bdd",
            "0267025e",
            "b9ec456a",
            "2f8d8cdc",
            "a73bc165",
            "64f5fd5c",
            "35e77c01",
            "df309fe5",
            "61b61c19",
            "74ba5e54",
            "9773b0b8",
            "67d7614b",
            "0d2d8cbe",
            "dec6318b",
            "a19eb90e",
            "e7487531",
            "6b5d7531",
            "238dd3fa",
            "84aecd89",
            "26ae3311",
            "d8ada4be",
            "ad90426d",
            "d4f2a06a"

        ],
        "type": "all",
        "ms": 200000,
        "count": 10
    }

    url1 = "http://e.ai:8083/latest-service/sensor/recently/query"

    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res1 = requests.post(url=url1, data=json.dumps(data), headers=headers)  # 调用数据
    data0 = res1.text
    # print("data0=", data0)
    return data0


data1 = sanbi()
list_dict = json.loads(data1)
# print(list_dict)
list1 = list_dict['data']
print(list1)
# print(list1[0])
# c = list1[0]
# d = c['datas']
# print(d)
# print(d[0])
# print(d[1])
# # e = d[0]
# f = e['timeID']
# g = e['v']
# print(f)
# print(g)
# print(list1[0])
# print(len(list1))

a = np.array(['timeID','EID','v',])


n = 0
m = 0
for i in range(len(list1)):
    b = list1[n]
    d = b['datas']
    # print(len(d[n]))
    # print(d)
    for i in range(len(d)):
        e = d[m]
        c = np.row_stack((a,[e['timeID'],b['Eid'],e['v']]))
        a = c
        m += 1
    # print(b['Eid'])
    n += 1
    m = 0
print(c)