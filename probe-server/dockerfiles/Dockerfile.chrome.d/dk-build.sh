#!/bin/bash - 
#===============================================================================
#
#          FILE: dk-build.sh
# 
#         USAGE: ./dk-build.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2021/03/24 11:47
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

echo "now building an image with python3.8 and google-chrome-stable(with chromedriver)..."
docker build -t probe.yamucloud.com:8666/probe-server/python3.9-chrome:latest -f Dockerfile.chrome .
docker push probe.yamucloud.com:8666/probe-server/python3.9-chrome:latest

