import sys
from pathlib import Path

# Add Backend folder to sys.path so app modules and routers resolve properly
backend_dir = Path(__file__).resolve().parent.parent / "Backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
