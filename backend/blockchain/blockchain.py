from backend.blockchain.block import Block
from backend.wallet.transactions import SystemTransactions
from backend.wallet.wallet import Wallet
from backend.config import INPUT_FOR_MINING_REWARD

class Blockchain:
    """"
    This the block: The public ledger for all transactions. It is implemented
    as a list of blocks - data sets of transactions
    """
    def __init__(self):
        self.chain = [Block.genesis_block_generator()]

    def add_block(self, data):
        self.chain.append(Block.mine_the_block(self.chain[-1], data))

    def __repr__(self):
        return f'Blockchain: {self.chain}'

    def replace_the_chain(self, chain):
        """
        In this section, i replace the local chain with the incoming one  
        but only if the following applies:
            - The incoming chain is longer than the local one.
            - The incoming chain is formatted properly.
        """
        if len(chain) <= len(self.chain):
            raise Exception('Chain Cannot Be Replaced: Incoming chain must be longer.')

        try:
            Blockchain.chain_is_valid(chain)
        except Exception as e:
            raise Exception(f'Chain Cannot Be Replaced: Incoming chain is invalid: {e}')

        self.chain = chain

    def convert_blockchain_list_to_json(self):
        """
        This section will serialize the blockchain into a list of blocks.
        """
        return list(map(lambda  block: block.convert_block_to_json(), self.chain))

        
    @staticmethod
    def convert_blocklist_to_chain_from_json(chain_json):
        """
        In this section, I serialize a list of serialized blocks into 
        a Blokchain instance, where the result will contain a chain list of Block instances.
        """
        blockchain = Blockchain()
        blockchain.chain = list(
            map(lambda block_json: Block.convert_block_from_json(block_json), chain_json)
        )
        return  blockchain

    @staticmethod
    def chain_is_valid(chain):
        """
        In this block, I validate the incoming chain.
        The whole point, it to ednforce the following rules of the blockchain:
          - the chain starts with the genesis block
          - blocks must be formatted correctly
        """
        if chain[0] != Block.genesis_block_generator():
            raise Exception('The Genesis Block Must Be Valid')

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i-1]
            Block.block_is_valid(last_block, block)      

        Blockchain.transaction_chain_is_valid(chain)
        


    @staticmethod
    def transaction_chain_is_valid(chain):
        """
        This section deals with enforcing rules of a chain made up 
        of blocks of transactions. The following must apply:
            - Each transaction must only appear once in the chain.
            - There can only be one mining reward per block.
            - Each transaction must be valid.
        """
        transaction_ids = set()
        
        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False

            for transaction_json in block.data:
                transaction = SystemTransactions.convert_transaction_data_from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f'Transaction {transaction.id} is not unique')

                transaction_ids.add(transaction.id)
                
                if transaction.transaction_input == INPUT_FOR_MINING_REWARD:
                    if has_mining_reward:
                        raise Exception(
                            'There can only be one mining reward given per block.'\
                            f'Check block with the hash: {block.hash}'
                        )
                    has_mining_reward = True  
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]
                    historic_balance = Wallet.wallet_balance_calculation(
                        historic_blockchain,
                        transaction.transaction_input['address']
                    )

                    if historic_balance != transaction.transaction_input['amount']:
                        raise Exception(
                            f'Transaction {transaction.id} has an invalid '\
                            'input amount'
                        )

                SystemTransactions.positively_validate_transaction(transaction)      


def main():
    blockchain = Blockchain()
    blockchain.add_block('one')
    blockchain.add_block('two')

    print(blockchain)
    print (f'blockchain.py __name__: {__name__}')

if __name__ == '__main__':
    main()
