#!/bin/bash

python clean_user_keys.py

cd ../server
../scripts/clean_database.sh server

cd ../user
../scripts/clean_database.sh user
