import json
import csv
import time
import math
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime, timedelta

#dictionaries to store events data
marginRatioData = {}
addMargin = {}
removeMargin = {}
trades = {}
liquidate = {}

#store all addresses that participated in trading
addresses = []

#api to get prices of BTC and ETH
import requests
TICKER_API_URL = "https://api.bittrex.com/api/v1.1/public/getticker?market="


def getMarginHistory(ad, addMargin, removeMargin, trades, liquidate):
    output = open(ad+"_Margin.csv" ,"w", newline ='')
    writer = csv.writer(output)
    #get add marigin history
    for blockNumber in addMargin:
        for address in addMargin[blockNumber]:
            for tradeHash in addMargin[blockNumber][address]:
                addMarginInfo = addMargin[blockNumber][address][tradeHash]
                owner = addMarginInfo["owner"]
                if owner == ad:
                    time = addMarginInfo["timestamp"]
                    bTokenId = addMarginInfo["bTokenId"]
                    bAmount = addMarginInfo["bAmount"]/(10**18)
                    aM = ["addMargin",owner, time, bTokenId,bAmount]
                    writer.writerow(aM)

    #get remove margin history
    for blockNumber in removeMargin:
        for address in removeMargin[blockNumber]:
            for tradeHash in removeMargin[blockNumber][address]:
                removeMarginInfo = removeMargin[blockNumber][address][tradeHash]
                owner = removeMarginInfo["owner"]
                if owner == ad:
                    time = removeMarginInfo["timestamp"]
                    bTokenId = removeMarginInfo["bTokenId"]
                    bAmount = removeMarginInfo["bAmount"]/(10**18)
                    rM = ["removeMargin",owner, time, bTokenId,-bAmount]
                    writer.writerow(rM)

    for blockNumber in trades:
        for address in trades[blockNumber]:
            for tradeHash in trades[blockNumber][address]:
                tradeInfo = trades[blockNumber][address][tradeHash]
                owner = tradeInfo["owner"]
                if owner == ad:
                    symbol = tradeInfo["symbol id"]
                    m = 0.0001 if symbol ==0 else 0.001
                    volume = tradeInfo["trade volume"]/(10**18)
                    price = tradeInfo["price"]/(10**18)
                    time = tradeInfo["timestamp"]
                    direction = 'long' if volume >0 else 'short'
                    trade = ["trade",owner, time, price, volume, abs(volume)*price* m * 0.001]
                    writer.writerow(trade)

    for blockNumber in liquidate:
        for address in liquidate[blockNumber]:
            for tradeHash in liquidate[blockNumber][address]:
                liquidateInfo = liquidate[blockNumber][address][tradeHash]
                owner = liquidateInfo["owner"]
                if owner == ad:
                    time = liquidateInfo["timestamp"]
                    reward = liquidateInfo["reward"]/(10**18)
                    liquidator = liquidateInfo["liquidator"]
                    li = ["liquidate",owner, time, liquidator,reward]
                    writer.writerow(li)
    output.close()

def sortByTimestamp(ad):
    with open(ad+"_Margin.csv") as data:
        reader = csv.reader(data,delimiter = ",")
        output = sorted(reader, key = lambda t: datetime.strptime(t[2], "%Y-%m-%dT%H:%M:%S"))
    with open(ad+"_Events.csv", mode='w',newline = "") as file:
        writer = csv.writer(file, delimiter=',')
        for event in output:
            writer.writerow(event)

def getInfo(ad,dailyInfo):
    # info format: [address, totalCost, BTCPrice, BTCVolume, ETHPrice, ETHVolume, PnL, margin, marginRatio]
    # daily info format: [timestamp, #Trades, tradeAmount, #liquidate, liquidateReward, maxP, maxL]
    info = [ad,0,0,0,0,0,0,0,0,"",0]
    events = []
    with open(ad+"_Events.csv","r") as data:
        reader = csv.reader(data,delimiter = ",")
        for row in reader:
            events.append(row)

    output = open("MarginRatio.csv" ,"a+", newline ='')
    writer = csv.writer(output)
    writer.writerow(["address", "totalCost", "BTCPrice", "BTCVolume", "ETHPrice", "ETHVolume", "PnL", "margin", "marginRatio","timestamp","unrealized PnL"])
    liquidation_amount = 0;
    for event in events:
        info[9] = event[2]
        if event[0]=="addMargin":
            info[7]+=float(event[4])
            if info[1]!=0:
                info[8]= (info[7]+info[6]+ liquidation_amount)/info[1]
            else:
                info[8]=0;
        elif event[0]=="removeMargin":
            info[7]+=float(event[4])
            if info[1]!=0:
                info[8]= (info[7]+info[6]+ liquidation_amount)/info[1]
            else:
                info[8]=0;
        elif event[0]=="trade":
            timestamp = datetime.strptime(event[2],"%Y-%m-%dT%H:%M:%S")
            print(timestamp)
            print(datetime.now() - timedelta(hours=36) <= timestamp)
            if datetime.now() - timedelta(hours=36)<= timestamp:
                dailyInfo[1]+=1
            
            #ETHUSD
            if float(event[3])<10000:
                if datetime.now() -timedelta(hours=36) <= timestamp:
                    dailyInfo[2]+= abs(float(event[3])*float(event[4])*0.001)
                #原先持有多仓
                if info[5]>0:
                    #加仓
                    if float(event[4])>0:
                        oldPrice = info[4]
                        newPrice = (info[4]*info[5] + float(event[3])*float(event[4])) / (info[5]+ float(event[4]))
                        #修改持仓量和平均持仓价格
                        info[5]+= float(event[4])
                        info[4]= newPrice
                        #产生浮盈浮亏
                        info[6]+= (newPrice-oldPrice)*info[5]*0.001
                        #修改总持仓
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)

                    #平仓
                    elif float(event[4])<0:
                        oldPrice = info[4]
                        oldVolume = info[5]
                        profit = 0;
                        #未完全平仓
                        if float(event[4])+ oldVolume >0:
                            info[5]= float(event[4])+ oldVolume
                            info[6]+= (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001
                            profit = (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001
                        #完全平仓或者反转仓位
                        else:
                            info[5] = float(event[4])+ oldVolume
                            if float(event[4])+ oldVolume==0:
                                info[4]=0;
                            else:
                                info[4] = float(event[3])
                            info[6]+= (float(event[3])-oldPrice)*oldVolume*0.001
                            profit = (float(event[3])-oldPrice)*oldVolume*0.001

                        if datetime.now() -timedelta(hours=36) <= timestamp:
                            if profit> dailyInfo[5]:
                                dailyInfo[5]=profit
                            elif profit <dailyInfo[6]:
                                dailyInfo[6]=profit
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)
                #原先持有空仓
                elif info[5]<0:
                    #加仓
                    if float(event[4])<0:
                        oldPrice = info[4]
                        newPrice = (info[4]*info[5] + float(event[3])*float(event[4])) / (info[5]+ float(event[4]))
                        #修改持仓量和平均持仓价格
                        info[5]+= float(event[4])
                        info[4]= newPrice
                        #产生浮盈浮亏
                        info[6]+= (newPrice-oldPrice)*info[5]*0.001
                        #修改总持仓
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)
                    #平仓
                    elif float(event[4])>0:
                        oldPrice = info[4]
                        oldVolume = info[5]
                        #未完全平仓
                        if float(event[4])+ oldVolume <0:
                            info[5]= float(event[4])+ oldVolume
                            info[6]+= (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001
                            if datetime.now() -timedelta(hours=36) <= timestamp:
                                if dailyInfo[5]< (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001:
                                    dailyInfo[5] = (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001;
                                elif dailyInfo[6]> (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001:
                                    dailyInfo[6] = (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.001
                        #完全平仓或者反转仓位
                        else:
                            info[5] = float(event[4])+ oldVolume
                            if float(event[4])+ oldVolume==0:
                                info[4]=0;
                            else:
                                info[4] = float(event[3])
                            info[6]+= (float(event[3])-oldPrice)*oldVolume*0.001
                            if datetime.now() -timedelta(hours=36) <= timestamp:
                                if dailyInfo[5]< (float(event[3])-oldPrice)*oldVolume*0.001:
                                    dailyInfo[5] = (float(event[3])-oldPrice)*oldVolume*0.001
                                elif dailyInfo[6]> (float(event[3])-oldPrice)*oldVolume*0.001:
                                    dailyInfo[6] = (float(event[3])-oldPrice)*oldVolume*0.001
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)

                #原先不持仓该币种
                elif info[5]==0:
                    price = float(event[3])
                    volume = float(event[4])
                    info[4]+= price
                    info[5]+= volume
                    info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)


            #BTCUSD
            else:
                if datetime.now() -timedelta(hours=36) <= timestamp:
                    dailyInfo[2]+= abs(float(event[3])*float(event[4])*0.0001)
                #原先持有多仓
                if info[3]>0:
                    #加仓
                    if float(event[4])>0:
                        oldPrice = info[2]
                        newPrice = (info[2]*info[3] + float(event[3])*float(event[4])) / (info[3]+float(event[4]))
                        #修改持仓量和平均持仓价格
                        info[3]+= float(event[4])
                        info[2]= newPrice
                        #产生浮盈浮亏
                        info[6]+= (newPrice-oldPrice)*info[3]*0.0001
                        #修改总持仓
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)

                    #平仓
                    elif float(event[4])<0:
                        oldPrice = info[2]
                        oldVolume = info[3]
                        profit = 0;
                        #未完全平仓
                        if float(event[4])+ oldVolume >0:
                            info[3]= float(event[4])+ oldVolume
                            profit = (float(event[3])-oldPrice)*(oldVolume + float(event[4]))*0.0001
                        #完全平仓或者反转仓位
                        else:
                            info[3] = float(event[4])+ oldVolume
                            if float(event[4])+ oldVolume==0:
                                info[2]=0;
                            else:
                                info[2] = float(event[3])
                            profit = (float(event[3])-oldPrice)*oldVolume*0.0001
                        info[6]+= profit
                        if datetime.now() -timedelta(hours=36) <= timestamp:
                            if profit> dailyInfo[5]:
                                dailyInfo[5]=profit
                            elif profit <dailyInfo[6]:
                                dailyInfo[6]=profit

                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)
                #原先持有空仓
                elif info[3]<0:
                    #加仓
                    if float(event[4])<0:
                        oldPrice = info[2]
                        newPrice = (info[2]*info[3] + float(event[3])*float(event[4])) / (info[3]+ float(event[4]))
                        #修改持仓量和平均持仓价格
                        info[3]+= float(event[4])
                        info[2]= newPrice
                        #产生浮盈浮亏
                        info[6]+= (newPrice-oldPrice)*info[3]*0.0001
                        #修改总持仓
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)
                    #平仓
                    elif float(event[4])>0:
                        oldPrice = info[2]
                        oldVolume = info[3]
                        profit = 0;
                        #未完全平仓
                        if float(event[4])+ oldVolume <0:
                            info[3]= float(event[4])+ oldVolume
                            info[6]+= (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.0001
                            profit = (float(event[3])-oldPrice) * (oldVolume + float(event[4]))*0.0001
                        #完全平仓或者反转仓位
                        else:
                            info[3] = float(event[4])+ oldVolume
                            if float(event[4])+ oldVolume==0:
                                info[2]=0;
                            else:
                                info[2] = float(event[3])
                            info[6]+= (float(event[3])-oldPrice)* oldVolume *0.0001
                            profit = (float(event[3])-oldPrice)* oldVolume *0.0001

                        if datetime.now() -timedelta(hours=36) <= timestamp:
                            if profit> dailyInfo[5]:
                                dailyInfo[5]=profit
                            elif profit <dailyInfo[6]:
                                dailyInfo[6]=profit
                        info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)

                #原先不持仓该币种
                elif info[3]==0:
                    price = float(event[3])
                    volume = float(event[4])
                    info[2]+= price
                    info[3]+= volume
                    info[1] = abs(info[2]*info[3]*0.0001) + abs(info[4]*info[5]*0.001)
            if info[1]!=0:
                info[8]= (info[7]+info[6]+ liquidation_amount)/info[1]
            else:
                info[8]=0;


        #爆仓
        elif event[0]=="liquidate":
            if datetime.now() -timedelta(hours=36) <= timestamp <= datetime.now():
                dailyInfo[3]+=1;
                dailyInfo[4]+= float(event[4])
            for i in range(1,6):
                info[i]=0;
            info[6]-=info[7];
            liquidation_amount += info[7]
            info[7]=0;
            info[8]=0;
            
            
        print(info);
        writer.writerow(info)
    return info

def get_latest_crypto_price(crypto):
    url = TICKER_API_URL + crypto
    j = requests.get(url)
    data = json.loads(j.text)
    price = data["result"]["Ask"]
    return price

if __name__ == "__main__":
     dailyInfo = [datetime.now(),0,0,0,0,0,0]

     file = open("add_margin_history.json")
     addMargin = json.load(file)
     addMargin = addMargin["blocks"]
     file.close()

     file = open("remove_margin_history.json")
     removeMargin = json.load(file)
     removeMargin = removeMargin["blocks"]
     file.close()

     file = open("liquidate_history.json")
     liquidate = json.load(file)
     liquidate = liquidate["blocks"]
     file.close()

     file = open("trade_history.json")
     trades = json.load(file)
     trades = trades["blocks"]
     file.close()
     
    

     for blockNumber in trades:
        for address in trades[blockNumber]:
            for tradeHash in trades[blockNumber][address]:
                tradeInfo = trades[blockNumber][address][tradeHash]
                owner = tradeInfo["owner"]
                if owner not in addresses:
                    addresses.append(owner)
     
     file = open("conclusion_info.csv","w",newline="")
     writer = csv.writer(file)
     writer.writerow(['address','totalCost','BTCPrice','BTCVolume','ETHPrice','ETHVolume','realized PnL','margin','marginRatio','timestamp','Unrealized PnL'])

     btc = get_latest_crypto_price("USD-BTC")
     eth = get_latest_crypto_price("USD-ETH")

     for address in addresses:
         getMarginHistory(address, addMargin, removeMargin, trades, liquidate)
         sortByTimestamp(address)
         info = getInfo(address,dailyInfo)

         
         value = abs(info[3]*btc*0.0001) + abs(info[5]*eth*0.001)
         info[10] = (value - info[1])

         writer.writerow(info)

     print(dailyInfo)

