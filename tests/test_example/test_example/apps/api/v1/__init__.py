from fastapi import APIRouter
from test_example.models import Reporter, Tree
from tortoise import Tortoise

router = APIRouter()


@router.get("/describe")
async def describe():
    x = Tortoise
    print(Reporter.describe())
    print(Tree.describe())


from test_example.schemas import x1
