#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #codecov
    codecov --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
fi
