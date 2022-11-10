from typing import Any

from starlette.requests import Request
from tortoise.queryset import QuerySet

from .base import BaseAdminControl, ModelFilter


def make_filter_by_str(request: Request, name: str, field: BaseAdminControl) -> ModelFilter:
    """
    根据字符串自动生成model对应field的搜索功能
    """
    control = field.get_formitem(request)
    filter_info = control.dict(exclude_none=True)
    filter_info["name"] = name
    filter_info["label"] = name
    filter_info.pop("required")
    return CommonFilter(field=field, **filter_info)


class CommonFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        val = self._field.amis_2_orm(val)
        return queryset.filter(**{self.name: val})


#
# class EqualFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{self.name: val})
#
#
# class ContainsFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__contains": val})
#
#
# class IcontainsFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__icontains": val})
#
#
# class GtFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__gt": val})
#
#
# class GteFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__gte": val})
#
#
# class LtFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__lt": val})
#
#
# class LteFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__lte": val})
#
#
# class InFilter(ModelFilter):
#     def queryset(self, request: Request, queryset: QuerySet, val: Iterable) -> QuerySet:
#         return queryset.filter(**{f"{self.name}__in": val})
