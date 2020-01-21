from flask import Response
from base64 import b64decode,b64encode
from werkzeug.http import parse_options_header
import sys,io
from urllib.parse import urlencode
from requests.structures import CaseInsensitiveDict

textTypes = set(['application/json','application/ld+json','application/json-seq','application/xml'])

def add_body(environ,body,contentType):
   environ['CONTENT_TYPE'] = contentType
   if body:
      environ['wsgi.input'] = io.BytesIO(body)
      environ['CONTENT_LENGTH'] = str(len(body))
   else:
      environ['wsgi.input'] = None
      environ['CONTENT_LENGTH'] = '0'

# TODO: necessary?
block = set(['x-amz-cf-id','x-amzn-trace-id','x-forwarded-for','x-forwarded-proto','x-forwarded-port'])

def add_headers(environ,headers,block_headers=True):
   for header in headers:
      if not block_headers or header.lower() not in block:
         wsgi_name = "HTTP_" + header.upper().replace('-', '_')
         environ[wsgi_name] = str(headers[header])

def aws_invoke(app,gateway_input,server_name='localhost',server_port='5000',http_protocol='HTTP/1.1',TLS=True,block_headers=True):
   headers = CaseInsensitiveDict(gateway_input.get('headers',{}))
   requestContext = gateway_input.get('requestContext')
   queryStringParameters = gateway_input.get('queryStringParameters',{})
   clientIp = headers.get('x-forwarded-for')
   if clientIp is None:
      clientIp = requestContext.get('identity',{}).get('sourceIp') if requestContext is not None else ''
   else:
      clientIp = clientIp.split(',')[0]
   environ = {
      'REQUEST_METHOD': gateway_input.get('httpMethod','GET').upper(),
      'SCRIPT_NAME': '',
      'PATH_INFO': gateway_input.get('path','/'),
      'QUERY_STRING': urlencode(queryStringParameters) if queryStringParameters is not None else '',
      'SERVER_NAME': headers.get('host',server_name),
      'SERVER_PORT': headers.get('x-forwarded-port',server_port),
      'SERVER_PROTOCOL': http_protocol,
      'SERVER_SOFTWARE': 'flask-serverless',
      'REMOTE_ADDR': clientIp,
      'wsgi.version': (1, 0),
      'wsgi.url_scheme': headers.get('x-forwarded-proto','https' if TLS else 'http'),
      'wsgi.input': None,
      'wsgi.errors': sys.stderr,
      'wsgi.multiprocess': True,
      'wsgi.multithread': False,
      'wsgi.run_once': True,
      'HTTP_X_AWS_PATH' : requestContext['path']
   }

   if environ['REQUEST_METHOD']=='POST' or environ['REQUEST_METHOD']=='PUT':
      contentType = headers.get('content-type','application/octet-stream')
      parsedContentType = parse_options_header(contentType)
      raw = gateway_input.get('body')
      if raw is None or gateway_input.get('isBase64Encoded',False):
         body = b64decode(raw) if raw is not None else None
      else:
         body = raw.encode(parsedContentType[1].get('charset','utf-8'))
      add_body(environ,body,contentType)

   add_headers(environ,headers,block_headers)

   response = Response.from_app(app.wsgi_app, environ)

   gateway_output = {
      'headers' : dict(response.headers),
      'statusCode' : response.status_code,
   }

   compressed = response.headers.get('Content-Encoding')=='gzip'

   responseType = parse_options_header(response.headers.get('Content-Type','application/octet-stream'))
   if not compressed and ('charset' in responseType[1] or responseType[0] in textTypes or responseType[0][0:5]=='text/'):
      gateway_output['body'] = response.data.decode(responseType[1].get('charset','utf-8'))
      gateway_output['isBase64Encoded'] = False
   else:
      gateway_output['body'] = b64encode(response.data).decode('utf-8')
      gateway_output['isBase64Encoded'] = True

   return gateway_output
