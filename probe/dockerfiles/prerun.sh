#!/bin/sh

# will be run before image is built.
# do some cleaning work here.
# the working folder is temporarily copied from the source folder

git clean -xdf .
rm -rf .git
rm -rf .gitignore
rm -rf version-man.py
rm -rf dk-build.sh
rm -rf dockerfiles
rm -rf TAG
rm -rf config.json
rm -rf config.default.json
