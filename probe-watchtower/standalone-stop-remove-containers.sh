#!/bin/sh

set -o nounset                              # Treat unset variables as an error

container_ids=`docker ps -aq -f "NAME=probe-standalone"`

echo "gonna stop and remove containers: $container_ids ..."
docker stop $container_ids
docker rm $container_ids
