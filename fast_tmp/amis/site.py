from typing import Any, Dict, List, Optional, Type, Tuple

from .schema.crud import CRUD
from .schema.page import Page

from fast_tmp.responses import not_found_model
from .utils import get_columns_from_model
from tortoise.models import Model
from tortoise.fields import ReverseRelation
from tortoise import ForeignKeyFieldInstance, ManyToManyFieldInstance, OneToOneFieldInstance, BackwardOneToOneRelation
from logging import getLogger

logger=getLogger(__file__)

class ModelAdmin:
    model: Type[Model]  # model
    __name: Optional[str] = None
    # list
    list_display: Tuple[str, ...] = ()
    list_per_page: int = 10
    list_max_show_all: int = 200
    # search list
    search_fields: Tuple[str, ...] = ()
    filter_fields: Tuple[str, ...] = ()
    # create
    create_fields: Tuple[str, ...] = ()
    # exclude: Tuple[Union[str, BaseModel], ...] = ()
    # update ,如果为空则取create_fields
    update_fields: Tuple[str, ...] = ()

    methods: Tuple[str, ...] = (
        "list",
        # "retrieve",
        "create",
        "put",
        "delete",
        # "deleteMany",
    )  # todo 需要retrieve
    # 页面相关的东西
    __create_dialog: Any = None
    __get_pks: Any = None

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
    @classmethod
    def get_list_page(cls):
        return get_columns_from_model(cls.model, cls.list_display)

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

    @classmethod
    def get_crud(cls):
        body = []
        if "create" in cls.methods and cls.create_fields:
            body.append(cls.get_create_dialogation_button())
        if "list" in cls.methods and cls.list_display:
            columns = []
            columns.extend(cls.get_list_page())
            # columns.append(cls.get_operation())
            body.append(
                CRUD(
                    api=cls.name() + "/list",
                    columns=columns,
                )
            )
        return body

    @classmethod
    def get_app_page(cls):
        return Page(title=cls.name(), body=cls.get_crud()).dict(exclude_none=True)

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

    #
    # @classmethod
    # def get_list_sql(cls):
    #     if cls.__list_sql is None:
    #         __list_display = []
    #         for i in cls.list_display:
    #             if hasattr(i.property, "direction"):
    #                 if i.property.direction in (MANYTOMANY, ONETOMANY):
    #                     continue
    #                 if i.property.direction == MANYTOONE:
    #                     __list_display.append(get_real_column_field(i))
    #             else:
    #                 __list_display.append(i)
    #         cls.__list_sql = select(__list_display)
    #     return cls.__list_sql
    #
    # __one_sql = None

    @classmethod
    def queryset(cls):
        ret = cls.model.all()
        fields = cls.model._meta.fields_map
        for field_name in cls.list_display:
            field=fields.get(field_name)
            if not field:
                logger.error("can not found field:",field_name)
            if isinstance(field, ForeignKeyFieldInstance):
                ret = ret.select_related(field)
            elif isinstance(field, OneToOneFieldInstance):
                ret = ret.select_related(field)
            elif isinstance(field, BackwardOneToOneRelation):
                ret = ret.prefetch_related(field)
        return ret

    @classmethod
    async def count(cls)->int:
        return await cls.model.all().count()

    @classmethod
    async def list(cls, limit: int = 10, offset: int = 0):
        datas = await cls.queryset().limit(limit).offset(offset)
        res = []
        for i in datas:
            ret = {}
            for name in cls.list_display and not isinstance(i,(ManyToManyFieldInstance,)):
                field = getattr(i, name)
                if field is None:# 如果这个字段是个函数
                    field=getattr(cls,name)  # 支持函数方式
                    if field is None:
                        logger.error("can not found field:",field)
                    ret[name]=field(i)
                if isinstance(field, ReverseRelation):
                    ret[name] = str(field)
                ret[name] = field
            res.append(ret)
        count = await cls.count()
        return {
            "total": count,
            "items": res
        }
    #
    # @classmethod
    # def get_one_sql(cls, pks: list, need_many: bool = False):
    #     if cls.__one_sql is None:
    #         __list_display = cls.get_clean_fields(cls.update_fields, need_many)
    #         cls.__one_sql = select(__list_display)
    #     return cls.__one_sql.where(*pks)
    #


model_list: Dict[str, List[Type[ModelAdmin]]] = {}


def register_model_site(model_group: Dict[str, List[Type[ModelAdmin]]]):
    model_list.update(model_group)


def get_model_site(resource: str) -> Optional[Type[ModelAdmin]]:
    for m_l in model_list.values():
        for i in m_l:
            if i.name() == resource:
                return i
    raise not_found_model
