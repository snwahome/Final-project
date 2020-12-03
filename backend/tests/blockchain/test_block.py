import pytest
import time

from backend.blockchain.block import Block, THE_GENESIS_BLOCK_DATA
from backend.config import MINE_RATE, SECS
from backend.util.hex_to_binary import convert_hex_to_binary


def test_for_mining_block():
    last_block = Block.genesis_block_generator()
    data = 'test-data'
    block = Block.mine_the_block(last_block, data)

    assert isinstance(block, Block)
    assert block.data == data
    assert block.last_hash == last_block.hash
    assert convert_hex_to_binary(block.hash)[0:block.difficulty] == '0' * block.difficulty

def test_for_genesis_generation():
    genesis = Block.genesis_block_generator()

    assert isinstance(genesis, Block)
    for key, value in THE_GENESIS_BLOCK_DATA.items():
        getattr(genesis, key) == value

def test_for_quickly_mined_blocks():
    last_block = Block.mine_the_block(Block.genesis_block_generator(), 'foo')
    mined_block = Block.mine_the_block(last_block, 'bar')

    assert mined_block.difficulty == last_block.difficulty + 1

def test_for_slowly_mined_blocks():
    last_block = Block.mine_the_block(Block.genesis_block_generator(), 'foo')
    time.sleep(MINE_RATE / SECS)
    mined_block = Block.mine_the_block(last_block, 'bar')

    assert mined_block.difficulty == last_block.difficulty - 1

def test_for_mined_block_diffuculty_limit_at_1():
    last_block = Block(
        time.time_ns(),
        'test_last_hash',
        'test_hash',
        'test_data',
        1,
        0
    )

    time.sleep(MINE_RATE / SECS)
    mined_block = Block.mine_the_block(last_block, 'bar')

    assert mined_block.difficulty == 1

@pytest.fixture
def last_block():
    return Block.genesis_block_generator()

@pytest.fixture
def block(last_block):
    return Block.mine_the_block(last_block, 'test_data')

def test_if_block_is_valid(last_block, block):
    Block.block_is_valid(last_block, block)

def test_if_bad_last_hash_in_block_is_valid(last_block, block):
    block.last_hash = 'bad_last_hash'

    with pytest.raises(Exception, match='`last_hash` Must be Correct'):
        Block.block_is_valid(last_block, block)

def test_if_bad_proof_of_work_in_block_is_valid(last_block, block):
    block.hash = 'fff'

    with pytest.raises(Exception, match='`Proof of Work` Requirement has not Been Met'):
        Block.block_is_valid(last_block, block)

def test_if_jumped_difficulty_in_block_is_valid(last_block, block):
    jumped_difficulty = 10
    block.difficulty = jumped_difficulty
    block.hash = f'{"0" * jumped_difficulty}111abc'

    with pytest.raises(Exception, match='Block Difficulty Can Only Be Adjusted by 1'):
        Block.block_is_valid(last_block, block)

def test_if_bad_block_hash_in_block_is_valid(last_block, block):
	block.hash = '0000000000000000bacabc'

	with pytest.raises(Exception, match='Block Hash Must be Correct'):
		Block.block_is_valid(last_block, block)