import base64
import json
import struct
import logging

from abci import (
    ABCIServer,
    BaseApplication,
    ResponseInfo,
    ResponseQuery,
    Result
)

from bigchaindb import Bigchain
from bigchaindb import config_utils
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import SchemaValidationError, ValidationError


logger = logging.getLogger(__name__)


# Tx encoding/decoding
def encode_number(value):
    return struct.pack('>I', value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder='big')


def validate_transaction(bigchaindb, tx):
    try:
        tx_obj = Transaction.from_dict(tx)
    except SchemaValidationError as e:
        logger.warning('Invalid transaction schema: %s', e.__cause__.message)
        return False
    except ValidationError as e:
        logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
        return False

    try:
        bigchaindb.validate_transaction(tx_obj)
    except ValidationError as e:
        logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
        return False
    return tx_obj


def write_transaction(bigchaindb, tx_obj):
    bigchaindb.write_transaction(tx_obj)


def encode_transaction(value):
    return base64.b64encode(json.dumps(value).encode('utf8')).decode('utf8')


def decode_transaction(raw):
    return json.loads(raw.decode('utf8'))


class SimpleCounter(BaseApplication):
    """Simple counting app.  It only excepts values sent to it in order.  The
    state maintains the current count. For example if starting at state 0, sending:
    -> 0x01 = ok
    -> 0x03 = fail (expects 2)

    To run it:
    - make a clean new directory for tendermint
    - start this server: python counter.py
    - start tendermint: tendermint --home "YOUR DIR HERE" node
    - The send transactions to the app:
    curl http://localhost:46657/broadcast_tx_commit?tx=0x01
    curl http://localhost:46657/broadcast_tx_commit?tx=0x02
    ...
    to see the latest count:
    curl http://localhost:46657/abci_query

    The way the app state is structured, you can also see the current state value
    in the tendermint console output.

    """
    def __init__(self, bigchaindb):
        self.bigchaindb = bigchaindb

    def info(self):
        r = ResponseInfo()
        r.last_block_height = 0
        r.last_block_app_hash = b''
        return r

    def init_chain(self, v):
        """Set initial state on first run"""
        self.txCount = 0

    def __valid_input(self, tx):
        """Check to see the given input is the next sequence in the count"""
        value = decode_number(tx)
        return value == (self.txCount + 1)

    def check_tx(self, tx):
        """ Validate the Tx before entry into the mempool """
        #if not self.__valid_input(tx):
        #    return Result.error(log='bad count')

        #return Result.ok(log='thumbs up')
        tx = decode_transaction(tx)
        print('check', tx['id'])
        if not validate_transaction(self.bigchaindb, tx):
            return Result.error(log='invalid transaction')

        return Result.ok(log='valid transaction')

    def deliver_tx(self, tx):
        """ Mutate state if valid Tx """
        #if not self.__valid_input(tx):
        #    return Result.error(log='bad count')

        #self.txCount += 1
        #return Result.ok()
        tx = decode_transaction(tx)
        print('deliver', tx['id'])
        tx = validate_transaction(self.bigchaindb, tx)
        if not tx:
            return Result.error(log='invalid transaction')

        self.buffer.append(tx)

        self.txCount += 1
        return Result.ok()

    def query(self, reqQuery):
        """Return the last tx count"""
        v = encode_number(self.txCount)
        rq = ResponseQuery(code=0, key=b'count', value=v)
        return rq

    def commit(self):
        """Return the current encode state value to tendermint"""
        #h = struct.pack('>Q', self.txCount)
        #return Result.ok(data=h)
        if self.buffer:
            block = self.bigchaindb.create_block(self.buffer)
            self.bigchaindb.write_block(block)
            print('block created', block.id)
        h = struct.pack('>Q', self.txCount)
        return Result.ok(data=h)

if __name__ == '__main__':
    app = ABCIServer(app=SimpleCounter())
    app.run()
