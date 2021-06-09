import time
import json
import random
import logging
import traceback
import multiprocessing.pool as mpp
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware, local_filter_middleware
from Preference import *


ABIS = {}


def getWeb3(network):
    web3 = Web3(Web3.HTTPProvider(random.choice(RPCS[network])))
    if 'bsc' in network or 'heco' in network:
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        web3.middleware_onion.add(local_filter_middleware)
    web3.network = network
    return web3


def getAbi(abiName):
    global ABIS
    if abiName in ABIS: return ABIS[abiName]
    with open(f'{DIR_ABIS}/{abiName}.json') as file:
        interface = json.load(file)
    ABIS[abiName] = interface['abi']
    return ABIS[abiName]


def getContract(network, address, abiName):
    web3 = getWeb3(network)
    contract = web3.eth.contract(address=address, abi=getAbi(abiName))
    return contract


def getBlock(network, number='latest'):
    web3 = getWeb3(network)
    block = web3.eth.getBlock(number)
    return block


def getBlocks(network, numbers, threads=10):
    if not numbers: return []
    web3 = getWeb3(network)
    pool = mpp.ThreadPool(threads)
    res = pool.map(web3.eth.getBlock, numbers)
    return res


def getEvents(network, address, abiName, eventName, fromBlock, toBlock, argumentFilters=None, period=5000, threads=10):
    if fromBlock > toBlock: return []
    contract = getContract(network, address, abiName)
    periods = [(fromBlock + i * period, min(fromBlock + (i+1) * period - 1, toBlock)) for i in range((toBlock - fromBlock) // period + 1)]
    if len(periods) == 1:
        eventFilter = contract.events[eventName].createFilter(fromBlock=fromBlock, toBlock=toBlock, argument_filters=argumentFilters)
        events = eventFilter.get_all_entries()
    else:
        pool = mpp.ThreadPool(threads)
        def query(n1, n2):
            eventFilter = contract.events[eventName].createFilter(fromBlock=n1, toBlock=n2, argument_filters=argumentFilters)
            return eventFilter.get_all_entries()
        events = pool.starmap(query, periods)
        events = [a for b in events for a in b]
    return events


def call(network, address, abiName, functionName, params=None):
    contract = getContract(network, address, abiName)
    if params is None: params = []
    return contract.functions[functionName](*params).call()


# details = [(network, address, abiName, functionName, params)...]
def multicall(details, threads=10):
    pool = mpp.ThreadPool(threads)
    return pool.starmap(call, details)


def batchCall(network, address, abiName, functionName, structList, batch=200):
    if not structList: return []
    batchs = (len(structList) - 1) // batch + 1
    details = [(network, address, abiName, functionName, [structList[i*batch:(i+1)*batch]]) for i in range(batchs)]
    values = multicall(details)
    values = [a for b in values for a in b]
    return values


def transact(network, address, abiName, functionName, params, account, private, gas=6000000, gasPrice=22000000000):
    contract = getContract(network, address, abiName)
    tx = contract.functions[functionName](*params).buildTransaction({
        'nonce': contract.web3.eth.getTransactionCount(account),
        'from': account,
        'gas': gas,
        'gasPrice': gasPrice
    })
    signedTx = contract.web3.eth.account.signTransaction(tx, private)
    txHash = contract.web3.eth.sendRawTransaction(signedTx.rawTransaction)
    receipt = contract.web3.eth.waitForTransactionReceipt(txHash)
    return receipt


def batchTransact(network, address, abiName, functionName, structList, account, private, gas=6000000, gasPrice=22000000000, batch=100):
    receipts = []
    batchs = (len(structList) - 1) // batch + 1
    for i in range(batchs):
        for n in range(3):
            try:
                receipt = transact(network, address, abiName, functionName, [structList[i*batch:(i+1)*batch]],
                                   account, private, gas=gas, gasPrice=gasPrice)
                if receipt.status:
                    receipts.append(receipt)
                    logging.info(f'Database batch transaction {i+1}/{batchs}: ({receipt.transactionHash.hex()}, {receipt.status})')
                    break
                else:
                    logging.info(f'Database batch transaction {i+1}/{batchs}: ({receipt.transactionHash.hex()}, {receipt.status})')
            except:
                logging.error(f'Database batch transaction {i+1}/{batchs}: {traceback.format_exc()}')
            time.sleep(5)
    return receipts
