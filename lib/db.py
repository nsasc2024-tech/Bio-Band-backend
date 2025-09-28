import os
from libsql_experimental import create_client

db = create_client(
    url=os.getenv("TURSO_DB_URL"),
    auth_token=os.getenv("TURSO_DB_TOKEN")
)