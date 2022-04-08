#!/bin/sh

set -o nounset                              # Treat unset variables as an error

echo "* build docker image for emqx..."
t="probe.yamucloud.com:8666/emqx/default:latest"
docker build -t $t .
echo "* built the image as $t"
