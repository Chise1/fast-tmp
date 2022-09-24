import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from starlette.requests import Request
from tortoise.models import Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.page import Page
from fast_tmp.responses import not_found_model

from ..amis.actions import AjaxAction, DialogAction, DrawerAction
from ..amis.buttons import Operation
from ..amis.enums import ButtonLevelEnum
from ..amis.forms import Form
from ..amis.frame import Dialog, Drawer
from .util import AbstractControl, BaseAdminControl, RelationSelectApi, create_column

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
    search_fields: Tuple[str, ...] = ()
    filter_fields: Tuple[str, ...] = ()
    # create
    create_fields: Tuple[str, ...] = ()
    # exclude: Tuple[Union[str, BaseModel], ...] = ()
    # update ,如果为空则取create_fields
    update_fields: Tuple[str, ...] = ()
    fields: Dict[str, BaseAdminControl] = None  # 存储字段名:control
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
    selct_defs = None

    def name(self) -> str:
        if self.__name is None:
            self.__name = self.model.__name__
        return self.__name

    def get_create_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.fields[i] for i in self.create_fields}

    def get_update_fields(self) -> Dict[str, BaseAdminControl]:
        return {i: self.fields[i] for i in self.update_fields}

    def get_update_fields_with_pk(self) -> Dict[str, BaseAdminControl]:
        ret = self.get_update_fields()
        ret["pk"] = self.fields["pk"]
        return ret

    async def get_create_dialogation_button(self, request: Request):
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

    async def get_list_page(self, request: Request):
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

    async def get_update_one_button(self, request: Request):
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

    async def get_operation(self, request: Request):
        buttons = []
        if "put" in self.methods and self.update_fields:
            buttons.append(await self.get_update_one_button(request))
        if "delete" in self.methods:
            buttons.append(self.get_del_one_button())
        return Operation(buttons=buttons)

    async def get_crud(self, request: Request):
        body = []
        columns = []
        if "create" in self.methods and self.create_fields:
            body.append(await self.get_create_dialogation_button(request))
        if "list" in self.methods and self.list_display:
            columns.extend(await self.get_list_page(request))
        columns.append(await self.get_operation(request))
        body.append(
            CRUD(
                api=self.prefix + "/list",
                columns=columns,
                quickSaveItemApi=self.prefix + "/patch/" + "$pk",
                syncLocation=False,
            )
        )
        return body

    def get_list_distplay(self) -> Dict[str, BaseAdminControl]:
        return {i: self.fields[i] for i in self.list_display}

    def get_list_display_with_pk(self) -> Dict[str, BaseAdminControl]:
        """
        去除多对多字段
        """
        ret = self.get_list_distplay()
        ret["pk"] = self.fields["pk"]
        return ret

    async def get_app_page(self, request: Request):
        return Page(title=self.name(), body=await self.get_crud(request)).dict(exclude_none=True)

    async def put(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        for field_name in self.update_fields:
            control = self.fields[field_name]
            await control.set_value(request, obj, data[field_name])
        await obj.save()
        return obj

    async def put_get(self, request: Request, pk: str) -> Any:
        obj = await self.get_instance(request, pk)
        ret = {}
        for field_name, field in self.get_update_fields_with_pk().items():
            ret[field_name] = await field.get_value(request, obj)
        return ret

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        for field_name in self.inline:
            control = self.fields[field_name]
            await control.set_value(request, obj, data[field_name])
        await obj.save()
        return obj

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
        for field_name, field in fields.items():
            queryset = field.prefetch(request, queryset)
        return queryset

    # @classmethod
    # def create_model(cls, data: dict, session: Session):
    #     """
    #     写入数据库之前调用
    #     """
    #     instance = cls.model()
    #     for k, v in data.items():
    #         field = getattr(cls.model, k)
    #         if isinstance(field.property, RelationshipProperty):
    #             if field.property.direction == MANYTOMANY:
    #                 model = field.mapper.class_
    #                 pk = list(get_pk(model).values())[0]
    #                 childs = session.execute(select(model).where(pk.in_(v))).scalars().fetchall()
    #                 setattr(instance, k, childs)
    #                 # getattr(instance, k).append(*childs)
    #             elif field.property.direction == MANYTOONE:
    #                 field = get_real_column_field(field)
    #                 setattr(instance, field.key, v)
    #             elif field.property.direction == ONETOMANY:  # todo 暂时不考虑支持
    #                 # onetoone
    #                 if not getattr(field.property, "uselist"):
    #                     pass
    #                 else:
    #                     pass
    #             else:
    #                 raise AttributeError(
    #                     f"error relationshipfield: {cls.model}'s {field} relationship is not true."
    #                 )
    #         else:
    #             setattr(instance, k, v)
    #     return instance
    #
    # @classmethod
    # def update_model(cls, instance: Any, data: dict, session: Session) -> Any:
    #     """
    #     更新数据之前调用
    #     """
    #     for k, v in data.items():
    #         field = getattr(cls.model, k)
    #         if isinstance(field.property, RelationshipProperty):
    #             if field.property.direction == MANYTOMANY:
    #                 model = field.mapper.class_
    #                 pk = list(get_pk(model).values())[0]
    #                 childs = session.execute(select(model).where(pk.in_(v))).scalars().fetchall()
    #                 setattr(instance, k, childs)
    #             elif field.property.direction == MANYTOONE:
    #                 field = get_real_column_field(field)
    #                 setattr(instance, field.key, v)
    #             elif field.property.direction == ONETOMANY:  # todo 暂时不考虑支持
    #                 # onetoone
    #                 if not getattr(field.property, "uselist"):
    #                     pass
    #                 else:
    #                     pass
    #             else:
    #                 raise AttributeError(
    #                     f"error relationshipfield: {cls.model}'s {field} relationship is not true."
    #                 )
    #         else:
    #             setattr(instance, k, v)
    #     return instance

    # @classmethod
    # def get_clean_fields(cls, fields, need_many: bool = False):
    #     """
    #     获取对外键进行处理过的列表,该方法主要用于数据处理
    #     """
    #     res = []
    #     for i in fields:
    #         if hasattr(i.property, "direction"):
    #             if i.property.direction in (MANYTOMANY, ONETOMANY):
    #                 if need_many:
    #                     res.append(i)
    #                 else:
    #                     continue
    #             if i.property.direction == MANYTOONE:
    #                 res.append(get_real_column_field(i))
    #         else:
    #             res.append(i)
    #     return res

    __list_sql = None

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

    async def get_instance(self, request: Request, pk: Any) -> Optional[Model]:
        queryset = self.model.filter(pk=pk)
        queryset = self.prefetch(request, queryset, self.get_update_fields())
        return await queryset.first()

    # @classmethod
    # def get_one_sql(cls, pks: list, need_many: bool = False):
    #     if cls.__one_sql is None:
    #         __list_display = cls.get_clean_fields(cls.update_fields, need_many)
    #         cls.__one_sql = select(__list_display)
    #     return cls.__one_sql.where(*pks)
    #
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

    def __init__(self, prefix: str = None):
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
