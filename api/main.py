import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from loguru import logger
from dotenv import load_dotenv

# Import Config and Routes
from api.config import get_settings
from api.routes import training, unlearning, verification, certificates, datasets

# Load environment variables from .env file
load_dotenv()

settings = get_settings()

def create_app() -> FastAPI:
    """
    Application Factory for Amnesia VMUaaS.
    Initializes the API, Middleware, and Routes.
    """
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Enterprise Machine Unlearning Platform (SISA Architecture)",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # 1. CORS Middleware
    # Essential so your Streamlit/React dashboard can communicate with this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Prometheus Metrics Middleware
    # Exposes /metrics endpoint for Grafana/Prometheus to scrape
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # 3. Register Routes
    # We prefix everything with /api/v1 (good practice for versioning)
    api_router = settings.API_V1_STR
    
    app.include_router(training.router, prefix=f"{api_router}/models", tags=["Training"])
    app.include_router(unlearning.router, prefix=f"{api_router}/data", tags=["Unlearning"])
    app.include_router(verification.router, prefix=f"{api_router}/verify", tags=["Verification"])
    app.include_router(certificates.router, prefix=f"{api_router}/certificates", tags=["Certificates"])
    app.include_router(datasets.router, prefix=f"{api_router}/datasets", tags=["Datasets"])

    # 4. Startup Events
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"🚀 {settings.APP_NAME} Starting up...")
        logger.info(f"📂 Storage Root: {settings.STORAGE_ROOT}")
        
        # Ensure necessary storage directories exist
        os.makedirs(settings.MODEL_STORAGE, exist_ok=True)
        os.makedirs(settings.DATA_STORAGE, exist_ok=True)
        os.makedirs(settings.CERT_STORAGE, exist_ok=True)
        
        # Initialize database tables
        try:
            from storage.database import Base, engine
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database init skipped: {e}")

    # 5. Health Check
    @app.get("/health", tags=["System"])
    def health_check():
        return {
            "status": "active", 
            "version": "1.0.0", 
            "architecture": "SISA", 
            "monitoring": "Prometheus Enabled"
        }

    return app

# Create the app instance
app = create_app()

def run_server():
    """
    Entry point for console_scripts in setup.py
    Allows running the server via the command: `amnesia`
    """
    uvicorn.run(
        "api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG_MODE
    )

if __name__ == "__main__":
    run_server()