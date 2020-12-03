import time

from backend.blockchain.blockchain import Blockchain
from backend.config import SECS

blockchain = Blockchain()

times = []

for i in range(1000):
    start_time = time.time_ns()
    blockchain.add_block(i)
    end_time = time.time_ns()


    time_to_mine = (end_time - start_time) / SECS
    times.append(time_to_mine)

    avg_time = sum(times) / len(times)

    print(f'The new block difficulty value: {blockchain.chain[-1].difficulty}')
    print(f'Time left to mine new block is: {time_to_mine}s')
    print(f'The new block difficulty value is: {avg_time}s\n')
    




