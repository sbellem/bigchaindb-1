#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
    -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
  docker-compose -f docker-compose.travis.yml run --rm --no-deps bdb pytest -v --cov=bigchaindb
fi
