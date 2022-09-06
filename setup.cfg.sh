#!/bin/bash
VERSION=`python -c "import flask_serverless; print('.'.join(map(str,flask_serverless.__version__)))"`
AUTHOR=`python -c "import flask_serverless; print(flask_serverless.__author__)"`
EMAIL=`python -c "import flask_serverless; print(flask_serverless.__author_email__)"`
DESCRIPTION="A flask serverless integration"
REQUIRES=`python -c "list(map(print,['\t'+line.strip() for line in open('requirements.txt', 'r').readlines()]))"`
cat <<EOF > setup.cfg
[metadata]
name = flask_serverless
version = ${VERSION}
author = ${AUTHOR}
author_email = ${EMAIL}
description = ${DESCRIPTION}
license = Apache License 2.0
url = https://github.com/alexmilowski/flask-serverless

[options]
packages =
   flask_serverless
include_package_data = True
install_requires =
${REQUIRES}

[options.package_data]
* = *.json, *.yaml

EOF
