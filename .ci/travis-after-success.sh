#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #codecov
    ls -al ${TRAVIS_BUILD_DIR}/bigchaindb/.coverage
    cd ${TRAVIS_BUILD_DIR}/bigchaindb
    codecov -v --root ${TRAVIS_BUILD_DIR}/bigchaindb --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
    ls -al ${TRAVIS_BUILD_DIR}/bigchaindb/coverage.xml
    ls -al ${TRAVIS_BUILD_DIR}/coverage.xml
fi
