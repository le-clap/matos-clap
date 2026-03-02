"""Export the FastAPI OpenAPI schema to openapi.json."""

import json
from pathlib import Path

from main import app

output = Path(__file__).parent / "openapi.json"
output.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"OpenAPI schema written to {output}")
