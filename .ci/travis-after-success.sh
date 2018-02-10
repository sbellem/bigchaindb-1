#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    cd ${TRAVIS_BUILD_DIR}/tests
    codecov -v
fi
