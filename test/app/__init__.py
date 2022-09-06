from .app import lambda_handler, main, api, Config

api.config.from_object('app.Config')
