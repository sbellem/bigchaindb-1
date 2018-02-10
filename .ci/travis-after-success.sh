#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    pip install --upgrade codecov
    codecov
fi
