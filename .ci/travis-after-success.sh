#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    #ls -al ${TRAVIS_BUILD_DIR}/bigchaindb/.coverage
    ls -al ${TRAVIS_BUILD_DIR}/.coverage
    #codecov --gcov-root ${TRAVIS_BUILD_DIR}/bigchaindb
    codecov
fi
