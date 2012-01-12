#!/bin/bash

#Start a mongrel2 fot the functional tests

dir=`dirname $0`

cd ${dir}
cd m2env
mkdir -p logs
mkdir -p tmp
mkdir -p run

mongrel2 config.sqlite f400bf85-4538-4f7a-8908-67e313d515c2
