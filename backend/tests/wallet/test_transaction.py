import pytest

from backend.wallet.transactions import SystemTransactions
from backend.wallet.wallet import Wallet
from backend.config import THE_MINING_REWARD, INPUT_FOR_MINING_REWARD

def test_transaction():
    wallet_for_sender = Wallet()
    recipient = 'recipient'
    amount = 50
    transaction = SystemTransactions(wallet_for_sender, recipient, amount)

    assert transaction.transaction_output[recipient] == amount
    assert transaction.transaction_output[wallet_for_sender.address] == wallet_for_sender.wallet_balance - amount

    assert 'timestamp' in  transaction.transaction_input
    assert transaction.transaction_input['amount'] == wallet_for_sender.wallet_balance
    assert transaction.transaction_input['address'] == wallet_for_sender.address
    assert transaction.transaction_input['public_key'] == wallet_for_sender.public_key


    assert Wallet.verify_signature(
        transaction.transaction_input['public_key'],
        transaction.transaction_output,
        transaction.transaction_input['signature']
    )

def test_if_transaction_exceeds_balance():
    with pytest.raises(Exception, match='The Amount Exceeds Balance'):
        SystemTransactions(Wallet(), 'recipient', 9001)

def test_if_transaction_update_exceeds_balance():
    wallet_for_sender = Wallet()
    transaction = SystemTransactions(wallet_for_sender, 'recipient', 50)

    with pytest.raises(Exception, match='The Amount Exceeds Balance'):
        transaction.transaction_update(wallet_for_sender, 'new_recipient', 9001)

def test_for_transaction_update():
    wallet_for_sender = Wallet()
    first_recipient = 'first_recipient'
    first_amount_sent = 45
    transaction = SystemTransactions(wallet_for_sender, first_recipient, first_amount_sent)

    next_recipient = 'next_recipient'
    next_amount_sent = 70
    transaction.transaction_update(wallet_for_sender, next_recipient, next_amount_sent)

    assert transaction.transaction_output[next_recipient] == next_amount_sent
    assert transaction.transaction_output[wallet_for_sender.address] ==\
        wallet_for_sender.wallet_balance - first_amount_sent - next_amount_sent
    assert Wallet.verify_signature(
        transaction.transaction_input['public_key'],
        transaction.transaction_output,
        transaction.transaction_input['signature']
    )

    amount_resend_to_first_recipient = 30
    transaction.transaction_update(wallet_for_sender, first_recipient, amount_resend_to_first_recipient)

    assert transaction.transaction_output[first_recipient] == \
        first_amount_sent + amount_resend_to_first_recipient
    assert transaction.transaction_output[wallet_for_sender.address] ==\
        wallet_for_sender.wallet_balance - first_amount_sent - next_amount_sent - amount_resend_to_first_recipient
    assert Wallet.verify_signature(
        transaction.transaction_input['public_key'],
        transaction.transaction_output,
        transaction.transaction_input['signature']
    )

def test_for_valid_transaction():
    SystemTransactions.positively_validate_transaction(SystemTransactions(Wallet(), 'recipient', 50))

def test_valid_transaction_with_invalid_outputs():
    wallet_for_sender = Wallet()
    transaction = SystemTransactions(wallet_for_sender, 'recipient', 45)
    transaction.transaction_output[wallet_for_sender.address] = 9001

    with pytest.raises(Exception, match='Invalid Transaction Because the Output Values Are Wrong'):
        SystemTransactions.positively_validate_transaction(transaction)

def test_for_valid_transaction_with_invalid_signature():
    transaction = SystemTransactions(Wallet(), 'recipient', 45)
    transaction.transaction_input['signature'] = Wallet().signature_generation(transaction.transaction_output)

    with pytest.raises(Exception, match='The Signature is Invalid'):
        SystemTransactions.positively_validate_transaction(transaction)

def test_for_transaction_rewards():
    miner_wallet = Wallet()
    transaction = SystemTransactions.transaction_reward_generation(miner_wallet)

    assert transaction.transaction_input == INPUT_FOR_MINING_REWARD
    assert transaction.transaction_output[miner_wallet.address] == THE_MINING_REWARD

def test_for_valid_reward_transaction():
    reward_transaction = SystemTransactions.transaction_reward_generation(Wallet())
    SystemTransactions.positively_validate_transaction(reward_transaction)

def test_for_extra_recipient_invalid_transaction():
    reward_transaction = SystemTransactions.transaction_reward_generation(Wallet())
    reward_transaction.transaction_output['extra_recipient'] = 60

    with pytest.raises(Exception, match='Mining Reward is Invalid'):
        SystemTransactions.positively_validate_transaction(reward_transaction)

def test_invalid_reward_transaction_invalid_amount():
    miner_wallet = Wallet()
    reward_transaction = SystemTransactions.transaction_reward_generation(miner_wallet)
    reward_transaction.transaction_output[miner_wallet.address] = 9001

    with pytest.raises(Exception, match='Mining Reward is Invalid'):
        SystemTransactions.positively_validate_transaction(reward_transaction)   