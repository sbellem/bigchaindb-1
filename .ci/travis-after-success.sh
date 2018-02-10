#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #codecov
    cd ${TRAVIS_BUILD_DIR}/bigchaindb
    ls -l .coverage
    #codecov -v --root ${TRAVIS_BUILD_DIR}/bigchaindb --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
    codecov -v
    ls -al ${TRAVIS_BUILD_DIR}/bigchaindb/coverage.xml
    ls -al ${TRAVIS_BUILD_DIR}/coverage.xml
fi
