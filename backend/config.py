import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)
load_dotenv()


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT = int(os.getenv("PORT", "5000"))

    # Database URL configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/news_brief_desk",
    )

    # JWT Secret
    JWT_SECRET = os.getenv("JWT_SECRET", "default-dev-secret-change-me")

    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # AI Pipeline Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    FAISS_CANDIDATE_THRESHOLD = float(os.getenv("FAISS_CANDIDATE_THRESHOLD", "0.60"))
    FAISS_TOP_K = int(os.getenv("FAISS_TOP_K", "10"))

    # CORS Configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://news-brief-desk.vercel.app")
    _cors_env = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS = [orig.strip().rstrip("/") for orig in _cors_env.split(",") if orig.strip()]
    if FRONTEND_URL:
        clean_frontend = FRONTEND_URL.strip().rstrip("/")
        if clean_frontend and clean_frontend not in CORS_ORIGINS:
            CORS_ORIGINS.append(clean_frontend)
    if "https://news-brief-desk.vercel.app" not in CORS_ORIGINS:
        CORS_ORIGINS.append("https://news-brief-desk.vercel.app")

