import requests
import time

from backend.wallet.wallet import Wallet

HOME = 'http://localhost:5000'

def fetch_blockchain():
    return requests.get(f'{HOME}/blockchain').json()

def fetch_the_mining_method():
    return requests.get(f'{HOME}/blockchain/mine').json()

def post_for_wallet_transactions(recipient, amount):
    return requests.post(
        f'{HOME}/wallet/transact',
        json={'recipient': recipient, 'amount': amount}
        ).json()

def fetch_wallet_info():
    return requests.get(f'{HOME}/wallet/info').json()

commence_blockchain = fetch_blockchain()
print(f'start_blockchain: {commence_blockchain}')

recipient = Wallet().address
post_transaction_1 = post_for_wallet_transactions(recipient, 25)
print(f'\n 1st Wallet Transaction 1: {post_transaction_1}')

time.sleep(1)
post_transaction_2 = post_for_wallet_transactions(recipient, 15)
print(f'\n 2nd Wallet Transaction 2: {post_transaction_2}')

time.sleep(1)
the_mined_block = fetch_the_mining_method()
print(f'\ The Mined Block: {the_mined_block}')

wallet_info = fetch_wallet_info()
print(f'\n The Wallet Info: {wallet_info}')

