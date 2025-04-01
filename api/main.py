from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trainee_routes

app = FastAPI(title="10 Academy Trainee API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trainee_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 