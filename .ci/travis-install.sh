#!/bin/bash

set -e -x

docker-compose build --no-cache
#pip install --upgrade pip
#
#if [[ -n ${TOXENV} ]]; then
#    pip install --upgrade tox
#else
#    pip install .[test]
#    pip install --upgrade codecov
#fi
