import functions_framework

from app import api
from flask_serverless import gcp_invoke

@functions_framework.http
def invoke(request):
   return gcp_invoke(api,request)