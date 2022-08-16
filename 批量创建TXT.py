# 创建一个txt文件，文件名为mytxtfile,并向文件写入msg
def text_create(name):
    desktop_path = "D:\轧钢厂数据采集点位\数据中台数据字典整理\数据整理1\西门子交流数据\全流程\\"  # 新创建的txt文件的存放路径
    full_path = desktop_path + name + '.txt'  # 也可以创建一个.doc的word文档
    file = open(full_path, 'w')
    #file.write(msg)  # msg也就是下面的Hello world!
    # file.close()

dict1 = [ede2b961,0b7fa433,0b3187f1,265a6509
3b93a86a
f4e97339
aaeca8a8
e7e588f0
35297c30
a9a815f9
c4053444
7122896f
1325f51c
070cd895
060dc2cd
7e292f40
3c536058
1b6aa326
30100120064
90077214
e88d76b8
ab7fb76b
016b4a74
05e6742d
09b2dc53
0e265e73
1114afbb
13304517
19f71256
202b9816
228f0b7a
2f612f25
30733538
31a09b2b
32f129cb
358d4bf7
3880489d
3b581e5d
3d723df3
440200a2
4a30e83a
4d1d2e64
5762e43d
5fdb1213
5ff911f3
63821adc
6672a324
74258211
80fa1286
813eb0c0
83462f93
8e973abc
927d78fa
99b33c98
aeb40393
b4795206
cb9a7def
d301635f
d3ee3f14
dd41477c
f2b7b640
fec7a68b
]

#批量建立TXT以t开头的
for i in range(1,70):
    if i<10:
        m = str(i)
    else:
        m = str(i)
    name="point"+str(m)
    print("data=", name)
    text_create(name)
# 调用函数创建一个名为mytxtfile的.txt文件，并向其写入Hello world!
