from fastapi import APIRouter

hello_fast_tmp_router = APIRouter(prefix="/test")


@hello_fast_tmp_router.get("/hello")
def hello_fast_mtp():
    return "你好,fast-tmp."
