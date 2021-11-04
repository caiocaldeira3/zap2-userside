import sys

from pathlib import Path

base_path = Path(__file__).resolve().parent.parent
sys.path.append(str(base_path / "user/"))

from app.util.crypto import clean_keys

clean_keys()
