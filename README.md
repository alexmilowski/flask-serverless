# Going Serverless with Flask

This repository contains a simple integration layer for serverless.  The code currently works with AWS lambda_handler
but I have a version for [OpenWhisk](https://github.com/alexmilowski/flask-openwhisk) that I plan on integrating. I am
using the AWS version in production!

# Getting Started

The package is `flask_serverless` and there is an example in `test_aws.py`.  The invocation is simple:


```python
from flask import Flask
from flask_serverless import aws_invoke

app = Flask(__name__)

# ... app configuration ...

# The AWS Lambda Handler function
def lambda_handler(event, context):
   return aws_invoke(app,event)   
```

If you want all the AWS Lambda request headers to go through to the application, just add the `block_headers` parameter:

```python
def lambda_handler(event, context):
   return aws_invoke(app,event,block_headers=False)
```   

# API

There is one function `aws_invoke`:

```python
def aws_invoke(app,gateway_input,server_name='localhost',server_port='5000',http_protocol='HTTP/1.1',TLS=True,block_headers=True):
```

The server name, port, and protocol will be pulled from the various forwarded headers.  If you want to change the defaults, you can
use the corresponding keyword parameters.  The `TLS` parameter controls whether the default protocol is `http` vs `https` but, again,
the protocol is pulled from the forwarded headers from AWS Lambda.

# AWS Lambda Functions

Your flask application needs to be constructed and invoked by the `aws_invoke` function.  There should be one main python script
that constructs the flask application and invokes aws_invoke (e.g., `production.py`):

```
def lambda_handler(event, context):
   return aws_invoke(app,event,block_headers=False)
```

Then the AWS lambda function handler is called `production.lambda_handler` when you configure the function in the AWS console or
via the CLI.

The process of actually creating the lambda function is rather simple and most of the complexity is in the packaging.  The packaging
requires a zip file that contains:

  * your flask applications
  * your application's required packages (e.g., flask!)
  * the `flask_serverless` package

While you can read more about packaging in the
[AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html), all
the supporting code needs to be in the root level of a zip file along with your application code and the handler function.

Assuming your code is in the current directory and the `flask_serverless` package is in a sibling directory, this
script will package a zip file for you:

```bash
#!/bin/bash
rm -rf dist
mkdir dist
cd dist
virtualenv env
source activate env
pip install -r ../requirements.txt
mkdir package
cp -r env/lib/python3.6/site-packages/* package
cp -r ../../flask-serverless/flask_serverless package
cp ../*.py package
find package -name __pycache__ -exec rm -rf {} \;
rm ../lambda.zip
cd package
zip -r ../../lambda.zip .
```

You can then upload the `lambda.zip` file to your AWS Lambda function. Make sure you adjust the handler function name to match your
invocation.


# API Gateway Proxy

All you need to do is forward any method to the flask application via the API Gateway. This is done by:

  1. Create an API for the application.
  2. Create a '/' resource and an 'ANY' method that maps to a Lambda Proxy for your flask lambda function.
  3. Create a '/{proxy+}' resource and an 'ANY' method that maps to a Lambda Proxy for your flask lambda function.
  4. Deploy your API to a stage.

Keep in mind that the URL paths may not match your Flask applications expectations. You can do various tricks with the API gateway's
"Custom Domain Names" to map the deployment stage URL path to the root path if necessary.


# Presentations

My talk from the SF Microservices Meetup (2017-07-11) and
other notes about using Flask on FaaS / Serverless infrastructure.
