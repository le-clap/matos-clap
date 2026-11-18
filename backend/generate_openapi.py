"""Export the FastAPI OpenAPI schema to openapi.json."""

import json
import os
from pathlib import Path

# Production mode tries to serve the built frontend from ./static, which doesn't necessarily exist.
os.environ.setdefault("ENV", "development")

from main import app  # noqa: E402

output = Path(__file__).resolve().parent / "openapi.json"
output.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"OpenAPI schema written to {output}")
