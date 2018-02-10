#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    ls -al ${TRAVIS_BUILD_DIR}/bigchaindb/.coverage
    codecov --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
fi
