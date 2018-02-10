#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
    -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
  docker-compose -f docker-compose.tendermint.yml ps
  docker-compose -f docker-compose.tendermint.yml run --rm  --no-deps bdb ping tendermint --timeout 5
  docker-compose -f docker-compose.tendermint.yml run --rm  --no-deps tendermint ping bdb -w 5
  docker-compose -f docker-compose.tendermint.yml run --rm  --no-deps tendermint curl http://bdb:9984
  docker-compose -f docker-compose.tendermint.yml run --rm  --no-deps bdb curl http://tendermint:46657/status
  curl http://localhost:46657/status
  docker-compose -f docker-compose.tendermint.yml up curl-client
  docker-compose -f docker-compose.tendermint.yml logs tendermint
  docker-compose -f docker-compose.tendermint.yml logs bdb
  docker-compose -f docker-compose.tendermint.yml run --rm --no-deps bdb pytest -v --cov=bigchaindb
fi
