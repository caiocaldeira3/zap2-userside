#!/bin/bash

python clean_user_keys.py

cd ../user
../scripts/clean_database.sh user
