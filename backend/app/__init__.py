import os
import requests
import random

from flask import Flask, jsonify, request

from backend.blockchain.blockchain import Blockchain
from backend.wallet.transactions import SystemTransactions
from backend.wallet.wallet import Wallet
from backend.wallet.transaction_pool import TransactionPool
from backend.pubsub import PubSub

app = Flask(__name__)
blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

@app.route('/')
def default():
    return 'Welcome to the Blockchain'

@app.route('/blockchain')
def blockchain_route():
    return jsonify(blockchain.convert_blockchain_list_to_json())

@app.route('/blockchain/mine')
def blockchain_mine_route():
    transaction_data = transaction_pool.transaction_of_data()
    transaction_data.append(SystemTransactions.transaction_reward_generation(wallet).convert_transaction_data_to_json())
    
    blockchain.add_block(transaction_data)
    block = blockchain.chain[-1]
    pubsub.block_broadcast(block)
    transaction_pool.clear_the_blockchain_transactions(blockchain)

    return jsonify(block.convert_block_to_json())

@app.route('/wallet/transact', methods=['POST'])
def wallet_transactions_route():
    transaction_data = request.get_json()
    transaction = transaction_pool.existing_transaction(wallet.address)
    if transaction:
        transaction.transaction_update(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )
    else:   
        transaction = SystemTransactions(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )

    pubsub.broadcast_transaction(transaction)
    return jsonify(transaction.convert_transaction_data_to_json())

@app.route('/wallet/info')
def wallet_route_info():
    return jsonify({'address': wallet.address, 'balance': wallet.the_true_balance})

ROOT_PORT = 5000
PORT = ROOT_PORT

if os.environ.get('PEER') == 'True':
    PORT = random.randint(5001, 6000)
    
    result_of_request = requests.get(f'http://localhost:{ROOT_PORT}/blockchain')
    result_of_blockchain_req = Blockchain.convert_blocklist_to_chain_from_json(result_of_request.json())
    
    try:
        blockchain.replace_the_chain(result_of_blockchain_req.chain)
        print('\n -- The local chain has been successfully synchronized ')
    except Exception as e:
        print(f'\n -- Error synrchronizing: {e}')
    

app.run(port=PORT)