
def gcp_invoke(app,request):

   context = app.test_request_context(path=request.full_path,method=request.method,headers=dict(request.headers))
   context.request.stream = request.stream

   context.push()
   response = app.full_dispatch_request()
   context.pop()
    
   return response