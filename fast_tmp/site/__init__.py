import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type

from starlette.requests import Request
from tortoise.models import Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.actions import AjaxAction, DialogAction
from fast_tmp.amis.buttons import Operation
from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.enums import ButtonLevelEnum
from fast_tmp.amis.filter import Filter, FilterModel
from fast_tmp.amis.forms import Form
from fast_tmp.amis.frame import Dialog
from fast_tmp.amis.page import Page
from fast_tmp.responses import NotFoundError, not_found_model
from fast_tmp.site.base import ModelFilter
from fast_tmp.site.util import BaseAdminControl, RelationSelectApi, create_column

logger = logging.getLogger(__file__)


# 操作数据库的方法
class DbSession:
    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
    ):
        """
        获取列表
        """
        pass

    async def get_instance(self, request: Request, pk: Any) -> Optional[Model]:
        """
        根据pk获取一个实例
        """
        pass

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        """
        对inline的数据进行更新
        """
        pass

    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        pass


class ModelAdmin(DbSession):  # todo inline字段必须都在update_fields内
    model: Type[Model]  # model
    __name: Optional[str] = None
    list_display: Tuple[str, ...] = ()
    inline: Tuple[str, ...] = ()
    prefix: str
    # search list
    searchs: Tuple[str, ...] = ()
    filters: Tuple[ModelFilter, ...] = ()
    # create
    create_fields: Tuple[str, ...] = ()
    # exclude: Tuple[Union[str, BaseModel], ...] = ()
    # update ,如果为空则取create_fields
    update_fields: Tuple[str, ...] = ()
    fields: Dict[str, BaseAdminControl] = None  # type: ignore
    __list_display: Dict[str, BaseAdminControl] = {}
    __list_display_with_pk: Dict[str, BaseAdminControl] = {}
    methods: Tuple[str, ...] = (
        "list",
        "create",
        "put",
        "delete",
        # "deleteMany",
    )  # todo 需要retrieve
    # 页面相关的东西
    __get_pks: Any = None
    list_per_page: int = 10  # 每页多少数据
    list_max_show_all: int = 200  # 最多每页多少数据
    selct_defs: Dict[
        str,
        Callable[
            [Request, Optional[str], Optional[int], Optional[int]], Coroutine[Any, Any, List[dict]]
        ],
    ]
    _filters = None

    def name(self) -> str:
        if self.__name is None:
            self.__name = self.model.__name__
        return self.__name

    def get_filters(self):
        if not self._filters:
            self._filters = {i.name: i for i in self.filters}
        return self._filters

    def queryset_filter(self, request: Request, queryset: QuerySet):
        query = request.query_params
        filter_fs = self.get_filters()
        for k, v in query.items():
            if k in ("pk", "page", "perPage"):
                continue
            func = filter_fs.get(k)
            if func is not None:
                queryset = func.queryset(request, queryset, v)
        return queryset

    def get_create_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_control_field(i) for i in self.create_fields}

    def get_update_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_control_field(i) for i in self.update_fields}

    def get_update_fields_with_pk(self) -> Dict[str, BaseAdminControl]:
        ret = self.get_update_fields()
        ret["pk"] = self.get_control_field("pk")
        return ret

    def get_create_dialogation_button(self, request: Request):
        controls = self.get_create_fields()

        return DialogAction(
            label="新增",
            dialog=Dialog(
                title="新增",
                body=Form(
                    name=f"新增{self.name()}",
                    title=f"新增{self.name()}",
                    body=[(i.get_control(request)) for i in controls.values()],
                    api=f"post:{self.name()}/create",
                ),
            ),
        )

    def get_list_page(self, request: Request):
        res = []
        for field_name, col in self.get_list_distplay().items():
            if field_name in self.inline:
                res.append(col.get_column_inline(request))
            else:
                res.append(col.get_column(request))
        return res

    def get_del_one_button(self):
        return AjaxAction(
            label="删除",
            level=ButtonLevelEnum.link,
            className="text-danger",
            confirmText="确认要删除？",
            api="delete:" + self.name() + "/delete/$pk",
        )

    def get_update_one_button(self, request: Request):
        body = [i.get_control(request) for i in self.get_update_fields().values()]
        return DialogAction(
            label="修改",
            level=ButtonLevelEnum.link,
            dialog=Dialog(
                title="修改",
                body=Form(
                    title=f"修改{self.name()}",
                    name=f"修改{self.name()}",
                    body=body,
                    api="put:" + self.name() + "/update/$pk",
                    initApi="get:" + self.name() + "/update/$pk",
                ),
            ),
        )

    def get_operation(self, request: Request):
        buttons = []
        if "put" in self.methods and self.update_fields:
            buttons.append(self.get_update_one_button(request))
        if "delete" in self.methods:
            buttons.append(self.get_del_one_button())
        return Operation(buttons=buttons)

    def get_filter_page(self, request: Request):
        """
        页面上的过滤框
        """
        return FilterModel(
            body=[
                Filter(
                    type=v.type,
                    name=v.name,
                    label=v.label,
                    clearable=v.clearable,
                    placeholder=v.placeholder,
                )
                for v in self.get_filters().values()
            ]
        )

    def get_crud(self, request: Request):
        body = []
        columns = []
        if "create" in self.methods and self.create_fields:
            body.append(self.get_create_dialogation_button(request))
        if "list" in self.methods and self.list_display:
            columns.extend(self.get_list_page(request))
        columns.append(self.get_operation(request))
        crud = CRUD(
            api=self.prefix + "/list",
            columns=columns,
            quickSaveItemApi=self.prefix + "/patch/" + "$pk",
            syncLocation=False,
        )
        if len(self.get_filters()) > 0:
            crud.filter = self.get_filter_page(request)
        body.append(crud)
        return body

    def get_list_distplay(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_control_field(i) for i in self.list_display}

    def get_list_display_with_pk(self) -> Dict[str, BaseAdminControl]:
        """
        去除多对多字段
        """
        ret = self.get_list_distplay()
        ret["pk"] = self.get_control_field("pk")
        return ret

    def get_app_page(self, request: Request):
        return Page(title=self.name(), body=self.get_crud(request)).dict(exclude_none=True)

    async def put(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        for field_name in self.update_fields:
            control = self.get_control_field(field_name)
            await control.set_value(request, obj, data[field_name])
        await obj.save()
        return obj

    async def put_get(self, request: Request, pk: str) -> dict:
        obj = await self.get_instance(request, pk)
        ret = {}
        for field_name, field in self.get_update_fields_with_pk().items():
            ret[field_name] = await field.get_value(request, obj)
        return ret

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]):
        obj = await self.get_instance(request, pk)
        for field_name in self.inline:
            control = self.get_control_field(field_name)
            await control.set_value(request, obj, data[field_name])
        await obj.save()

    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        obj = self.model()
        for field_name, field in self.get_create_fields().items():
            await field.set_value(request, obj, data[field_name])
        await obj.save()
        return obj

    async def delete(self, request: Request, pk: str):
        await self.model.filter(pk=pk).delete()

    def prefetch(
        self, request: Request, queryset: QuerySet, fields: Dict[str, BaseAdminControl]
    ) -> QuerySet:
        """
        判断是否需要额外预加载的数据
        """
        select_list = []
        prefeth_list = []
        for field_name, field in fields.items():
            d = field.prefetch()
            if d == "select":
                select_list.append(field_name)
            elif d == "prefetch":
                prefeth_list.append(field_name)
        if len(select_list) > 0:
            queryset = queryset.select_related(*select_list)
        elif len(prefeth_list) > 0:
            queryset = queryset.prefetch_related(*prefeth_list)
        return queryset

    def queryset(self, request: Request):
        ret = self.model.all()
        return ret

    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
    ):
        base_queryset = self.queryset(request)
        base_queryset = self.queryset_filter(request, base_queryset)
        queryset = self.prefetch(request, base_queryset, self.get_list_distplay())
        datas = await queryset.limit(perPage).offset((page - 1) * perPage)
        res = []
        for i in datas:
            ret = {}
            for field_name, field in self.get_list_display_with_pk().items():
                if field._many:
                    continue
                ret[field_name] = await field.get_value(request, i)
            res.append(ret)
        count = await base_queryset.count()
        return {"total": count, "items": res}

    async def get_instance(self, request: Request, pk: Any) -> Model:
        queryset = self.model.filter(pk=pk)
        queryset = self.prefetch(request, queryset, self.get_update_fields())
        instance = await queryset.first()

        if instance is None:
            raise NotFoundError("can not found instance:" + str(pk))
        return instance

    def make_fields(self):
        if not self.fields.get("pk"):
            self.fields["pk"] = create_column("pk", self.model._meta.pk, self.prefix)
        s = []
        s.extend(self.list_display)
        s.extend(self.create_fields)
        s.extend(self.update_fields)
        s = set(s)
        for field in s:
            if not self.fields.get(field):
                field_type = self.model._meta.fields_map.get(field)
                if not field_type:
                    logger.error(f"can not found field {field} in {self.model.__name__}")
                    continue
                self.fields[field] = create_column(field, field_type, self.prefix)

    def get_control_field(self, name: str) -> BaseAdminControl:
        ret = self.fields.get(name)
        if ret is None:
            raise NotFoundError("can not found field:" + name)
        return ret

    def __init__(self, prefix: str = None):
        if not self.fields:
            self.fields = {}
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = self.name()
        self.make_fields()
        col_set = set(self.get_list_distplay())
        for i in self.inline:
            if i not in col_set:
                logger.warning("inline field " + i + " not in list_display")

        # 同步select或其他接口
        self.selct_defs = {}
        for field_name, field in self.fields.items():
            if isinstance(field, RelationSelectApi):
                self.selct_defs[field_name] = field.get_selects

    async def select_options(
        self,
        request: Request,
        name: str,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ):
        """
        外键的枚举获取值以及多对多获取对象列表
        """
        return await self.selct_defs[name](request, pk, perPage, page)


# TModelAdmin=TypeVar("TModelAdmin",bound=ModelAdmin)
model_list: Dict[str, List[ModelAdmin]] = {}


def register_model_site(model_group: Dict[str, List[ModelAdmin]]):
    model_list.update(model_group)


def get_model_site(resource: str) -> Optional[ModelAdmin]:
    for m_l in model_list.values():
        for i in m_l:
            if i.name() == resource:
                return i
    raise not_found_model
