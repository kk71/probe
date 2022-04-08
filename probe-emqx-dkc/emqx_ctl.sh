#!/bin/bash - 
#===============================================================================
#
#          FILE: emqx_ctl.sh
# 
#         USAGE: ./emqx_ctl.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/10 11:35
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker exec -it probe-emqx emqx_ctl

