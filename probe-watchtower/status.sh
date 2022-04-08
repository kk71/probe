#!/bin/bash - 
#===============================================================================
#
#          FILE: status.sh
# 
#         USAGE: ./status.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/04 12:03
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker ps -a -f "NAME=(probe-dev|probe-prod|watchtower)"
