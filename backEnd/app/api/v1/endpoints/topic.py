from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import repos
from app.api.v1.deps.auth import get_current_user
from app.core.db import get_session
from app.models import User, UserRoleEnum as UserRoleEnumModel
from app.services.topic_service import TopicService
from app.schemas import TopicDetailedResponse, TopicCreate
from app.core.exceptions import http_exceptions

router = APIRouter()


@router.post(
    "/",
    summary="Create a new topic (admin only 👮)",
    description="Create a new topic. Authentication required.",
    response_model=TopicDetailedResponse,
)
async def create_topic(
    db: Annotated[AsyncSession, Depends(get_session)],
    new_topic: TopicCreate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Only admins can create topics
    if current_user.role != UserRoleEnumModel.ADMIN:
        raise http_exceptions.ForbiddenException("Only admins can create new topics.")

    # Check for existing topic with same name or slug
    existing_topic = await repos.TopicRepo(db).get_by_name_or_slug(
        name=new_topic.name,
        slug=new_topic.slug,
    )

    if existing_topic:
        raise http_exceptions.ConflictException("Topic with the same name or slug already exists.")

    # Create the new topic
    topic_new = await repos.TopicRepo(db).create_one(new_topic)
    return TopicDetailedResponse(
        id=topic_new.id,
        name=topic_new.name,
        slug=topic_new.slug,
        description=topic_new.description,
        is_active=topic_new.is_active,
        post_count=0,
        created_at=topic_new.created_at,
    )


@router.get(
    "/",
    response_model=list[TopicDetailedResponse],
    summary="Get all topics",
    description="Retrieve all topics with post counts. No authentication required.",
)
async def get_topics(
    db: Annotated[AsyncSession, Depends(get_session)],
    only_active: bool = True,
):
    """
    Get all topics with their post counts.

    Returns:
        - topics: List of topics with id, name, slug, description, is_active, post_count
    """
    all_topics: list[TopicDetailedResponse] = []

    async for topic in TopicService(db).get_all_with_counts(only_active=only_active):
        all_topics.append(
            TopicDetailedResponse(
                id=topic.get("id"),
                name=topic.get("name"),
                slug=topic.get("slug"),
                description=topic.get("description"),
                is_active=topic.get("is_active"),
                post_count=topic.get("post_count"),
                created_at=topic.get("created_at"),
            )
        )

    return all_topics
