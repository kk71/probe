#!/bin/bash - 
#===============================================================================
#
#          FILE: install.sh
# 
#         USAGE: ./install.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/03 09:15
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

probe_watchtower_path=`pwd`

echo "YOU WILL NEED THE ACCESS TO "
echo "dev.probe.yamucloud.com:5678 AND probe.yamucloud.com:8666"
echo "TO INSTALL DOCKER WITH PRIVATE REPO ENABLED!"
echo ""
echo "* uninstalling the old versions of docker packages if installed ..."
sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine

echo "* downloading docker packages ..."
cd /tmp
wget http://dev.probe.yamucloud.com:5678/dependencies/docker-all.tar.gz

echo "* installing ..."
sudo yum install -y yum-utils
tar xvf docker-all.tar.gz
cd docker
sudo yum install -y *

# check the docker executable is present, otherwise the following steps are meaningless
command -v docker >/dev/null 2>&1 || { echo >&2 "* docker is not installed properly.  Aborting."; exit 1; }

cd $probe_watchtower_path
echo "* set the docker repo self-registered sign to /etc/docker ..."
sudo mkdir -p /etc/docker/certs.d
sudo cp -r ./certs/* /etc/docker/certs.d/
echo "* making docker service auto-started at startup ..."
sudo systemctl enable docker
echo "* starting docker service ..."
sudo systemctl start docker
echo "* test if docker is working properly with our registry ..."
sudo docker run probe.yamucloud.com:8666/probe/hello-world:latest
echo " "
echo "MAKE SURE THE TESTING CONTAINER IS RUN AND EXITED PROPERLY!"
