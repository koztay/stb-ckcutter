#!/bin/sh
celery multi start worker1
#celery -A ecommerce_istebu_cookiecutter.taskapp worker -Q xml --concurrency=1 -l INFO -Ofair --without-gossip --without-mingle --without-heartbeat
#celery -A ecommerce_istebu_cookiecutter.taskapp worker -Q images --concurrency=1 -l INFO -Ofair --without-gossip --without-mingle --without-heartbeat
#celery -A ecommerce_istebu_cookiecutter.taskapp worker -Q default --concurrency=1 -l INFO -Ofair --without-gossip --without-mingle --without-heartbeat
