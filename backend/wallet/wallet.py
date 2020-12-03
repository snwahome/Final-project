import uuid
import json

from backend.config import WALLET_STARTING_BALANCE
#from backend.wallet.transactions import SystemTransactions

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature,
    decode_dss_signature
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class Wallet:
    """
    This section denotes the individual wallet held
    by a miner and does the following:
        - Keeps track of miner's balance
        - Allows a miner to authorize transactions
    """

    def __init__(self, blockchain=None):
        self.blockchain = blockchain
        self.address = str(uuid.uuid4())[0:8]
        self.wallet_balance = WALLET_STARTING_BALANCE
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        self.public_key_serialization()

    @property
    def the_true_balance(self):
        return Wallet.wallet_balance_calculation(self.blockchain, self.address)

    def public_key_serialization(self):
        """
        This section deals with Serializing the public key 
        """
        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def signature_generation(self, data):
        """
        In this section, i use the data from local private key to generate
        a signature
        """
        return decode_dss_signature(self.private_key.sign(
            json.dumps(data).encode('utf-8'), 
            ec.ECDSA(hashes.SHA256())
        ))

    @staticmethod
    def verify_signature(public_key, data, signature):
        """
        In this section, i verify the generated signatures based on the original
        public key and data
        """
        deserialized_public_key = serialization.load_pem_public_key(
            public_key.encode('utf-8'),
            default_backend()
        )

        (r, s) = signature
     
        try:
            deserialized_public_key.verify(
                encode_dss_signature(r,s),
                json.dumps(data).encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False
    @staticmethod
    def wallet_balance_calculation(blockchain, address):
        """
        In this section i calculate the balance of the given address with considerations
        based on the transaction data within the blockchain

        It is important to note that the balance is found by adding the output values that
        belong to the address since the most recent transaction by that address.
        """
        true_balance = WALLET_STARTING_BALANCE

        if not blockchain: 
            return true_balance

            for block in blockchain.chain:
                for transaction in block.data:
                    if transaction['transaction_input']['address'] == address:
                        # Balance should reset anytime the address conducts 
                        # a new transaction
                        true_balance = transaction['transaction_output'][address]
                    elif address in transaction['transaction_output']:
                        true_balance += transaction['transaction_output'][address]

            return true_balance
def main():
    wallet = Wallet()
    print(f'Wallet Contents (.__dict__): {wallet.__dict__}')

    data = {'foo' : 'bar'}
    signature = wallet.signature_generation(data)
    print(f'signature: {signature}')

    when_valid = Wallet.verify_signature(wallet.public_key, data, signature)
    print(f'When Valid: {when_valid}')

    when_invalid = Wallet.verify_signature(Wallet().public_key, data, signature)
    print(f'When Invalid: {when_invalid}')

    
if __name__ == '__main__':
    main()