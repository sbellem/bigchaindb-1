#!/bin/bash

set -e -x

pip install --upgrade pip
#pip install --upgrade tox

#if [[ ${TOXENV} == py* ]]; then
#
#    #if [[ "${TOXENV}" == *-rdb ]]; then
#    #    sudo apt-get install rethinkdb
#    #elif [[ "${TOXENV}" == *-mdb ]]; then
#    #    sudo apt-get install mongodb-org-server
#    #fi
#
#    pip install --upgrade codecov
#fi

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
else
    pip install -e .[test]
    pip install --upgrade codecov
fi
