from typing import Any, Iterable

from starlette.requests import Request
from tortoise.queryset import QuerySet

from .base import ModelFilter


class EqualFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{self.name: val})


class ContainsFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__contains": val})


class IcontainsFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__icontains": val})


class GtFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__gt": val})


class GteFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__gte": val})


class LtFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__lt": val})


class LteFilter(ModelFilter):
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset.filter(**{f"{self.name}__lte": val})


class InFilter(ModelFilter):  # todo 是否要转为列表进行处理？传进来的字符串还是列表？
    def queryset(self, request: Request, queryset: QuerySet, val: Iterable) -> QuerySet:
        return queryset.filter(**{f"{self.name}__in": val})
