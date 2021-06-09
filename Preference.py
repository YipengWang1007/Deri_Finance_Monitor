import os
import json
import logging
from decimal import Decimal

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler('Logs.log')
    ]
)

DIR_DATA = 'Data'
DIR_ABIS = 'Abis'
os.makedirs(DIR_DATA, exist_ok=True)
os.makedirs(DIR_ABIS, exist_ok=True)

ONE = 10**18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

CHAINIDS = {
    'ethereum':     1,
    'bsc':          56,
    'heco':         128,
    'ropsten':      3,
    'kovan':        42,
    'bsctestnet':   97,
    'hecotestnet':  256,
}

RPCS = {
    'ethereum': [
        'https://mainnet.infura.io/v3/be8f2596352a4ea2986472ec46f5c6e1',
        'https://mainnet.infura.io/v3/2ded4661ec3d4e6f9bb1c9a27a160436',
    ],
    'bsc': [
        'https://bsc-dataseed.binance.org/',
        'https://bsc-dataseed1.defibit.io/',
        'https://bsc-dataseed1.ninicoin.io/',
    ],
    'heco': [
        'https://http-mainnet.hecochain.com',
    ],
    'ropsten': [
        'https://ropsten.infura.io/v3/be8f2596352a4ea2986472ec46f5c6e1',
        'https://ropsten.infura.io/v3/2ded4661ec3d4e6f9bb1c9a27a160436',
    ],
    'kovan': [
        'https://kovan.infura.io/v3/be8f2596352a4ea2986472ec46f5c6e1',
        'https://kovan.infura.io/v3/2ded4661ec3d4e6f9bb1c9a27a160436',
    ],
    'bsctestnet': [
        'https://data-seed-prebsc-1-s1.binance.org:8545/',
        'https://data-seed-prebsc-2-s1.binance.org:8545/',
        'https://data-seed-prebsc-1-s2.binance.org:8545/',
        'https://data-seed-prebsc-2-s2.binance.org:8545/',
        'https://data-seed-prebsc-1-s3.binance.org:8545/',
        'https://data-seed-prebsc-2-s3.binance.org:8545/',
    ],
    'hecotestnet': [
        'https://http-testnet.hecochain.com',
    ]
}
