from typing import Any, Dict, List, Optional, Type, Tuple, Sequence, Iterable, TypeVar

from starlette.requests import Request
from tortoise.queryset import QuerySet

from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.page import Page

from fast_tmp.responses import not_found_model
from .util3 import AbstractControl, create_column
from .utils2 import get_columns_from_model, get_controls_from_model
from tortoise.models import Model

from ..amis.response import AmisStructError


class ModelAdmin:  # todo inline字段必须都在update_fields内
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
    fields: Dict[str, AbstractControl] = dict()  # 存储字段名:control
    __list_display: Dict[str, AbstractControl] = {}
    __list_display_with_pk: Dict[str, AbstractControl] = {}
    methods: Tuple[str, ...] = (
        "list",
        "retrieve",
        "create",
        "put",
        "delete",
        # "deleteMany",
    )  # todo 需要retrieve
    # 页面相关的东西
    __create_dialog: Any = None
    __get_pks: Any = None
    list_per_page: int = 10  # 每页多少数据
    list_max_show_all: int = 200  # 最多每页多少数据

    @classmethod
    def name(cls) -> str:
        if cls.__name is None:
            cls.__name = cls.model.__name__
        return cls.__name

    # @classmethod
    # def get_create_dialogation_button(cls):
    #     if cls.__create_dialog is None:
    #         cls.__create_dialog = DialogAction(
    #             label="新增",
    #             dialog=Dialog(
    #                 title="新增",
    #                 body=Form(
    #                     name=f"新增{cls.name()}",
    #                     title=f"新增{cls.name()}",
    #                     body=make_controls(cls.create_fields),
    #                     api=f"post:{cls.name()}/create",
    #                 ),
    #             ),
    #         )
    #     return cls.__create_dialog
    #
    async def get_list_page(self, request: Request):
        res = []
        for field_name, col in self.get_list_distplay().items():
            if field_name in self.inline:
                res.append(await col.get_column_inline(request))
            else:
                res.append(await col.get_column(request))
        return res

    #
    # @classmethod
    # def pks(cls):
    #     if cls.__get_pks is None:
    #         primary_keys = get_pk(cls.model).keys()
    #         del_path = []
    #         for pk in primary_keys:
    #             del_path.append(f"{pk}=${pk}")
    #         cls.__get_pks = "&".join(del_path)
    #     return cls.__get_pks

    # @classmethod
    # def get_del_one_button(cls):
    #     return AjaxAction(
    #         label="删除",
    #         level=ButtonLevelEnum.danger,
    #         confirmText="确认要删除？",
    #         api="delete:" + cls.name() + "/delete?" + cls.pks(),
    #     )

    # @classmethod
    # def get_update_one_button(cls):
    #     return DialogAction(
    #         label="修改",
    #         dialog=Dialog(
    #             title="修改",
    #             body=Form(
    #                 name=f"修改{cls.name()}",
    #                 body=get_controls_from_model(cls.update_fields),
    #                 api="put:" + cls.name() + "/update?" + cls.pks(),
    #                 initApi="get:" + cls.name() + "/update?" + cls.pks(),
    #             ),
    #         ),
    #     )

    # @classmethod
    # def get_operation(cls):
    #     buttons = []
    #     if "delete" in cls.methods:
    #         buttons.append(cls.get_del_one_button())
    #     if "put" in cls.methods and cls.update_fields:
    #         buttons.append(cls.get_update_one_button())
    #     return Operation(buttons=buttons)

    async def get_crud(self, request: Request):
        body = []
        # if "create" in cls.methods and cls.create_fields:
        #     body.append(cls.get_create_dialogation_button())
        # if "list" in cls.methods and cls.list_display:
        columns = []
        columns.extend(await self.get_list_page(request))
        # columns.append(cls.get_operation())
        body.append(
            CRUD(
                api=self.prefix + "/list",
                columns=columns,
                quickSaveItemApi=self.prefix + "/patch/" + "$pk"
            )
        )
        return body

    def get_list_distplay(self) -> Dict[str, AbstractControl]:
        return {i: self.fields[i] for i in self.list_display}

    def get_list_display_with_pk(self) -> Dict[str, AbstractControl]:
        ret = self.get_list_distplay()
        ret["pk"] = self.fields["pk"]
        return ret

    async def get_app_page(self, request: Request):
        return Page(title=self.name(), body=await self.get_crud(request)).dict(exclude_none=True)

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        obj = await self.get_instance(request, pk)
        for field_name in self.inline:
            control = self.fields[field_name]
            await control.set_value(request, obj, data[field_name])
        await obj.save()
        return obj

    def prefetch(self, request: Request, queryset: QuerySet) -> QuerySet:
        """
        判断是否需要额外预加载的数据
        """
        for field_name, field in self.fields.items():
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

    @classmethod
    def queryset(cls, request: Request):
        ret = cls.model.all()
        return ret

    async def list(self, request: Request, limit: int = 10, offset: int = 0):
        base_queryset = self.queryset(request)
        queryset = self.prefetch(request, base_queryset)
        datas = await queryset.limit(limit).offset(offset)
        res = []
        for i in datas:
            ret = {}
            for field_name, field in self.get_list_display_with_pk().items():
                ret[field_name] = await field.get_value(request, i)
            res.append(ret)
        count = await base_queryset.count()
        return {
            "total": count,
            "items": res
        }

    async def get_instance(self, request: Request, pk: Any) -> Optional[Model]:
        return await self.model.filter(pk=pk).first()

    #
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

        for field in self.list_display:
            if not self.fields.get(field):
                field_type = self.model._meta.fields_map.get(field)
                self.fields[field] = create_column(field, field_type, self.prefix)
        for field in self.create_fields:
            if not self.fields.get(field):
                field_type = self.model._meta.fields_map.get(field)
                self.fields[field] = create_column(field, field_type, self.prefix)

    def __init__(self, prefix: str = None):
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = self.name()
        self.make_fields()


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
