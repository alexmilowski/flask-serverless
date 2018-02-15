from flask import Flask,request,jsonify
from werkzeug.http import parse_options_header
from flask_serverless import aws_invoke
import json

app = Flask(__name__)

class Config(object):
   DEBUG=True

app.config.from_object('test_aws.Config')

@app.route('/')
def index():
   return 'Hello!'

@app.route('/echo',methods=['GET','HEAD','POST','PUT','DELETE','OPTIONS'])
def echo():
   obj = {
     'method' : request.method,
     'headers' : dict(request.headers)
   }
   if request.method=='POST' or request.method=='PUT':
      contentType = parse_options_header(request.headers.get('Content-Type','application/octet-stream'))
      encoding = contentType[1].get('charset','utf-8')
      obj['data'] = request.data.decode(encoding)
   return jsonify(obj)

def lambda_handler(event, context):
   return aws_invoke(app,event)

if __name__ == '__main__':
   event = '''
{
"resource": "/echo",
"path": "/echo",
"httpMethod": "GET",
"headers": {
   "X-Forwarded-For": "10.0.0.128, 10.0.0.1"
},
"queryStringParameters": null,
"pathParameters": null,
"stageVariables": null,
"requestContext": {
"path": "/echo",
"accountId": "419393064696",
"resourceId": "fn5qyr",
"stage": "test-invoke-stage",
"requestId": "test-invoke-request",
"identity": {
   "cognitoIdentityPoolId": null,
   "cognitoIdentityId": null,
   "apiKey": "test-invoke-api-key",
   "cognitoAuthenticationType": null,
   "userArn": "arn:aws:iam::419393064696:root",
   "apiKeyId": "test-invoke-api-key-id",
   "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_144)",
   "accountId": "419393064696",
   "caller": "419393064696",
   "sourceIp": "test-invoke-source-ip",
   "accessKey": "ASIAIW5XC4QRG736NVQA",
   "cognitoAuthenticationProvider": null,
   "user": "419393064696"
},
"resourcePath": "/echo",
"httpMethod": "GET",
"apiId": "4a6ywoxe5a"
},
"body": null,
"isBase64Encoded": false
}
'''
   print(json.dumps(lambda_handler(json.loads(event),None)))
