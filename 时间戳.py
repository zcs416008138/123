from gevent import monkey
monkey.patch_all(select=False)
from flask_cors import CORS
import json
import requests
from gevent.pywsgi import WSGIServer
from multiprocessing import cpu_count, Process
from flask import Flask,  request
import time
import datetime





# 从吴工写的接口里面读取中台数据,读取哈轴数据的
def wugonghazhou(eid):
    url = "http://10.6.1.188:8888/dd2/web/data/hzch"  # 吴工的万能接口地址
    data = {"sql": "SELECT * from ha_zhou.data_all where Eid = '"+ eid +"' order by EventTime desc limit 4"}  # 请求的sql语句。
    #print("data=",data)
    headers = {"Content-Type": "application/json"}  # 指定提交的是json格式提交（否则无法读取到）
    res = requests.post(url=url, data=json.dumps(data), headers=headers)  # 调用数据
    #print("result=", res.text)  # 打印出结果
    resu = res.text
    return resu