import time
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import get_current_user, get_current_user_optional
from app.core import responses
from app.core.db import get_session
from app.core.exceptions.http_exceptions import TooManyRequestsException
from app.models.user import User
from app.schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    VoteRequest,
    ReportCreate,
    PostDetailedResponse,
    PostFeedResponse,
    PostSearchResponse,
)
from app.services.cache.rate_limiter import rate_limiter
from app.services.post_service import PostService
from app.services.report_service import ReportService
from app.services.vote_service import VoteService

router = APIRouter()


@router.get(
    "/",
    response_model=PostDetailedResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": responses.InternalServerErrorResponse},
    },
    summary="Get posts feed",
    description="Retrieve paginated feed of posts with sorting options. "
    "Authentication is optional - if authenticated, user_vote field is included.",
)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
    sort: Literal["hot", "new", "top"] = Query(
        "hot", description="Sort method: hot (default), new, or top"
    ),
    topic_id: int | None = Query(None, description="Filter by topic ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
):
    """
    Get posts feed with pagination and sorting.

    Query Parameters:
        - sort: Sorting method (hot, new, top)
        - topic_id: Filter posts by topic
        - limit: Maximum posts to return (1-100)
        - offset: Number of posts to skip for pagination

    Returns:
        - posts: List of posts
        - total: Number of posts returned
        - has_more: Whether more posts are available
    """
    service = PostService(db)

    # Get posts feed with user votes if authenticated
    topic_ids = [topic_id] if topic_id else None

    posts = await service.get_feed(
        sort=sort,
        topic_ids=topic_ids,
        skip=offset,
        limit=limit + 1,  # Fetch one extra to check has_more
        current_user_id=current_user.id if current_user else None,
    )

    has_more = len(posts) > limit
    posts = posts[:limit]

    return PostDetailedResponse(
        posts=[
            PostFeedResponse(**post.to_dict(exclude_keys={"is_deleted", "updated_at"}))
            for post in posts
        ],
        total=len(posts),
        has_more=has_more,
    )


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": responses.BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": responses.UnauthorizedResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": responses.TooManyRequestsResponse},
    },
    summary="Create a new post",
    description="Create a new post with 1-5 topics. Requires authentication. "
    "Rate limited to 10 posts per hour.",
)
async def create_post(
    data: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
    response: Response,
):
    """
    Create a new post.

    Rate Limit: 10 posts per hour per user

    Request Body:
        - title: Post title (5-300 characters)
        - content: Post content (minimum 10 characters)
        - topic_ids: List of 1-5 topic IDs

    Returns:
        Created post object
    """
    # Rate limiting: 10 posts per hour
    key = rate_limiter.build_rate_limit_key("post", "create", f"user:{current_user.id}")
    is_allowed, info = await rate_limiter.check_rate_limit(key, limit=10, window=3600)

    if not is_allowed:
        raise TooManyRequestsException(
            detail=f"Rate limit exceeded. Try again in {info['reset_time'] - int(time.time())} seconds",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
            },
        )

    # Add rate limit headers to successful response
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_time"])

    # Create post
    service = PostService(db)
    post = await service.create_post(current_user.id, data)
    await db.commit()
    await db.refresh(post)

    return post


@router.get(
    "/search",
    response_model=PostSearchResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": responses.BadRequestResponse},
    },
    summary="Search posts",
    description="Search posts by title and content. Minimum query length is 3 characters.",
)
async def search_posts(
    db: Annotated[AsyncSession, Depends(get_session)],
    q: str = Query(..., min_length=3, description="Search query (minimum 3 characters)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """
    Search posts by title and content.

    Query Parameters:
        - q: Search query (minimum 3 characters)
        - limit: Maximum results to return (1-100)
        - offset: Number of results to skip

    Returns:
        - posts: List of matching posts
        - query: The search query used
        - total: Number of results returned
    """
    service = PostService(db)
    posts = await service.search_posts(
        query=q,
        skip=offset,
        limit=limit + 1,  # fetch one extra to check has_more
    )

    return PostSearchResponse(
        posts=[
            PostFeedResponse(
                id=post_item.id,
                user_id=post_item.user_id,
                title=post_item.title,
                content=post_item.content,
                vote_count=post_item.vote_count,
                view_count=post_item.view_count,
                comment_count=post_item.comment_count,
                created_at=post_item.created_at,
            )
            for post_item in posts[:limit]
        ],
        query=q,
        total=len(posts) - 1 if len(posts) > limit else len(posts),
        has_more=len(posts) > limit,
    )


@router.get(
    "/{id}",
    response_model=PostResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": responses.NotFoundResponse},
    },
    summary="Get a single post",
    description="Retrieve detailed information about a specific post. "
    "View count is automatically incremented (except for post author).",
)
async def get_post(
    id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
):
    """
    Get a single post by ID.

    View count is incremented automatically unless:
    - User is not authenticated, OR
    - User is the post author

    Returns:
        Post object with user and topics loaded
    """
    service = PostService(db)
    post = await service.get_post_detail(id)

    # Increment view count if user is not the author
    if not current_user or current_user.id != post.user_id:
        await service.increment_view_count(id)
        await db.commit()

    return post


@router.put(
    "/{id}",
    response_model=PostResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": responses.BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": responses.UnauthorizedResponse},
        status.HTTP_403_FORBIDDEN: {"model": responses.ForbiddenResponse},
        status.HTTP_404_NOT_FOUND: {"model": responses.NotFoundResponse},
    },
    summary="Update a post",
    description="Update an existing post. Only the post owner can update it.",
)
async def update_post(
    id: int,
    data: PostUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update a post (owner only).

    Request Body:
        - title: Updated title (optional)
        - content: Updated content (optional)
        - topic_ids: Updated topic IDs (optional, 1-5)

    Returns:
        Updated post object
    """
    service = PostService(db)
    post = await service.update_post(id, current_user.id, data)
    await db.commit()
    await db.refresh(post)

    return post


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": responses.UnauthorizedResponse},
        status.HTTP_403_FORBIDDEN: {"model": responses.ForbiddenResponse},
        status.HTTP_404_NOT_FOUND: {"model": responses.NotFoundResponse},
    },
    summary="Delete a post",
    description="Soft delete a post. Post owner or moderators/admins can delete.",
)
async def delete_post(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Delete a post (soft delete).

    Authorization:
        - Post owner can delete their own posts
        - Moderators and admins can delete any post

    Returns:
        Success message
    """
    service = PostService(db)
    await service.delete_post(id, current_user.id, current_user.role)
    await db.commit()

    return {"message": "Post deleted successfully"}


@router.post(
    "/{id}/vote",
    response_model=dict,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": responses.UnauthorizedResponse},
        status.HTTP_404_NOT_FOUND: {"model": responses.NotFoundResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": responses.TooManyRequestsResponse},
    },
    summary="Vote on a post",
    description="Upvote or downvote a post. Clicking the same vote again removes it. "
    "Rate limited to 100 votes per hour.",
)
async def vote_on_post(
    id: int,
    vote_data: VoteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
    response: Response,
):
    """
    Vote on a post.

    Rate Limit: 100 votes per hour per user

    Vote Logic:
        - vote = 1: Upvote (clicking again removes upvote)
        - vote = -1: Downvote (clicking again removes downvote)
        - vote = 0: Explicitly remove vote

    Request Body:
        - vote: 1 (upvote), -1 (downvote), or 0 (remove vote)

    Returns:
        - vote_count: New vote count for the post
        - user_vote: User's current vote (1, -1, or null)
    """
    # Rate limiting: 100 votes per hour
    key = rate_limiter.build_rate_limit_key("post", "vote", f"user:{current_user.id}")
    is_allowed, info = await rate_limiter.check_rate_limit(key, limit=100, window=3600)

    if not is_allowed:
        raise TooManyRequestsException(
            detail=f"Rate limit exceeded. Try again in {info['reset_time'] - int(time.time())} seconds",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
            },
        )

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_time"])

    # Process vote
    service = VoteService(db)
    result = await service.vote_on_post(current_user.id, id, vote_data.vote)
    await db.commit()

    return result


@router.post(
    "/{id}/report",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": responses.BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": responses.UnauthorizedResponse},
        status.HTTP_404_NOT_FOUND: {"model": responses.NotFoundResponse},
        status.HTTP_409_CONFLICT: {"model": responses.ConflictResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": responses.TooManyRequestsResponse},
    },
    summary="Report a post",
    description="Report a post for violating community guidelines. "
    "Rate limited to 10 reports per hour. Can only report same post once per 24 hours.",
)
async def report_post(
    id: int,
    data: ReportCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
    response: Response,
):
    """
    Report a post for moderation.

    Rate Limit: 10 reports per hour per user
    Duplicate Check: Same post can only be reported once per 24 hours by same user

    Request Body:
        - reason: Reason for report (spam, harassment, inappropriate, misinformation, other)
        - details: Additional details (required if reason='other', max 500 chars)

    Returns:
        - message: Success message
        - report_id: ID of created report
    """
    # Rate limiting: 10 reports per hour
    key = rate_limiter.build_rate_limit_key("post", "report", f"user:{current_user.id}")
    is_allowed, info = await rate_limiter.check_rate_limit(key, limit=10, window=3600)

    if not is_allowed:
        raise TooManyRequestsException(
            detail=f"Rate limit exceeded. Try again in {info['reset_time'] - int(time.time())} seconds",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
            },
        )

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_time"])

    # Create report
    service = ReportService(db)
    report = await service.create_report(
        reporter_id=current_user.id,
        reportable_type="post",
        reportable_id=id,
        reason=data.reason,
        details=data.details,
    )
    await db.commit()

    return {
        "message": "Report submitted successfully",
        "report_id": report.id,
    }
