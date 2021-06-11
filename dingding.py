# -*- coding:utf-8 -*-
import requests
import json
import csv
from netValue import *

url = f'''https://oapi.dingtalk.com/robot/send?access_token=6150bdd7b72bca8ca2c6f43dd1d128e537da0980288a3c94b4d3cb78147f5972'''
alert_profit = 1000
access_token= f'''6150bdd7b72bca8ca2c6f43dd1d128e537da0980288a3c94b4d3cb78147f5972'''

def send_dingding(access_token, address, amount, is_at=False):
    # access_token = "xx" # access_token 【每个群的每个机器人都不一样】
    url = f"""https://oapi.dingtalk.com/robot/send?access_token={access_token }"""
    # 构建请求头部
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }

    alert_text = "Unusal activity: account address at "
    msg = {
     "msgtype": "markdown",
     "markdown": {
         "title":"交易异常报警",
         "text": alert_text + address +  " has gained profit of " + str(amount) + " BUSD"
     }
 }
    if is_at:
        msg['at'] = {
            "atMobiles": [
                "17368735729", # mobile
            ],
            "isAtAll": False
        }
    # 对请求的数据进行json封装
    message_json = json.dumps(msg)
    try:
        res = requests.post(url=url, data=message_json, headers=header).json()
    except Exception as e:
        print(e)
    if res["errcode"] == 0:
        print("发送钉钉成功！")
    else:
        print("发送钉钉成功!")


if __name__ == "__main__":
    file = open("test-state.json")
    trades = json.load(file)
    trades = trades["blocks"]
    getNetValues(trades)
    print(netValues)
    for account in netValues:
        if netValues[account][5]>alert_profit:
            send_dingding(access_token, account, netValues[account][5], is_at=False)
        else:
            continue







