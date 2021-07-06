# -*- coding:utf-8 -*-
import requests
import json
import csv

url = f'''https://oapi.dingtalk.com/robot/send?access_token=6150bdd7b72bca8ca2c6f43dd1d128e537da0980288a3c94b4d3cb78147f5972'''
alert_profit = 1000
access_token= f'''6150bdd7b72bca8ca2c6f43dd1d128e537da0980288a3c94b4d3cb78147f5972'''

def send_dingding(access_token, address, amount, is_at=False):
    url = f"""https://oapi.dingtalk.com/robot/send?access_token={access_token}"""
    # define request header
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }

    alert_text = "Unusual activity: account address at "
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
    # convert requested message to json structure
    message_json = json.dumps(msg)
    try:
        res = requests.post(url=url, data=message_json, headers=header).json()
    except Exception as e:
        print(e)
    if res["errcode"] == 0:
        print("发送钉钉成功！")
    else:
        print("发送钉钉成功!")

def alert():
    file = open("trade_history.json")
    trades = json.load(file)
    trades = trades["blocks"]
    getNetValues(trades)
    print(netValues)
    for account in netValues:
        if netValues[account][5]>alert_profit:
            send_dingding(access_token, account, netValues[account][5], is_at=False)
        else:
            continue

if __name__ == "__main__":
    alert()
    







