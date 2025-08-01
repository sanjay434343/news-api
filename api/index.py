from vercel_python_wsgi import make_lambda_handler
from workspaces.logsy.main import app

handler = make_lambda_handler(app)
