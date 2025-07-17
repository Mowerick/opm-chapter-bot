#!/bin/bash
ARGS=$@
cd $(dirname $0)
DIRECTORY=".."
VIRTUALENV_DIRECTORY=./opmscrapervenv

cd ${DIRECTORY}
virtualenv -p python3 opmscrapervenv
if [[ ! -d $VIRTUALENV_DIRECTORY ]]; then
    python3 -m venv ./opmscrapervenv
fi

source opmscrapervenv/bin/activate
pip3 install -r requirements.txt
