#!/bin/bash - 
#===============================================================================
#
#          FILE: gen-cert.sh
# 
#         USAGE: ./gen-cert.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2020/11/10 17:29
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

echo "generating CA cert for $1 ..."

mkdir -p "certs/$1"
cd "certs/$1"

openssl req \
    -new \
    -newkey rsa:2048 \
    -days 3650 \
    -nodes \
    -x509 \
    -subj "/C=CN/O=YAMU NETWORKS CO., Ltd/CN=$1" \
    -keyout root-ca.key \
    -out root-ca.crt

echo "generating certs for server ..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key \
    -out server.csr
openssl x509 -req \
 -days 3650 \
 -in server.csr \
 -CA root-ca.crt \
 -CAkey root-ca.key \
 -CAcreateserial \
 -out server.crt \
 -extensions v3_req \

echo "generating certs for client ..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=$1"
openssl x509 -req -days 3650 -in client.csr -CA root-ca.crt -CAkey root-ca.key -CAcreateserial -out client.crt

echo "verifying certs ..."
openssl verify -CAfile root-ca.crt server.crt
openssl verify -CAfile root-ca.crt client.crt

echo "done."