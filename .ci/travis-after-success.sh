#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #codecov
    codecov -v --root ${TRAVIS_BUILD_DIR}/bigchaindb --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
fi
