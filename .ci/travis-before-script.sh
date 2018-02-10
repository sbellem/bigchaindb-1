#!/bin/bash

set -e -x

if [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
        -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps mdb
    sleep 20
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps bdb
    sleep 20
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps tendermint
    sleep 20
    docker-compose -f docker-compose.tendermint.yml logs --tail=20 mdb
    docker-compose -f docker-compose.tendermint.yml logs --tail=20 bdb
    docker-compose -f docker-compose.tendermint.yml logs --tail=20 tendermint
fi
