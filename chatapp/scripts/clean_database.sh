#!/bin/bash

cd ../$1
rm app.db -r migrations
flask db init
flask db migrate -m "Initial Migration"
flask db stamp head
flask db upgrade
