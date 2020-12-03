import pytest

from backend.blockchain.blockchain import Blockchain
from backend.wallet.wallet import Wallet
from backend.wallet.transactions import SystemTransactions
from backend.blockchain.block import THE_GENESIS_BLOCK_DATA

def test_for_blockchain_instance():
    blockchain = Blockchain()

    assert blockchain.chain[0].hash == THE_GENESIS_BLOCK_DATA['hash']

def test_for_add_block():
    blockchain = Blockchain()
    data = 'test-data'
    blockchain.add_block(data)

    assert blockchain.chain[-1].data == data

@pytest.fixture
def three_block_blockchain():
    blockchain = Blockchain()
    for i in range(3):
        blockchain.add_block([SystemTransactions(Wallet(), 'recipient', i).convert_transaction_data_to_json()])
    return blockchain

def test_if_chain_is_valid(three_block_blockchain):
    Blockchain.chain_is_valid(three_block_blockchain.chain)

def test_for_bad_genesis_in_valid_chain(three_block_blockchain):
    three_block_blockchain.chain[0].hash = 'bad_hash'

    with pytest.raises(Exception, match = 'Genesis Block Must Be Valid'):
        Blockchain.chain_is_valid(three_block_blockchain.chain)#

def test_for_replacing_chain(three_block_blockchain):
    blockchain = Blockchain()
    blockchain.replace_the_chain(three_block_blockchain.chain)

    assert blockchain.chain == three_block_blockchain.chain

def test_for_replacing_chain_if_not_longer(three_block_blockchain):
    blockchain = Blockchain()

    with pytest.raises(Exception, match='Incoming chain must be longer'):
        three_block_blockchain.replace_the_chain(blockchain.chain)

def test_for_replacing_chain_if_bad_chain(three_block_blockchain):
    blockchain = Blockchain()
    three_block_blockchain.chain[1].hash = 'bad_hash'

    with pytest.raises(Exception, match='Incoming chain is invalid'):
        blockchain.replace_the_chain(three_block_blockchain.chain)

def test_for_valid_transaction_chain(three_block_blockchain):
    Blockchain.transaction_chain_is_valid(three_block_blockchain.chain)

def test_for_duplicate_transactions_in_is_valid_transaction_chain(three_block_blockchain):
    transaction = SystemTransactions(Wallet(), 'recipient', 1).convert_transaction_data_to_json()
    three_block_blockchain.add_block([transaction, transaction])

    with pytest.raises(Exception, match='is not unique'):
        Blockchain.transaction_chain_is_valid(three_block_blockchain.chain)

def test_for__multiple_rewards_in_is_valid_transaction_chain(three_block_blockchain):
    reward_1 = SystemTransactions.transaction_reward_generation(Wallet()).convert_transaction_data_to_json()
    reward_2 = SystemTransactions.transaction_reward_generation(Wallet()).convert_transaction_data_to_json()
    three_block_blockchain.add_block([reward_1, reward_2])

    with pytest.raises(Exception, match='There can only be one mining reward given per block'):
        Blockchain.transaction_chain_is_valid(three_block_blockchain.chain)

def test_for_bad_transaction_in_is_valid_transaction_chain(three_block_blockchain):
    bad_transaction = SystemTransactions(Wallet(), 'recipient', 1)
    bad_transaction.transaction_input['signature'] = Wallet().signature_generation(
        bad_transaction.transaction_output)
    three_block_blockchain.add_block([bad_transaction.convert_transaction_data_to_json()])

    with pytest.raises(Exception):
        Blockchain.transaction_chain_is_valid(three_block_blockchain.chain)

def test_for_bad_historic_balance_in_is_valid_transaction_chain(three_block_blockchain):
    wallet = Wallet()
    bad_transaction = SystemTransactions(wallet, 'recipient', 1)
    bad_transaction.transaction_output[wallet.address] = 9000
    bad_transaction.transaction_input['amount'] = 9001
    bad_transaction.transaction_input['signature'] = wallet.signature_generation(bad_transaction.transaction_output)

    three_block_blockchain.add_block([bad_transaction.convert_transaction_data_to_json()])

    with pytest.raises(Exception, match='has an invalid input amount'):
        Blockchain.transaction_chain_is_valid(three_block_blockchain.chain)