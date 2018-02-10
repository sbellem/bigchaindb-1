#!/bin/bash

set -e -x

if [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
        -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps mdb
    sleep 20
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps bdb
    sleep 40
    docker-compose -f docker-compose.tendermint.yml up -d --no-deps tendermint
fi
