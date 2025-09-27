import os
from os import environ

import dotenv

env_filename = ".env"
dotenv.load_dotenv()

BATCH_SIZE = int(environ.get('BATCH_SIZE'))
GA_DAY_DATA = int(environ.get('GA_DAY_DATA'))
ENCRYPTION_KEY = environ.get('ENCRYPTION_KEY')
