from vercel_python_wsgi import make_lambda_handler
from main import app

handler = make_lambda_handler(app)
