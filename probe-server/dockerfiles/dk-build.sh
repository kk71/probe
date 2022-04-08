#!/bin/sh

#  usage:
#  ./dk-build.sh [dev/prod] [push]
#  target: the target to build, choices are: dev prod
#  push: if exists, push images after docker image build succeeded

#set -o nounset  # Treat unset variables as an error

# record the current path
original_path=`pwd`
# get the current version
ver=`cat ../VERSION`
cd ..

# all env for building the image is in a temporary folder
build_env_path="/tmp/probe-server-docker-image-build-env"
rm -rf $build_env_path
mkdir -p $build_env_path
cp -r . $build_env_path
cd $build_env_path

# docker image tags
target=$1
push=$2||push=""
version_tag="probe.yamucloud.com:8666/probe-server/$target:$ver"
latest_tag="probe.yamucloud.com:8666/probe-server/$target:latest"

echo "* building image as target $target ..."
echo "* run standalone_prerun.sh before build ..."
./dockerfiles/standalone_prerun.sh
docker build -t $version_tag -f $original_path/dockerfile .
docker build -t $latest_tag -f $original_path/dockerfile .

echo "
========================================================================
successfully built images as

  $version_tag

  $latest_tag

>>> DO remember to change your docker-compose.yml <<<
========================================================================
"

if [[ "$push" = "push" ]]; then
  echo "* now push the images to the docker repo ..."
  docker push $version_tag
  docker push $latest_tag
  echo "* since the images were pushed, clean local images ..."
  docker rmi $version_tag $latest_tag
fi
