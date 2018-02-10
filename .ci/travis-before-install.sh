#!/bin/bash

if [[ -z ${TOXENV} ]]; then
    sudo rm /usr/local/bin/docker-compose
    curl -L https://github.com/docker/compose/releases/download/1.17.1/docker-compose-`uname -s`-`uname -m` > docker-compose
    chmod +x docker-compose
    sudo mv docker-compose /usr/local/bin

    docker pull python:3.6
    docker pull tendermint/tendermint:0.13
    docker pull mongo:3.4.3
fi
