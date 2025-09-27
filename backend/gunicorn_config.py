from multiprocessing import cpu_count

import constants

bind = "0.0.0.0:8080"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# structlog Options

# change path before deploying this file
loglevel = 'debug'

# Whether to send fastapi output to the error log
capture_output = True

# Access log - records incoming HTTP requests
accesslog = constants.API_ACCESS_LOG

# Error log - records Gunicorn server goings-on
errorlog = constants.API_ERROR_LOG
