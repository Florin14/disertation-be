#!/bin/sh
PRIVATE="private-key.pem"
PUBLIC="public-key.pem"
mkdir -p $1
rm -f "$1/$PRIVATE"
rm -f "$1/$PUBLIC"
openssl genrsa -out "$1/$PRIVATE" 1024
openssl rsa -in "$1/$PRIVATE" -out "$1/$PUBLIC" -pubout -outform PEM
