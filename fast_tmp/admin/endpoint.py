import os.path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from starlette.requests import Request

from fast_tmp.admin.depends import get_staff
from fast_tmp.conf import settings
from fast_tmp.exceptions import PermError
from fast_tmp.responses import BaseRes
from fast_tmp.site import ModelSession, PageRouter, get_model_site

router = APIRouter()


@router.get("/{resource}/list", dependencies=[Depends(get_staff)])
async def list_view(
    request: Request,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
    perPage: int = 10,
    page: int = 1,
):
    await page_model.check_perm(request, resource + "_list")
    datas = await page_model.list(request, perPage, page)
    return BaseRes(data=datas)


@router.get("/{resource}/select/{field_name}", dependencies=[Depends(get_staff)])
async def select_view(
    request: Request,
    field_name: str,
    resource: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelSession = Depends(get_model_site),
):
    """
    枚举字段的额外加载，主要用于外键
    """
    await page_model.check_perm(request, resource + "_list")
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.post("/{resource}/patch/{pk}", dependencies=[Depends(get_staff)])
async def patch_data(
    request: Request,
    pk: str,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
):
    """
    内联模式快速修改需要的接口
    """
    await page_model.check_perm(request, resource + "_update")
    data = await request.json()
    await page_model.patch(request, pk, data)
    return BaseRes().dict()


@router.put("/{resource}/update/{pk}", dependencies=[Depends(get_staff)])
async def update_data(
    request: Request,
    pk: str,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
):
    await page_model.check_perm(request, resource + "_update")
    data = await request.json()
    await page_model.update(request, pk, data)


@router.get("/{resource}/update/{pk}", dependencies=[Depends(get_staff)])
async def update_view(
    request: Request,
    pk: str,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
):
    await page_model.check_perm(request, resource + "_update")
    data = await page_model.get_update(request, pk)
    return BaseRes(data=data)


@router.post("/{resource}/create", dependencies=[Depends(get_staff)])
async def create(
    request: Request,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
):
    await page_model.check_perm(request, resource + "_create")
    data = await request.json()
    await page_model.create(request, data)


@router.delete("/{resource}/delete/{pk}", dependencies=[Depends(get_staff)])
async def delete_func(
    request: Request,
    pk: str,
    resource: str,
    page_model: ModelSession = Depends(get_model_site),
):
    await page_model.check_perm(request, resource + "_delete")
    await page_model.delete(request, pk)
    return BaseRes()


@router.get("/{resource}/schema", dependencies=[Depends(get_staff)])
async def get_schema(
    request: Request,
    page: PageRouter = Depends(get_model_site),
):
    return BaseRes(data=(await page.get_app_page(request)).dict(exclude_none=True))


# todo 考虑清除没有被使用的文件 考虑对上传的文件进行校验，判断该字段是否应该上传文件
@router.post("/{resource}/file/{name}", dependencies=[Depends(get_staff)])
async def update_file(
    request: Request,
    name: str,
    file: UploadFile,
    resource: str,
    page: ModelSession = Depends(get_model_site),
):
    try:
        await page.check_perm(request, resource + "_create")
    except PermError:
        await page.check_perm(request, resource + "_update")

    # pip install aiofiles
    import aiofiles  # type: ignore

    if not os.path.exists(settings.MEDIA_PATH):
        os.mkdir(settings.MEDIA_PATH)
    if not os.path.exists(os.path.join(settings.MEDIA_PATH, resource)):
        os.mkdir(os.path.join(settings.MEDIA_PATH, resource))
    cwd = os.path.join(settings.MEDIA_PATH, resource, name)
    if not os.path.exists(cwd):
        os.mkdir(cwd)
    async with aiofiles.open(os.path.join(cwd, file.filename), "wb") as f:
        await f.write(await file.read())
    res_path = f"/{settings.MEDIA_ROOT}/{resource}/{name}/{file.filename}"
    return BaseRes(data={"value": res_path})


@router.api_route("/{resource}/extra/{prefix}", methods=["POST", "GET", "DELETE", "PUT", "PATCH"])
async def extra_func(
    request: Request,
    prefix: str,
    page: PageRouter = Depends(get_model_site),
):
    method = request.method
    return await page.router(request, prefix, method)
