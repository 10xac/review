from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from api.routes import trainee_routes, batch_routes, webhook_routes
from api.core.error_handlers import validation_exception_handler, pydantic_validation_exception_handler
from typing import List

app = FastAPI(title="10 Academy User API")

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)

# CORS Settings
ALLOWED_ORIGINS: List[str] = [
    # "http://localhost:8009",  
    # "http://localhost:8008",
    # "http://127.0.0.1:8009",
    # "http://127.0.0.1:8008",
    "https://tenx.gettenacious.com",
    "https://tenx.10academy.org", 
    "https://dev-tenx.10academy.org",
    "https://kaimtenx.10academy.org"
]
    
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trainee_routes.router)
app.include_router(batch_routes.router)
app.include_router(webhook_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 