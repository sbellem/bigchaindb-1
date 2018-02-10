#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #codecov
    cd ${TRAVIS_BUILD_DIR}/tests
    ls -l .coverage
    #codecov -v --root ${TRAVIS_BUILD_DIR}/bigchaindb --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
    codecov -v
    ls -al ${TRAVIS_BUILD_DIR}/tests/coverage.xml
fi
