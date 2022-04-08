#!/bin/bash - 
#===============================================================================
#
#          FILE: stop-remove-containers.sh
# 
#         USAGE: ./stop-remove-containers.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/06 13:42
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

container_ids=`docker ps -aq -f "NAME=(probe-dev|probe-prod|watchtower)"`

echo "gonna stop and remove containers: $container_ids ..."
docker stop $container_ids
docker rm $container_ids
