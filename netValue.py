import json
import csv
import math
from tqdm import tqdm

trades = {} #store part of a json dictionary for convinient key hashing
netValues = {} #dictionary of pairs of owner:netValue (in stable coin values)
profits = {}
multiplier  = 10**18 #used as divisor to retrieve real trade values 

#netValues structure: {owner:(totalValue, BTCValue, BTCVolume, ETHValue, ETHVolume, profit)} *values all in stable coin unit
def updateNetValues(trade):
    #either create trader netvalue info or update it if existed
    if trade[0] not in netValues:
        netValues[trade[0]] = [trade[2] * trade[3],0,0,0,0,0]
        if trade[1]== 0:#update account BTC value
            netValues[trade[0]][1] = trade[2] * trade[3]
            netValues[trade[0]][2] = trade[2]
        elif trade[1]== 1:#update account ETH value
            netValues[trade[0]][3] = trade[2] * trade[3]
            netValues[trade[0]][4] = trade[2]
    else:
        if trade[1]== 0: #BTC 
            #same direction order modifies values but creates no profit change
            if trade[2] * netValues[trade[0]][2]>=0:
                netValues[trade[0]][1] += trade[2] * trade[3]
                netValues[trade[0]][2] += trade[2]
                netValues[trade[0]][0] += trade[2] * trade[3]

            #opposite direction order creates profits change
            elif trade[2] * netValues[trade[0]][2]<0:
                averagePrice = netValues[trade[0]][1]/netValues[trade[0]][2]
                if trade[2]<0: #short order on long position
              
                    if netValues[trade[0]][2]< abs(trade[2]): #position switched
                        netValues[trade[0]][5] += (trade[3] - averagePrice)* netValues[trade[0]][2]

                        
                        netValues[trade[0]][1] = (trade[2]+ netValues[trade[0]][2])* trade[3]
                        netValues[trade[0]][2] += trade[2]

                    else: #maintain original position status or make a clearance
                        netValues[trade[0]][5] -= (trade[3] - averagePrice)* trade[2]
                        netValues[trade[0]][2] += trade[2]
                        netValues[trade[0]][1] = averagePrice * netValues[trade[0]][2]

                elif trade[2]>0: #long order on short positions 

                    if abs(netValues[trade[0]][2])< trade[2]: #position switched
                        netValues[trade[0]][5] += (trade[3] - averagePrice)* netValues[trade[0]][2]
                        netValues[trade[0]][1] = (trade[2]+ netValues[trade[0]][2])* trade[3]
                        netValues[trade[0]][2] += trade[2]
                    else: #maintain original position status or make a clearance
                        netValues[trade[0]][5] -= (trade[3] - averagePrice)* trade[2]
                        netValues[trade[0]][2] += trade[2]
                        netValues[trade[0]][1] = averagePrice * netValues[trade[0]][2]

                #update total values
                netValues[trade[0]][0] = netValues[trade[0]][1] * netValues[trade[0]][2] + netValues[trade[0]][3] * netValues[trade[0]][4]
                

        elif trade[1]== 1: #ETH
            #same direction order modifies values but creates no profit change
            if trade[2] * netValues[trade[0]][4]>=0:
                netValues[trade[0]][3] += trade[2] * trade[3]
                netValues[trade[0]][4] += trade[2]
                netValues[trade[0]][0] += trade[2] * trade[3]

            #opposite direction order creates profits change
            elif trade[2] * netValues[trade[0]][4]<0:
                averagePrice = netValues[trade[0]][3]/netValues[trade[0]][4]
                if trade[2]<0: #short order on long position
              
                    if netValues[trade[0]][4]< abs(trade[2]): #position switched
                        netValues[trade[0]][5] += (trade[3] - averagePrice)* netValues[trade[0]][4]
                        netValues[trade[0]][3] = (trade[2]+ netValues[trade[0]][4])* trade[3]
                        netValues[trade[0]][4] += trade[2]
                    else: #maintain original position status or make a clearance
                        netValues[trade[0]][5] -= (trade[3] - averagePrice)* trade[2]
                        netValues[trade[0]][4] += trade[2]
                        netValues[trade[0]][3] = averagePrice * netValues[trade[0]][4]

                elif trade[2]>0: #long order on short positions 

                    if abs(netValues[trade[0]][4])< trade[2]: #position switched
                        netValues[trade[0]][5] += (trade[3] - averagePrice)* netValues[trade[0]][4]
                        netValues[trade[0]][3] = (trade[2]+ netValues[trade[0]][4])* trade[3]
                        netValues[trade[0]][4] += trade[2]
                    else: #maintain original position status or make a clearance
                        netValues[trade[0]][5] -= (trade[3] - averagePrice)* trade[2]
                        netValues[trade[0]][4] += trade[2]
                        netValues[trade[0]][3] = averagePrice * netValues[trade[0]][4]

                #update other values
                netValues[trade[0]][0] = netValues[trade[0]][1] * netValues[trade[0]][2] + netValues[trade[0]][3] * netValues[trade[0]][4]

 


def getNetValues(trades):
    #loops does not increase runtime here, constant time to getItem due to json file structure
    for blockNumber in trades:
        for address in trades[blockNumber]:
            for tradeHash in trades[blockNumber][address]:
                #trade information dictionary
                tradeInfo = trades[blockNumber][address][tradeHash]
                owner = tradeInfo["owner"]
                symbol = tradeInfo["symbol id"]
                volume = tradeInfo["trade volume"]/multiplier
                price = tradeInfo["price"]/multiplier
                time = tradeInfo["timestamp"]
                trade = (owner, symbol, volume, price, time)
                print(trade)
                updateNetValues(trade)
                


if __name__ == "__main__":
    file = open("test-state.json")
    trades = json.load(file)
    trades = trades["blocks"]
    getNetValues(trades)
    print(netValues)

    
    output = open("output.csv","w")
    writer = csv.writer(output)
    writer.writerow(["account address","总仓位成本","BTC建仓成本","BTC仓位","ETH建仓成本", "ETH仓位", "利润"])
    for account in netValues:
        writer.writerow([account] + netValues[account])

    file.close()
    output.close()
  