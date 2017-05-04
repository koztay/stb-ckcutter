#!/usr/bin/env bash

#git rm --cached --force importer/tests/data/18.04.2017-Yeni Liste.xlsx
#git rm --cached --force importer/tests/data/istebu_08_Ocak_2017_Liste Son Hali.xlsx

docker-compose run celeryworker celery -A ecommerce_istebu_cookiecutter.taskapp purge
