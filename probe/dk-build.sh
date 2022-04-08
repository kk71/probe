#!/bin/bash - 

#  usage:
#  ./dk-build.sh [target] [push]
#  target: the target to build, choices are: dev prod standalone
#  push: if exists, push images after docker image build succeeded

set -o nounset                              # Treat unset variables as an error


# record the path to dockerfiles
original_path=`pwd`
# all env for building the image is in a temporary folder
build_env_path="/tmp/probe-docker-image-build-env"
rm -rf $build_env_path
mkdir -p $build_env_path
cp -r . $build_env_path
cd $build_env_path

# get the current version
ver=`cat ./VERSION`

# since within the temp build-env, the dockerfiles will be deleted,
# so we should use the original dockerfile
tag="probe.yamucloud.com:8666/probe/$1:$ver"
latest_tag="probe.yamucloud.com:8666/probe/$1:latest"
docker_file="$original_path/dockerfiles/Dockerfile.$1"

echo "* build $1 image for probe ..."
echo "* run prerun.sh before build ..."
./dockerfiles/prerun.sh
docker build -t $tag -f $docker_file .
docker build -t $latest_tag -f $docker_file .

echo "
========================================================================
successfully built images as

  $tag

  $latest_tag

========================================================================
"

if [[ "$2" = "push" ]]; then
  echo "* now push the images to the docker repo ..."
  docker push $tag
  docker push $latest_tag
  echo "* since the images were pushed, clean local images ..."
  docker rmi $tag $latest_tag
fi
