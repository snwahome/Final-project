import time

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from backend.blockchain.block import Block
from backend.wallet.transactions import SystemTransactions

pncofig = PNConfiguration()
pncofig.publish_key = 'pub-c-6b96b8c8-6958-4b11-beac-e69295491201'
pncofig.subscribe_key = 'sub-c-8fcf0e0c-304b-11eb-a9aa-e23bcc63a965'


COMMUNICATION_CHANNELS = {
    'TEST' : 'TEST',
    'BLOCK' : 'BLOCK',
    'TRANSACTION' : 'TRANSACTION'
}

class Listener(SubscribeCallback):
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        print(f'\n-- Channel: {message_object.channel} | Message : {message_object.message}')

        if message_object.channel == COMMUNICATION_CHANNELS['BLOCK']:
            block = Block.convert_block_from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_the_chain(potential_chain)
                self.transaction_pool.clear_the_blockchain_transactions(
                    self.blockchain
                )
                print('\n -- The local chain was replaced succesfully')
            except Exception as e:
                print(f'\n -- Unfortunately, the chain was not replaced: {e}')
        elif message_object.channel == COMMUNICATION_CHANNELS['TRANSACTION']:
            transaction = SystemTransactions.convert_transaction_data_from_json(message_object.message)
            self.transaction_pool.setting_the_trasaction(transaction)
            print('\n -- The New Transaction has Been Set in the Transaction Pool')


class PubSub():
    """
    This section, handles the publish/subscribe layer of the application. It provides
    the communication between the nodes of the blockchain network.
    """
    def __init__(self, blockchain, transaction_pool):
        self.pubnub = PubNub(pncofig)
        self.pubnub.subscribe().channels(COMMUNICATION_CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel, message):
        """
        This section is for publishing the message object to the channel
        """
        self.pubnub.publish().channel(channel).message(message).sync()
    
    def block_broadcast(self, block):
        """
        This section takes care of broacasting a block object to all noeds
        """
        self.publish(COMMUNICATION_CHANNELS['BLOCK'], block.convert_block_to_json())

    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction to all nodes.
        """
        self.publish(COMMUNICATION_CHANNELS['TRANSACTION'], transaction.convert_transaction_data_to_json()) 




def main():
    pubsub = PubSub()
    time.sleep(1)
    pubsub.publish(COMMUNICATION_CHANNELS['TEST'], {'foo': 'bar'})

if __name__ == '__main__':
    main()
