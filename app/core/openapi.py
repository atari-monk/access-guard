from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def setup_openapi(app: FastAPI) -> None:
    """
    Custom OpenAPI schema to enable JWT Bearer authentication in Swagger.
    Adds 'Authorize' button and applies security to all protected endpoints.
    """
    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        # Generate default schema
        openapi_schema = get_openapi(
            title="AccessGuard",
            version="1.0.0",
            description="""
AccessGuard – Role-Based Access Control (RBAC) API

### Features
- 🔐 JWT Authentication (OAuth2 Bearer)
- 👤 User registration & login
- 🧩 Role assignment
- 🔑 Permission management & checks

### Authentication
1. Register a user
2. Login to obtain JWT token
3. Click **Authorize** in Swagger
4. Paste: `Bearer <your_token>`
""",
            routes=app.routes,
        )

        # 🔐 Add JWT BearerAuth security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        # 🔒 Apply security to all non-auth endpoints
        for path, path_value in openapi_schema["paths"].items():
            for _method, endpoint in path_value.items():
                if path not in ["/auth/register", "/auth/login"]:
                    endpoint["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
