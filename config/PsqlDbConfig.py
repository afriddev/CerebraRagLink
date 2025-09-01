# config/PsqlDbConfig.py

import os
from dbservices import PsqlDb
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING", "")

psqlDb = PsqlDb(DATABASE_CONNECTION_STRING)
