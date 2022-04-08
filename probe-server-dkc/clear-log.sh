#!/bin/bash - 
#===============================================================================
#
#          FILE: clear-log.sh
# 
#         USAGE: ./clear-log.sh 
# 
#   DESCRIPTION: please use this script only after the service is down
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/26 15:10
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

rm -rf logs
mkdir -p logs/scheduler
mkdir -p logs/controller
mkdir -p logs/analyser
mkdir -p logs/statistics

