"""
Export OpenAPI schema for Football Player Service.

Generates a JSON schema file that can be used for:
- Client code generation (openapi-generator, swagger-codegen)
- API documentation (swagger-ui, redoc)
- Contract testing (schemathesis, dredd)
- Validation and monitoring
"""
import json
from pathlib import Path

from football_player_service.app.main import app


# Generate OpenAPI schema from FastAPI app
schema = app.openapi()

# Create output directory (inside package for cleaner structure)
contracts_dir = Path("football_player_service/contracts")
contracts_dir.mkdir(parents=True, exist_ok=True)

# Write schema to file
output_path = contracts_dir / "openapi.json"
output_path.write_text(json.dumps(schema, indent=2))

# Print summary
print(f"Exported OpenAPI schema to {output_path}")
print(f"  Title: {schema['info']['title']}")
print(f"  Version: {schema['info']['version']}")
print(f"  Endpoints: {len(schema['paths'])}")
print(f"\nUse this file to:")
print(f"  - Generate client SDKs (Python, TypeScript, Java, etc.)")
print(f"  - Validate API responses in tests")
print(f"  - Generate interactive documentation")
print(f"  - Monitor API contract compliance")

