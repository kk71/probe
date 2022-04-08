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
#       CREATED: 2020/04/14 12:29
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

docker-compose ps --services