#!/bin/bash - 
#===============================================================================
#
#          FILE: emqx.sh
# 
#         USAGE: ./emqx.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/10 11:34
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker exec -it probe-emqx emqx $0

