import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple, Type, Union

from starlette.requests import Request
from tortoise import transactions
from tortoise.exceptions import ValidationError
from tortoise.models import Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.actions import AjaxAction, DialogAction
from fast_tmp.amis.base import BaseAmisModel, _Action
from fast_tmp.amis.column import Operation
from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.enums import ButtonLevelEnum
from fast_tmp.amis.forms import FilterModel, Form
from fast_tmp.amis.frame import Dialog
from fast_tmp.amis.page import Page
from fast_tmp.exceptions import FieldsError, NotFoundError, PermError
from fast_tmp.models import Permission
from fast_tmp.responses import ListDataWithPage
from fast_tmp.site.base import ModelFilter, ModelSession, PageRouter
from fast_tmp.site.field import BaseAdminControl, RelationSelectApi, create_column
from fast_tmp.site.filter import make_filter_by_str

logger = logging.getLogger(__file__)


class ModelAdmin(ModelSession, PageRouter):  # todo inline字段必须都在update_fields内
    model: Type[Model]  # model
    list_display: Tuple[str, ...] = ()
    inline: Tuple[str, ...] = ()
    # search list
    searchs: Tuple[str, ...] = ()
    filters: Tuple[Union[str, ModelFilter], ...] = ()
    # create
    create_fields: Tuple[str, ...] = ()
    update_fields: Tuple[str, ...] = ()
    fields: Dict[str, BaseAdminControl] = None  # type: ignore
    _permissions: Optional[List[str]] = None  # 设置为 ()即可不验证权限
    methods: Tuple[str, ...] = (
        "list",
        "create",
        "put",
        "delete",
        # "deleteMany",
    )  # todo 需要retrieve？
    selct_defs: Dict[
        str,
        Callable[
            [Request, Optional[str], Optional[int], Optional[int],Optional[Any]], Coroutine[Any, Any, List[dict]]
        ],
    ]
    _filters = None

    def get_filters(self, request: Request) -> Dict[str, ModelFilter]:
        if self._filters is None:
            filters = {}
            for filter in self.filters:
                if isinstance(filter, ModelFilter):
                    filters[filter.name] = filter
                else:
                    name_split = filter.split("__")
                    if len(name_split) == 1:  # equal
                        field = self.fields[filter]
                    elif len(name_split) == 2:
                        name = name_split[0]
                        field = self.fields[name]
                    else:
                        raise AttributeError("filter field can not be " + filter)
                    filters[filter] = make_filter_by_str(request, filter, field)
            self._filters = filters
        return self._filters

    def queryset_filter(self, request: Request, queryset: QuerySet):
        query = request.query_params
        filter_fs = self.get_filters(request)
        for k, v in query.items():
            if k in ("pk", "page", "perPage"):
                continue
            func = filter_fs.get(k)
            if func is not None:
                queryset = func.queryset(request, queryset, v)
        return queryset

    def get_create_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_formitem_field(i) for i in self.create_fields}

    def get_update_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_formitem_field(i) for i in self.update_fields}

    def get_update_fields_with_pk(self) -> Dict[str, BaseAdminControl]:
        ret = self.get_update_fields()
        ret["pk"] = self.get_formitem_field("pk")
        return ret

    def get_create_dialogation_button(self, request: Request) -> List[_Action]:
        formitems = self.get_create_fields()

        return [
            DialogAction(
                label="新增",
                dialog=Dialog(
                    title="新增",
                    body=Form(
                        name=f"新增{self.name}",
                        title=f"新增{self.name}",
                        # fixme 你的field字段传实例了吗？
                        body=[(i.get_formitem(request)) for i in formitems.values()],
                        api=f"post:{self.prefix}/create",
                    ),
                ),
            )
        ]

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
            api="delete:" + self.prefix + "/delete/$pk",
        )

    def get_update_one_button(self, request: Request):
        body = [i.get_formitem(request) for i in self.get_update_fields().values()]
        return DialogAction(
            label="修改",
            level=ButtonLevelEnum.link,
            dialog=Dialog(
                title="修改",
                body=Form(
                    title=f"修改{self.name}",
                    name=f"修改{self.name}",
                    body=body,
                    api="put:" + self.prefix + "/update/$pk",
                    initApi="get:" + self.prefix + "/update/$pk",
                ),
            ),
        )

    def get_operation(self, request: Request, codenames: List[str]):
        buttons = []
        if "put" in self.methods and self.update_fields and self.name + "_update" in codenames:
            buttons.append(self.get_update_one_button(request))
        if "delete" in self.methods and self.name + "_delete" in codenames:
            buttons.append(self.get_del_one_button())
        if len(buttons) > 0:
            return Operation(buttons=buttons)
        return None

    def get_filter_page(self, request: Request):
        """
        页面上的过滤框
        """
        return FilterModel(
            body=[v.filter_control(request) for v in self.get_filters(request).values()]
        )

    def get_crud(self, request: Request, codenames: List[str]):
        body: List[BaseAmisModel] = []
        columns = []
        if "create" in self.methods and self.create_fields and self.name + "_create" in codenames:
            body.extend(self.get_create_dialogation_button(request))
        if "list" in self.methods and self.list_display and self.name + "_list" in codenames:
            columns.extend(self.get_list_page(request))
        buttons = self.get_operation(request, codenames)
        if buttons:
            columns.append(buttons)
        crud = CRUD(
            api=self._prefix + "/list",
            columns=columns,
            quickSaveItemApi=self._prefix + "/patch/" + "$pk",
            syncLocation=False,
        )
        if len(self.get_filters(request)) > 0 and self.name + "_list" in codenames:
            crud.filter = self.get_filter_page(request)
        body.append(crud)
        return body

    def get_list_distplay(self) -> Dict[str, BaseAdminControl]:
        return {i: self.get_formitem_field(i) for i in self.list_display}

    def get_list_display_with_pk(self) -> Dict[str, BaseAdminControl]:
        """
        去除多对多字段
        """
        ret = self.get_list_distplay()
        ret["pk"] = self.get_formitem_field("pk")
        return ret

    async def get_app_page(self, request: Request) -> Page:
        codenames = await self.permission_code(request)
        return Page(title=self.name, body=self.get_crud(request, codenames))

    async def update(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        err_fields = {}
        for field_name in self.update_fields:
            control = self.get_formitem_field(field_name)
            try:
                await control.set_value(request, obj, data[field_name])
            except ValidationError as e:
                err_fields[field_name] = str(e)
        if err_fields:
            raise FieldsError(err_fields)
        await obj.save()
        return obj

    async def get_update(self, request: Request, pk: str) -> dict:
        obj = await self.get_instance(request, pk)
        ret = {}
        for field_name, field in self.get_update_fields_with_pk().items():
            ret[field_name] = await field.get_value(request, obj)
        return ret

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        err_fields = {}
        for field_name in self.inline:
            control = self.get_formitem_field(field_name)
            try:
                await control.set_value(request, obj, data[field_name])
            except ValidationError as e:
                err_fields[field_name] = str(e)
        if err_fields:
            raise FieldsError(err_fields)
        await obj.save()
        return obj

    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        obj = self.model()
        cors = []
        field_errors = {}
        for field_name, field in self.get_create_fields().items():
            try:
                cor = await field.set_value(request, obj, data.get(field_name))  # 只有create可能有返回协程
                if cor:
                    cors.append(cor)
            except ValidationError as e:
                field_errors[field_name] = str(e)
        if field_errors:
            raise FieldsError(field_errors)

        @transactions.atomic()
        async def save_all():
            await obj.save()
            for cor in cors:
                await cor

        await save_all()
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
    ) -> ListDataWithPage:
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
        return ListDataWithPage(total=count, items=res)

    async def get_instance(self, request: Request, pk: Any) -> Model:
        queryset = self.model.filter(pk=pk)
        queryset = self.prefetch(request, queryset, self.get_update_fields())
        instance = await queryset.first()

        if instance is None:
            raise NotFoundError("can not found instance:" + str(pk))
        return instance

    async def permission_code(self, request: Request):
        """
        判断用户拥有的权限
        """
        if self._permissions is None:
            self._permissions = [
                self.name + "_list",
                self.name + "_create",
                self.name + "_update",
                self.name + "_delete",
            ]
        user = request.user
        if user.is_superuser:
            return self._permissions
        return [
            i.codename
            for i in await Permission.filter(groups__users=user, codename__in=self._permissions)
        ]

    def make_fields(self):
        if not self.fields.get("pk"):
            self.fields["pk"] = create_column("pk", self.model._meta.pk, self._prefix)
        s = []
        s.extend(self.list_display)
        s.extend(self.create_fields)
        s.extend(self.update_fields)
        s = set(s)
        for field in s:
            field_ = self.fields.get(field)
            if not field_:
                field_type = self.model._meta.fields_map.get(field)
                if not field_type:
                    logger.error(f"can not found field {field} in {self.model.__name__}")
                    continue
                self.fields[field] = create_column(field, field_type, self._prefix)
            else:
                if callable(field_):
                    field_type = self.model._meta.fields_map.get(field)
                    if not field_type:
                        logger.error(f"can not found field {field} in {self.model.__name__}")
                        continue
                    self.fields[field] = field_(name=field, field=field_type, prefix=self.prefix)

    def get_formitem_field(self, name: str) -> BaseAdminControl:
        ret = self.fields.get(name)
        if ret is None:
            raise NotFoundError("can not found field:" + name)
        return ret

    def __init__(self, prefix: Optional[str] = None, label: Optional[str] = None):
        if not prefix:
            prefix = self.model.__name__

        super().__init__(prefix, label or self.model.__name__.lower())
        if not self.fields:
            self.fields = {}
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
    ) -> List[Dict[str, str]]:
        """
        外键的枚举获取值以及多对多获取对象列表
        """
        return await self.selct_defs[name](request, pk, perPage, page)

    async def check_perm(self, request: Request, codename: str):
        user = request.user
        if not await user.has_perm(codename.lower()):
            raise PermError()


model_list: Dict[str, List[PageRouter]] = {}
resources: Set[str] = set()


def register_model_site(model_group: Dict[str, List[PageRouter]]):
    for models in model_group.values():
        for model in models:
            if model.prefix in resources:
                raise ValueError(f"prefix {model.prefix} can not be same!")
        else:
            resources.add(model.prefix)
    model_list.update(model_group)


def get_model_site(resource: str) -> Optional[PageRouter]:
    for m_l in model_list.values():
        for i in m_l:
            if i.prefix == resource:
                return i
    raise NotFoundError("can not found " + resource)
