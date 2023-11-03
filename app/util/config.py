import fileinput
import os
import sys
from pathlib import Path

import dotenv
import regex as re

base_path = Path(__file__).resolve().parent.parent.parent
dotenv.load_dotenv(base_path / ".env", override=True)

sys.path.append(str(base_path))


# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MONGO_CONN = os.environ["MONGO_CONNECTION_STRING"]
MONGO_DB = os.environ["MONGO_DATABASE"]
CHAT_SECRET = os.environ["CHAT_SECRET"]
SECRET_KEY = os.environ["SECRET_KEY"]

USER_ID = os.environ["USER_ID"]

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "W1JKKarQaco3qtBhwfpToqIrK3ATRP9q"

# Secret key for signing cookies
SECRET_KEY = os.environ["SECRET_KEY"]

def update_user_id (value: str) -> None:
    global USER_ID
    environ_regex = re.compile(f"(?<=USER_ID=).*")
    os.environ["USER_ID"] = str(value)

    with fileinput.FileInput(base_path / ".env", inplace=True, backup=".bak") as env:
        for line in env:
            print(environ_regex.sub(f"{value}", line), end="")

    USER_ID = value