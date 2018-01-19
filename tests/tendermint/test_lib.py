import os
from unittest.mock import patch

import pytest
from pymongo import MongoClient

from bigchaindb import backend


pytestmark = pytest.mark.tendermint


@pytest.mark.bdb
def test_asset_is_separated_from_transaciton(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    asset = {'Never gonna': ['give you up',
                             'let you down',
                             'run around'
                             'desert you',
                             'make you cry',
                             'say goodbye',
                             'tell a lie',
                             'hurt you']}

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)],
                            metadata=None,
                            asset=asset)\
                    .sign([alice.private_key])

    b.store_transaction(tx)
    assert 'asset' not in backend.query.get_transaction(b.connection, tx.id)
    assert backend.query.get_asset(b.connection, tx.id)['data'] == asset
    assert b.get_transaction(tx.id) == tx


def test_get_latest_block(b):
    from bigchaindb.tendermint.lib import Block

    for i in range(10):
        app_hash = os.urandom(16).hex()
        block = Block(app_hash=app_hash, height=i)._asdict()
        b.store_block(block)

    block = b.get_latest_block()
    assert block['height'] == 9


def test_validation_error(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key]).to_dict()

    tx['metadata'] = ''
    assert not b.validate_transaction(tx)


@patch('requests.post')
def test_write_and_post_transaction(mock_post, b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.tendermint.utils import encode_transaction

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key]).to_dict()

    tx = b.validate_transaction(tx)
    b.write_transaction(tx)

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert 'broadcast_tx_async' == kwargs['json']['method']
    encoded_tx = [encode_transaction(tx.to_dict())]
    assert encoded_tx == kwargs['json']['params']


@pytest.mark.bdb
def test_update_utxoset(tb, signed_create_tx, signed_transfer_tx, db_context):
    mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    tb.update_utxoset(signed_create_tx)
    utxoset = mongo_client[db_context.name]['utxos']
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_create_tx.id
    assert utxo['output_index'] == 0
    tb.update_utxoset(signed_transfer_tx)
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_transfer_tx.id
    assert utxo['output_index'] == 0


@pytest.mark.bdb
def test_store_transaction(mocker, tb, signed_create_tx, signed_transfer_tx, db_context):
    mocked_store_asset = mocker.patch('bigchaindb.backend.query.store_asset')
    mocked_store_metadata = mocker.patch('bigchaindb.backend.query.store_metadata')
    mocked_store_transaction = mocker.patch('bigchaindb.backend.query.store_transaction')
    mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    tb.store_transaction(signed_create_tx)
    utxoset = mongo_client[db_context.name]['utxos']
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_create_tx.id
    assert utxo['output_index'] == 0
    assert mocked_store_asset.called
    assert mocked_store_metadata.called
    assert mocked_store_transaction.called
    tb.store_transaction(signed_transfer_tx)
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_transfer_tx.id
    assert utxo['output_index'] == 0
