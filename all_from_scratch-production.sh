#!/usr/bin/env bash

# Aşağıdaki satırlara CoreOs için gerek var.
# Activate bashrc
# there is no need to run the following line
# because i have fixed it by adding it to ~/.bash_profile
# source ~/.bashrc

# Use docker 1.10.3
# source satırını çalıştırmayınca dvm satırı çalışsa bile docker -v
# doğru versiyon göstermiyor...
#source ~/.bashrc
#dvm use 1.10.3
#docker -v

eval $(docker-machine env istebu-core01)
# eval $(docker-machine env istebu)
# Stop and remove all containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# Delete all images
docker rmi -f $(docker images -q)

# Delete all volumes
docker volume ls -qf dangling=true | xargs docker volume rm

# Build with no-cache
docker-compose build
# Build without no-cache
#docker-compose -f docker-compose-production.yml build
# Up containers
docker-compose up -d