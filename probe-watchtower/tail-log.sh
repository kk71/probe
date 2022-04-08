#!/bin/bash - 
#===============================================================================
#
#          FILE: tail-log.sh
# 
#         USAGE: ./tail-log.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/04 11:56
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker logs -f probe-$1

