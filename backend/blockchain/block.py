import time

from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import convert_hex_to_binary
from backend.config import MINE_RATE


THE_GENESIS_BLOCK_DATA = {
    'timestamp': 1,
    'last_hash': 'genesis_last_hash',
    'hash': 'genesis_hash',
    'data': [],
    'difficulty': 3,
    'nonce': 'genesis_nonce'

}

class Block:
    """
    This is the block: The unit for storage.
    They store transactions in a blockchain that supports a cryptocurrency.
    """
    def __init__(self, timestamp, last_hash, hash, data, difficulty, nonce):
        self.timestamp = timestamp
        self.last_hash = last_hash
        self.hash = hash
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce

    def __repr__(self):
        return (
            'Block('
            f'timestamp: {self.timestamp}, '
            f'last_hash: {self.last_hash}, '
            f'hash: {self.hash}, '
            f'data: {self.data}), '
            f'difficulty: {self.difficulty}), '
            f'nonce: {self.nonce})'
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def convert_block_to_json(self):
        """
        In this section i serialize the block into a dictionary of 
        its attributes
        """

        return self.__dict__   

    @staticmethod
    def mine_the_block(last_block, data):
        """
        Here I mine a block based on the given last_block and data till the block hash 
        that is found meets requirement of leading O's as stipulated in the proof of work
        """
        timestamp = time.time_ns()
        last_hash = last_block.hash
        difficulty = Block.adjust_mining_difficulty(last_block, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        while convert_hex_to_binary(hash)[0:difficulty] != '0' * difficulty:
            nonce += 1
            timestamp = time.time_ns()
            difficulty = Block.adjust_mining_difficulty(last_block, timestamp)
            hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        return Block(timestamp, last_hash, hash, data, difficulty, nonce)

    @staticmethod
    def genesis_block_generator():
        """
        Here, i generate the genesis block
        """
        # return Block(
        #     THE_GENESIS_BLOCK_DATA['timestamp'],
        #     THE_GENESIS_BLOCK_DATA['last_hash'],
        #     THE_GENESIS_BLOCK_DATA['hash'],
        #     THE_GENESIS_BLOCK_DATA['data']
        # )
        return Block(**THE_GENESIS_BLOCK_DATA)

    @staticmethod
    def convert_block_from_json(block_json):
        """
        This section deserializes the json representation for a block instance.
        """
        return Block(**block_json)   

    @staticmethod
    def adjust_mining_difficulty(last_block, new_timestamp):
        """
        This sections calculates the adjusted difficulty according to the MINE_RATE by:
        - increasing the difficulty for quickly mined blocks.
        - descreasing the difficulty for slowly mined blocks.
        """

        if (new_timestamp - last_block.timestamp) < MINE_RATE:
            return last_block.difficulty + 1

        if (last_block.difficulty - 1) > 0:
            return last_block.difficulty - 1

        return 1

    @staticmethod
    def block_is_valid(last_block, block):
        """
        In this block, I am trying to validate a blokc by enforcing the following:
            - the block must have the proper last_hash reference
            - the block must meet the proof of work requirement
            - the difficulty must only adjust by 1
            - the block hash must be a valid combination of the block fields
        """
        if block.last_hash != last_block.hash:
            raise Exception ('Block `last_hash` Must be Correct')
        
        if convert_hex_to_binary(block.hash)[0:block.difficulty] != '0' * block.difficulty:
            raise Exception('`Proof of Work` Requirement has not Been Met')

        if abs(last_block.difficulty - block.difficulty) > 1:
            raise Exception('Block Difficulty Can Only Be Adjusted by 1')
        
        reconstructed_hash = crypto_hash(
            block.timestamp,
            block.last_hash,
            block.data,
            block.nonce,
            block.difficulty
        )

        if block.hash != reconstructed_hash:
            raise Exception('Block Hash Must be Correct')    

def main():
    genesis_block = Block.genesis_block_generator()
    bad_block = Block.mine_the_block(genesis_block, 'foo')
    bad_block.last_hash = 'wrong_data'

    try:
        Block.block_is_valid(genesis_block, bad_block)
    except Exception as e:
        print(f'block_is_valid: {e}')


if __name__ == '__main__':
    main()