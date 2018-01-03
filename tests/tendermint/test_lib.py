import os
from unittest.mock import patch

import pytest

from bigchaindb import backend


pytestmark = pytest.mark.tendermint


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


def test_extract_spent_outputs(tb, signed_transfer_tx):
    spent_outputs = tb.extract_spent_outputs(signed_transfer_tx)
    tx = signed_transfer_tx.to_dict()
    assert len(spent_outputs) == 1
    spent_output = spent_outputs[0]
    assert spent_output.transaction_id == tx['inputs'][0]['fulfills']['transaction_id']
    assert spent_output.output_index == tx['inputs'][0]['fulfills']['output_index']
    assert spent_output._asdict() == tx['inputs'][0]['fulfills']


def test_update_utxoset():
    raise NotImplementedError
