from bigchaindb.util import verify_vote_signature


class BaseConsensusRules():
    """Base consensus rules for Bigchain.
    """

    @staticmethod
    def validate_transaction(bigchain, transaction):
        """See `models.Transaction.validate` for documentation"""
        return transaction.validate(bigchain)

    @staticmethod
    def validate_block(bigchain, block):
        """See `models.Block.validate` for documentation"""
        return block.validate(bigchain)

    @staticmethod
    def verify_vote_signature(voters, signed_vote):
        """Verify the signature of a vote.

        Refer to the documentation of ``bigchaindb.util.verify_signature``
        """
        return verify_vote_signature(voters, signed_vote)
