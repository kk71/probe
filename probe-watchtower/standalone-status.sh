#!/bin/bash -

set -o nounset                              # Treat unset variables as an error

docker ps -a -f "NAME=probe-standalone"
