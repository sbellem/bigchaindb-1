"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""
import logging

from abci import BaseApplication, Result

from bigchaindb.tendermint import BigchainDB
from bigchaindb.tendermint.utils import decode_transaction

logger = logging.getLogger(__name__)


class App(BaseApplication):
    """Bridge between BigchainDB and Tendermint.

    The role of this class is to expose the BigchainDB
    transactional logic to the Tendermint Consensus
    State Machine."""

    def __init__(self, bigchaindb=None):
        if not bigchaindb:
            bigchaindb = BigchainDB()
        self.bigchaindb = bigchaindb

    def check_tx(self, raw_transaction):
        """Validate the transaction before entry into
        the mempool.

        Args:
            raw_tx: an encoded transaction."""
        logger.debug('check_tx: %s', raw_transaction)
        transaction = decode_transaction(raw_transaction)
        if self.bigchaindb.validate_transaction(transaction):
            logger.debug('check_tx: VALID')
            return Result.ok()
        else:
            logger.debug('check_tx: INVALID')
            return Result.error()

    def deliver_tx(self, raw_transaction):
        """Validate the transaction before mutating the state.

        Args:
            raw_tx: an encoded transaction."""

        logger.debug('deliver_tx: %s', raw_transaction)
        transaction = self.bigchaindb.validate_transaction(
                decode_transaction(raw_transaction))

        if not transaction:
            logger.debug('deliver_tx: INVALID')
            return Result.error(log='Invalid transaction')
        else:
            logger.debug('storing tx')
            self.bigchaindb.store_transaction(transaction)
            return Result.ok()
