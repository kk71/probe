#!/bin/bash -
#===============================================================================
#
#          FILE: log.sh
#
#         USAGE: ./log.sh
#
#   DESCRIPTION:
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (),
#  ORGANIZATION:
#       CREATED: 2019/06/03 12:31
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

d=`date '+%Y-%m-%d'`
echo "* tailing logs of $@ within $d ..."
sleep 3
tail -f ./logs/$@/$d/*
