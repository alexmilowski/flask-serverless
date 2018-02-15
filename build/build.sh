#!/bin/bash
rm -rf dist
mkdir dist
cp -r env/lib/python3.6/site-packages/* dist
cp -r ../flask_serverless dist
cp -r ../test_aws.py dist
find dist -name __pycache__ -exec rm -rf {} \;
rm lambda.zip
cd dist; zip -r ../lambda.zip .
