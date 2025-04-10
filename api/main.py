from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trainee_routes, batch_routes, webhook_routes
from typing import List
app = FastAPI(title="10 Academy User API")

# CORS Settings
ALLOWED_ORIGINS: List[str] = [
    "http://0.0.0.0:8009",  
    "http://0.0.0.0:8008",  
    "https://user-management.10academy.org",  
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