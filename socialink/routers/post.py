import logging
import sqlalchemy
from enum import Enum

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from socialink.tasks import generate_and_add_to_post
from socialink.models.user import User
from socialink.security import get_current_user

from socialink.database import comment_table, database, post_table, likes_table
from socialink.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostsWithComments,
    UserPostWithLikes,
)

select_post_and_likes = (
    sqlalchemy.select(
        post_table, sqlalchemy.func.count(likes_table.c.id).label("likes")
    )
    .select_from(post_table.outerjoin(likes_table))
    .group_by(post_table.c.id)
)

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn,
    current_user: Annotated[User, Depends(get_current_user)],
    background_task: BackgroundTasks,
    request: Request,
    prompt: str = None,
):
    logger.info("Creating Post")
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)

    if prompt:
        background_task.add_task(
            generate_and_add_to_post,
            current_user.email,
            last_record_id,
            request.url_for("get_comments_with_post", post_id=last_record_id),
            database,
            prompt,
        )
    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    logger.info("Getting all posts")

    if sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Creating comment")

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not Found")
    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_posts(post_id: int):
    logger.info("Getting comments on a post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostsWithComments)
async def get_comments_with_post(post_id: int):
    logger.info("Getting all posts with comments")

    query = select_post_and_likes.where(post_table.c.id == post_id)

    logger.debug(query)

    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_comments_on_posts(post_id),
    }


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Liking post")

    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**like.model_dump(), "user_id": current_user.id}
    query = likes_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
