from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain
from backend.wallet.transactions import SystemTransactions
from backend.config import WALLET_STARTING_BALANCE

def test_to_verify_valid_signature():
    valid_test_data = {'foo' : 'test_data'}
    test_wallet = Wallet()
    wallet_test_signature = test_wallet.signature_generation(valid_test_data)

    assert Wallet.verify_signature(test_wallet.public_key, valid_test_data, wallet_test_signature)


def test_to_verify_invalid_signature():
    invalid_test_data = {'foo': 'test_data'}
    test_wallet = Wallet()
    wallet_test_signature = test_wallet.signature_generation(invalid_test_data)

    
    assert not Wallet.verify_signature(Wallet().public_key, invalid_test_data, wallet_test_signature)

def test_for_calculating_balance():
    blockchain = Blockchain()
    wallet = Wallet()

    assert Wallet.wallet_balance_calculation(blockchain, wallet.address) == WALLET_STARTING_BALANCE

    amount = 55
    transaction = SystemTransactions(wallet, 'recipient', amount)
    blockchain.add_block([transaction.convert_transaction_data_to_json()])

    assert Wallet.wallet_balance_calculation(blockchain, wallet.address) == \
        WALLET_STARTING_BALANCE - amount

    amnt_to_recieve_1 = 35
    no_1_transac_received = SystemTransactions(
        Wallet(),
        wallet.address,
        amnt_to_recieve_1
    )

    amnt_to_recieve_2 = 33
    no_2_transac_received = SystemTransactions(
        Wallet(),
        wallet.address,
        amnt_to_recieve_2
    )

    blockchain.add_block(
        [no_1_transac_received.convert_transaction_data_to_json(), no_2_transac_received.convert_transaction_data_to_json()]
    )

    assert Wallet.wallet_balance_calculation(blockchain, wallet.address) == \
        WALLET_STARTING_BALANCE - amount + amnt_to_recieve_1 + amnt_to_recieve_2
