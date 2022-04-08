#!/bin/bash - 
#===============================================================================
#
#          FILE: create-volumes.sh
# 
#         USAGE: ./create-volumes.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/12 10:50
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker volume create probe-emqx-etc
docker volume create probe-emqx-data

