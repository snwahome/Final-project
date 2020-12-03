class TransactionPool:
    def __init__(self):
        self.map_of_transactions = {}

    def setting_the_trasaction(self, transaction):
        """
        This section is in charge of setting a 
        transaction in the transaction pool
        """

        self.map_of_transactions[transaction.id] = transaction

    def existing_transaction(self, address):
        """
        In this section, i try to find a transaction generated 
        by the address in the transaction pool
        """
        for transaction in self.map_of_transactions.values():
            if transaction.transaction_input['address'] == address:
                return transaction

    def transaction_of_data(self):
        """
        this sections returns the transactions of thje transaction pool represented in their
        json serialized form.
        """

        return list(map(
            lambda transaction: transaction.convert_transaction_data_to_json(),
            self.map_of_transactions.values()
        ))

    def clear_the_blockchain_transactions(self, blockchain):
        """
        This section deals with deleting blockchain recorded 
        transactions from the transaction pool.
        """
        for block in blockchain.chain:
            for transaction in block.data:
                try:
                    del self.map_of_transactions[transaction['id']]
                except KeyError:
                    pass   