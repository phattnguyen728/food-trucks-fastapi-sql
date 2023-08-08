from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from queries.users import UserQueries, UserListOut, UserOut, UserIn

# Implement the following endpoints
# 1. get a user with a specific id
# 2. get all users
# 3. create a user
# 4. delete a user
# 
# Resources
# routers.trucks example
# docs page (at http://localhost:8000/docs#)
# Notion: https://marbled-particle-5cf.notion.site/FastAPI-2eee765c870245ab9f28a3ef5456a981?pvs=4
# take note of endpoints best practices


