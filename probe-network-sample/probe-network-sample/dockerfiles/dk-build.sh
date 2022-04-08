#!/bin/bash -

#  usage:
#  ./dk-build.sh [target] [push]
#  target: the target to build, choices are: dev prod
#  push: if exists, push images after docker image build succeeded

cd ..
echo "wait for getting current version ..."
current_version=$(mvn org.apache.maven.plugins:maven-help-plugin:3.1.0:evaluate -Dexpression=project.version -q -DforceStdout)
echo "* current version is $current_version"

target=$1
push=$2
version_tag="probe.yamucloud.com:8666/probe-network-sample/$target:$current_version"
latest_tag="probe.yamucloud.com:8666/probe-network-sample/$target:latest"

echo "maven clean and install dependencies..."
mvn -q clean install
echo "maven clean, build and package..."
mvn -q clean package
echo "building docker images ..."
docker build -t $version_tag -f dockerfiles/dockerfile ..
docker build -t $latest_tag -f dockerfiles/dockerfile ..

echo "==============================================
successfully built these tags:

$version_tag

$latest_tag

=============================================="

if [[ $push = "push" ]]; then
  echo "* now push the images to the docker repo ..."
  docker push $latest_tag
  docker push $version_tag
  echo "* since the images were pushed, clean local images ..."
  docker rmi $version_tag $latest_tag
fi

