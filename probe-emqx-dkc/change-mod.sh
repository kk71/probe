#!/bin/bash - 
#===============================================================================
#
#          FILE: change-mod.sh
# 
#         USAGE: ./change-mod.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/11 11:43
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

sudo chmod a+w ./emqx.conf
sudo chmod a+w ./emqx_auth_redis.conf
