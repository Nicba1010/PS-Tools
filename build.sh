#!/usr/bin/env bash

plat=$(echo "$(uname)" | tr '[:upper:]' '[:lower:]')
echo "$plat"


cd dependencies/openssl
./config no-afalgeng no-async no-capieng no-cms no-comp no-ct no-dgram no-ec no-ec2m no-gost no-hw-pacdlock \
    no-nextprotoneg no-ocsp no-psk no-rdrand no-rfc3779 no-sock no-srp no-srtp no-ui no-ts no-ssl no-ssl3 no-tls \
    no-dtls no-aria no-bf no-blake2 no-camellia no-cast no-chacha no-cmac no-des no-dh no-dsa no-ecdh no-ecdsa \
    no-idea no-md4 no-mdc2 no-ocb no-poly1305 no-rc2 no-rc4 no-rmd160 no-scrypt no-seed no-siphash no-siv no-sm2 \
    no-sm3 no-sm4 no-whirlpool
make
cd ../..

gcc ./utils/xor.c /Users/troidozagreb2/PycharmProjects/PS-Tools/dependencies/openssl/libcrypto.a -shared -std=c99 -O3 -Idependencies/openssl/include -o "./utils/xor.$plat.lib"
pyinstaller --onefile --add-data "./utils/xor.$plat.lib":. --add-data "./format/pkg/naming_exceptions.txt":. pstools.py