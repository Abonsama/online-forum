import asyncio
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.core.db import engine
from app.api.routes import api_router
from app.core.config import Environment, settings
from app.core.logger import cleanup_logging, configure_logging
from app.core.seeders import create_initial_data
from app.middleware.logging import LoggingMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis.asyncio import Redis


@asynccontextmanager
async def get_db_context():
    """Get database context for lifespan events"""
    async_session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def run_once_across_workers():
    """Run initialization tasks only once across multiple workers"""
    if settings.current_environment == Environment.LOCAL:

        # In development, always run (single worker usually)
        async with get_db_context() as db:
            await create_initial_data(db)
        return

    # Use Redis for coordination in production
    redis_client = None
    try:
        redis_client = Redis.from_url(
            settings.redis_url.human_repr(), decode_responses=True, socket_timeout=5
        )

        # Try to acquire a lock with expiration
        lock_key = "superfit:initialization:lock"
        completed_key = "superfit:initialization:completed"

        # Check if initialization is already completed
        if await redis_client.get(completed_key):
            logger.info("Initialization already completed by another worker")
            return

        # Try to acquire lock for 30 seconds
        if await redis_client.set(lock_key, "locked", nx=True, ex=30):
            logger.info("Acquired initialization lock, running seed data...")

            try:
                # Double-check if another worker completed it while we were waiting
                if await redis_client.get(completed_key):
                    logger.info("Initialization completed by another worker while acquiring lock")
                    return

                # Run the initialization
                async with get_db_context() as db:
                    await create_initial_data(db)

                # Mark as completed (expires in 5 minutes)
                await redis_client.set(completed_key, "done", ex=300)
                logger.info("Initialization completed successfully")

            finally:
                # Release the lock
                await redis_client.delete(lock_key)
        else:
            # Wait for other worker to complete
            logger.info("Another worker is handling initialization, waiting...")

            # Wait up to 60 seconds for completion
            for _ in range(60):
                if await redis_client.get(completed_key):
                    logger.info("Initialization completed by another worker")
                    return
                await asyncio.sleep(1)

            logger.warning("Initialization timeout - proceeding anyway")

    except Exception as e:
        logger.error(f"Redis coordination failed: {e}")
        logger.info("Falling back to running initialization without coordination")
        async with get_db_context() as db:
            await create_initial_data(db)
    finally:
        if redis_client is not None:
            await redis_client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""

    logger.info("Initializing resources...")
    await configure_logging()
    await run_once_across_workers()
    logger.success("Resources initialized.")

    yield  # Application runs here

    logger.info("Cleaning up resources...")
    await cleanup_logging()
    logger.success("Resources cleaned up.")


ALLOWED_ENVIRONMENTS = {Environment.LOCAL, Environment.DEV, Environment.STG}

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=settings.app_description,
    openapi_url=("/openapi.json" if settings.current_environment in ALLOWED_ENVIRONMENTS else None),
    docs_url="/docs" if settings.current_environment in ALLOWED_ENVIRONMENTS else None,
    redoc_url=("/redoc" if settings.current_environment in ALLOWED_ENVIRONMENTS else None),
    lifespan=lifespan,
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}",
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Set logging middleware
app.add_middleware(LoggingMiddleware)

# Include API router
app.include_router(api_router)
