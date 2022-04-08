#!/bin/bash -

set -o nounset                              # Treat unset variables as an error

chmod a+rw ./redis-data

mkdir -p es/log
mkdir -p es/data

chmod a+rwx es/log
chgrp 1000 es/log

chmod a+rwx es/data
chgrp 1000 es/data

chmod a+r es-x-pack-keys/*
chmod a+rwx es/log
chgrp 1000 es/log

chmod a+rwx es/data
chgrp 1000 es/data

chmod a+r es-x-pack-keys/*
