#!/usr/bin/python3
"""create a unique FileStorage instance for your application"""

import os
from dotenv import load_dotenv

load_dotenv()

storage_type = os.getenv("UMPIRE_TYPE_STORAGE", "file")

storage = None

if storage_type == "db":
    from backend.models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from backend.models.engine.file_storage import FileStorage
    storage = FileStorage()
storage.reload()