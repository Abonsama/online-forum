from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import repos
from app.core.auth import get_password_hash
from app.core.config import settings
from app.schemas import UserCreate


async def create_initial_data(db: AsyncSession) -> None:
    """
    Create initial data for the application.
    Args:
        db: Database session
    """
    logger.info("Running initial data")
    await create_default_users(db)
    logger.success("Finished initial data")


async def create_default_users(db: AsyncSession) -> None:
    # Check if admin user exists
    admin = await repos.UserRepo(db).get_by_username(settings.admin_username)

    if not admin:
        new_user = UserCreate(
            username=settings.admin_username,
            email=settings.admin_email,
            hashed_password=get_password_hash(settings.admin_password),
            first_name=settings.admin_first_name,
            last_name=settings.admin_last_name,
        )
        await repos.UserRepo(db).create_one(new_user)
        logger.info("Admin user created")
