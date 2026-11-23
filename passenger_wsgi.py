import sys
from pathlib import Path

# Ensure project root is on sys.path for `src.api` imports under Phusion Passenger
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from a2wsgi import ASGIMiddleware
from src.api import app

# Expose WSGI callable for cPanel / Phusion Passenger
application = ASGIMiddleware(app)
