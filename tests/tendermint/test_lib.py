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


@pytest.mark.bdb
def test_get_latest_block(tb):
    from bigchaindb.tendermint.lib import Block

    b = tb
    for i in range(10):
        app_hash = os.urandom(16).hex()
        txn_id = os.urandom(16).hex()
        block = Block(app_hash=app_hash, height=i,
                      transactions=[txn_id])._asdict()
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
    b.write_transaction(tx, 'broadcast_tx_async')

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert 'broadcast_tx_async' == kwargs['json']['method']
    encoded_tx = [encode_transaction(tx.to_dict())]
    assert encoded_tx == kwargs['json']['params']


@patch('requests.post')
@pytest.mark.parametrize('mode', [
    'broadcast_tx_async',
    'broadcast_tx_sync',
    'broadcast_tx_commit'
])
def test_post_transaction_valid_modes(mock_post, b, mode):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None) \
        .sign([alice.private_key]).to_dict()
    tx = b.validate_transaction(tx)
    b.write_transaction(tx, mode)

    args, kwargs = mock_post.call_args
    assert mode == kwargs['json']['method']


def test_post_transaction_invalid_mode(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.common.exceptions import ValidationError
    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None) \
        .sign([alice.private_key]).to_dict()
    tx = b.validate_transaction(tx)
    with pytest.raises(ValidationError):
        b.write_transaction(tx, 'nope')


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
def test_store_transaction(mocker, tb, signed_create_tx,
                           signed_transfer_tx, db_context):
    mocked_store_asset = mocker.patch('bigchaindb.backend.query.store_asset')
    mocked_store_metadata = mocker.patch(
        'bigchaindb.backend.query.store_metadata')
    mocked_store_transaction = mocker.patch(
        'bigchaindb.backend.query.store_transaction')
    mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    tb.store_transaction(signed_create_tx)
    utxoset = mongo_client[db_context.name]['utxos']
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_create_tx.id
    assert utxo['output_index'] == 0
    mocked_store_asset.assert_called_once_with(
        tb.connection,
        {'id': signed_create_tx.id, 'data': signed_create_tx.asset['data']},
    )
    mocked_store_metadata.asser_called_once_with(
        tb.connection,
        {'id': signed_create_tx.id, 'metadata': signed_create_tx.metadata},
    )
    mocked_store_transaction.assert_called_once_with(
        tb.connection,
        {k: v for k, v in signed_create_tx.to_dict().items()
         if k not in ('asset', 'metadata')},
    )
    mocked_store_asset.reset_mock()
    mocked_store_metadata.reset_mock()
    mocked_store_transaction.reset_mock()
    tb.store_transaction(signed_transfer_tx)
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_transfer_tx.id
    assert utxo['output_index'] == 0
    assert not mocked_store_asset.called
    mocked_store_metadata.asser_called_once_with(
        tb.connection,
        {'id': signed_transfer_tx.id, 'metadata': signed_transfer_tx.metadata},
    )
    mocked_store_transaction.assert_called_once_with(
        tb.connection,
        {k: v for k, v in signed_transfer_tx.to_dict().items()
         if k != 'metadata'},
    )
