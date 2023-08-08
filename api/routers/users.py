from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from typing import Optional
from psycopg.errors import ForeignKeyViolation
from queries.users import UserQueries, UserListOut, UserOut, UserIn


router = APIRouter()

# Implement the following endpoints
# 1. get a user with a specific id
# 2. get all users
# 3. create a user
# 4. delete a user
#
# Resources
# routers.trucks example
# users.queries
# docs page (at http://localhost:8000/docs#)
# Notion: https://marbled-particle-5cf.notion.site/FastAPI-2eee765c870245ab9f28a3ef5456a981?pvs=4
# take note of endpoints best practices


@router.get("/api/users", response_model=UserListOut)
def get_users(
    queries: UserQueries = Depends()
):
    return {"users": queries.get_all_users()}


@router.get("/api/users/{user_id}", response_model=Optional[UserOut])
def get_user(
    user_id: int,
    queries: UserQueries = Depends(),
):
    record = queries.get_user(user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No truck found with id {}".format(user_id))
    else:
        return record



@router.post("/api/users", response_model=UserOut)
def create_user(
    user: UserIn,
    queries: UserQueries = Depends(),
):
    try:
        return queries.create_user(user)
    except ForeignKeyViolation as e:
        raise HTTPException(status_code=400, detail="Failed to create user")


@router.delete("/api/users/{user_id}", response_model=bool)
def delete_user(
    user_id: int,
    queries: UserQueries = Depends()
):
    queries.delete_user(user_id)
    return True
