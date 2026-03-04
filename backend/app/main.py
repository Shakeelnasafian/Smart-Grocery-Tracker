import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app import models, database
from app.routers import grocery, auth, analytics, budget, shopping, alerts, food_api, recipes
from app.scheduler import start_scheduler, stop_scheduler

# ── Logging ───────────────────────────────────────────────────────────────────
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": (
                    '{"time": "%(asctime)s", "level": "%(levelname)s",'
                    ' "logger": "%(name)s", "message": "%(message)s"}'
                ),
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
)

logger = logging.getLogger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ── App Lifespan ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
    start_scheduler()
    logger.info("Smart Grocery Tracker API started")
    yield
    stop_scheduler()
    logger.info("Smart Grocery Tracker API stopped")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Smart Grocery Tracker API",
    description=(
        "A full-featured grocery management API with authentication, analytics, "
        "budget tracking, shopping list generation, expiry alerts, and food database integration."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(grocery.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(shopping.router)
app.include_router(alerts.router)
app.include_router(food_api.router)
app.include_router(recipes.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Smart Grocery Tracker API v2.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
