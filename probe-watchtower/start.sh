#!/bin/sh


#
# usage:
#
# ./start.sh [mount-default-config]
# mount-default-config: mount external config.default.json file into the container


set -o nounset                              # Treat unset variables as an error


the_default_config_json_file="$(pwd)/config.default.json"
dev_config_json_file="$(pwd)/config.json.dev"
prod_config_json_file="$(pwd)/config.json.prod"


to_mount_default_config="";
if [[ "$@" = "mount-default-config" ]]; then
    touch $the_default_config_json_file
    to_mount_default_config="-v $the_default_config_json_file:/project/config.default.json"
    echo "* mounting with external default config ..."
fi

echo "starting the containers ..."

docker run -d \
    --name watchtower \
    --restart unless-stopped \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --log-opt max-size=50m --log-opt max-file=2 \
    containrrr/watchtower --cleanup --interval 3600

# the dev version
touch $dev_config_json_file
docker run -d --name probe-dev \
    --restart unless-stopped \
    -v $dev_config_json_file:/project/config.json \
    $to_mount_default_config \
    --log-opt max-size=50m --log-opt max-file=2 \
    probe.yamucloud.com:8666/probe/dev:latest

# the prod version
touch $prod_config_json_file
docker run -d --name probe-prod \
    --restart unless-stopped \
    -v $prod_config_json_file:/project/config.json \
    $to_mount_default_config \
    --log-opt max-size=50m --log-opt max-file=2 \
    probe.yamucloud.com:8666/probe/prod:latest
