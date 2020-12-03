import uuid
import time

from backend.wallet.wallet import Wallet
from backend.config import THE_MINING_REWARD, INPUT_FOR_MINING_REWARD

class SystemTransactions:
    """
    In this section i document all currency exchanges from a 
    sender to one or more recepients
    """

    def __init__(
        self, 
        wallet_for_sender=None, 
        recipient=None, 
        amount=None,
        id=None,
        transaction_output=None,
        transaction_input=None
    ):
        self.id = id or str(uuid.uuid4())[0:8]
        self.transaction_output = transaction_output or self.create_transaction_output(
            wallet_for_sender,
            recipient,
            amount
        )
        self.transaction_input = transaction_input or self.create_transaction_input(wallet_for_sender, self.transaction_output)

    def create_transaction_output(self, wallet_for_sender, recipient, amount):
        """
        This section controls transaction ouputs
        """
        if amount > wallet_for_sender.wallet_balance:
            raise Exception('The Amount Exceeds Balance')

        transaction_ouput = {}
        transaction_ouput[recipient] = amount
        transaction_ouput[wallet_for_sender.address] = wallet_for_sender.wallet_balance - amount

        return transaction_ouput

    def create_transaction_input(self, wallet_for_sender, transaction_ouput):
        """
        This section is to structure the input data for the transaction. Then
        sign the transaction and include the sender's public key and address
        """

        return {
            'timestamp': time.time_ns(),
            'amount': wallet_for_sender.wallet_balance,
            'address': wallet_for_sender.address,
            'public_key': wallet_for_sender.public_key,
            'signature': wallet_for_sender.signature_generation(transaction_ouput)
    }

    def transaction_update(self, wallet_for_sender, recipient, amount):
        """
        Update the transaction with an existing or new recipient.
        """
        if amount > self.transaction_output[wallet_for_sender.address]:
            raise Exception('The Amount Exceeds Balance')

        if recipient in self.transaction_output:
            self.transaction_output[recipient] = self.transaction_output[recipient] + amount
        else:
            self.transaction_output[recipient] = amount

        self.transaction_output[wallet_for_sender.address] = \
            self.transaction_output[wallet_for_sender.address] - amount

        self.transaction_input = self.create_transaction_input(wallet_for_sender, self.transaction_output)

    def convert_transaction_data_to_json(self):
        """
        Serialize the transaction.
        """
        return self.__dict__

    @staticmethod
    def convert_transaction_data_from_json(transaction_json):
        """
        In this section, i seserialize a transaction's json 
        representation back into a Transaction instance
        """
        return SystemTransactions(**transaction_json)

    @staticmethod
    def positively_validate_transaction(transaction):
        """
        This section is responsible for validating a transaction and 
        then to raise an exception for invalid transactions.
        """
        if transaction.transaction_input == INPUT_FOR_MINING_REWARD:
            if list(transaction.transaction_output.values()) != [THE_MINING_REWARD]:
                raise Exception('Mining Reward is Invalid')
            return
        transaction_output_total = sum(transaction.transaction_output.values())

        if transaction.transaction_input['amount'] != transaction_output_total:
            raise Exception('Invalid Transaction Because the Output Values Are Wrong')

        if not Wallet.verify_signature(
            transaction.transaction_input['public_key'],
            transaction.transaction_output,
            transaction.transaction_input['signature']
        ):
            raise Exception('The Signature is Invalid')

    @staticmethod
    def transaction_reward_generation(miner_wallet):
        """
        This section generates a reward to give miners 
        """
        output = {}
        output[miner_wallet.address] = THE_MINING_REWARD
        
        return SystemTransactions(transaction_input=INPUT_FOR_MINING_REWARD, transaction_output=output)

def main():
    transaction = SystemTransactions(Wallet(), 'recipient', 15)
    print(f'transaction Data as .__dict__: {transaction.__dict__}')

    transaction_json = transaction.convert_transaction_data_to_json()
    restored_transaction_data = SystemTransactions.convert_transaction_data_from_json(transaction_json)
    print(f'Restored Transaction Data as .__dict__: {restored_transaction_data.__dict__}')

if __name__ == '__main__':
    main()
