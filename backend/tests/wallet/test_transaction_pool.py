from backend.wallet.transaction_pool import TransactionPool
from backend.wallet.transactions import SystemTransactions
from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain
# from backend.blockchain.blockchain import Blockchain

def test_set_transaction():
    transaction_pool = TransactionPool()
    transaction = SystemTransactions(Wallet(), 'recipient', 1)
    transaction_pool.setting_the_trasaction(transaction)

    assert transaction_pool.map_of_transactions[transaction.id] == transaction

def test_clear_blockchain_transactions():
    transaction_pool = TransactionPool()
    transac_number_1 = SystemTransactions(Wallet(), 'recipient', 1)
    transac_number_2 = SystemTransactions(Wallet(), 'recipient', 2)

    transaction_pool.setting_the_trasaction(transac_number_1)
    transaction_pool.setting_the_trasaction(transac_number_2)

    blockchain = Blockchain()
    blockchain.add_block([transac_number_1.convert_transaction_data_to_json(), transac_number_2.convert_transaction_data_to_json()])

    assert transac_number_1.id in transaction_pool.map_of_transactions
    assert transac_number_2.id in transaction_pool.map_of_transactions    

    transaction_pool.clear_the_blockchain_transactions(blockchain)

    assert not transac_number_1.id in transaction_pool.map_of_transactions
    assert not transac_number_2.id in transaction_pool.map_of_transactions 