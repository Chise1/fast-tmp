import binascii
import datetime
import os
import uuid
from decimal import Decimal
from enum import Enum, IntEnum

from tortoise import fields
from tortoise.models import Model

from fast_tmp.contrib.tortoise.fields import ImageField


def generate_token():
    return binascii.hexlify(os.urandom(16)).decode("ascii")


class Author(Model):
    name = fields.CharField(max_length=255)
    birthday = fields.DateField()

    def __str__(self):
        return self.name


class Book(Model):
    name = fields.CharField(max_length=255)
    author: fields.ForeignKeyRelation[Author] = fields.ForeignKeyField(
        "fast_tmp.Author", related_name="books"
    )
    cover = ImageField()
    rating = fields.FloatField()


class BookNoConstraint(Model):
    name = fields.CharField(max_length=255)
    author: fields.ForeignKeyRelation[Author] = fields.ForeignKeyField(
        "fast_tmp.Author", db_constraint=False
    )
    rating = fields.FloatField()


class Tournament(Model):
    id = fields.SmallIntField(pk=True)
    name = fields.CharField(max_length=255)
    desc = fields.TextField(null=True)
    created = fields.DatetimeField(auto_now_add=True, index=True)

    events: fields.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Reporter(Model):
    """Whom is assigned as the reporter"""

    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ReverseRelation["Event"]

    class Meta:
        table = "re_port_er"

    def __str__(self):
        return self.name


class Event(Model):
    """Events on the calendar"""

    event_id = fields.BigIntField(pk=True)
    #: The name
    name = fields.TextField()
    tournament: fields.ForeignKeyRelation["Tournament"] = fields.ForeignKeyField(
        "fast_tmp.Tournament", related_name="events"
    )
    reporter: fields.ForeignKeyNullableRelation[Reporter] = fields.ForeignKeyField(
        "fast_tmp.Reporter", null=True
    )
    participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(
        "fast_tmp.Team", related_name="events", through="event_team", backward_key="idEvent"
    )
    modified = fields.DatetimeField(auto_now=True)
    token = fields.TextField(default=generate_token)
    alias = fields.IntField(null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Node(Model):
    name = fields.CharField(max_length=10)


class Tree(Model):
    parent: fields.ForeignKeyRelation[Node] = fields.ForeignKeyField(
        "fast_tmp.Node", related_name="parent_trees"
    )
    child: fields.ForeignKeyRelation[Node] = fields.ForeignKeyField(
        "fast_tmp.Node", related_name="children_trees"
    )


class Address(Model):
    city = fields.CharField(max_length=64)
    street = fields.CharField(max_length=128)

    event: fields.OneToOneRelation[Event] = fields.OneToOneField(
        "fast_tmp.Event", on_delete=fields.CASCADE, related_name="address", pk=True
    )


class Team(Model):
    """
    Team that is a playing
    """

    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ManyToManyRelation[Event]
    alias = fields.IntField(null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Gender(str, Enum):
    male = "male"
    female = "female"


class Degree(IntEnum):
    unknow = 0
    bachelor = 1  # 学士
    master = 2  # 硕士
    doctor = 3  # 博士


class Role(Model):
    name = fields.CharField(max_length=32)
    age = fields.IntField()
    desc = fields.TextField()
    birthday = fields.DateField(null=True)
    money = fields.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal(10))
    height = fields.FloatField(null=True)
    married = fields.BooleanField(default=False)
    gender = fields.CharEnumField(Gender)
    degree = fields.IntEnumField(Degree, default=Degree.unknow)
    game_length = fields.BigIntField(default=0)  # 游戏时长，按秒计算
    avator = fields.BinaryField(null=True)  # 头像
    config = fields.JSONField(null=True)
    waiting_length = fields.TimeDeltaField(null=True)  # 等待时长
    max_time_length = fields.TimeField(default=datetime.time)  # 最长游戏时长
    uuid = fields.UUIDField(default=uuid.uuid4)
    level = fields.SmallIntField(default=0)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)


class Dec(Model):
    dec1 = fields.DecimalField(max_digits=10, decimal_places=2)
    dec2 = fields.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal(10))


class I1(IntEnum):
    one = 1
    two = 2


class For(Model):
    name = fields.CharField(max_length=32)

    def __str__(self):
        return self.name


class IntEnumField(Model):
    int_enum_1 = fields.IntEnumField(I1, null=True)
    int_enum_2 = fields.IntEnumField(I1, default=I1.one)
    bool_1 = fields.BooleanField(null=True)
    bool_2 = fields.BooleanField(default=True)
    datetime_1 = fields.DatetimeField(null=True)
    datetime_2 = fields.DatetimeField(default=datetime.datetime.now)
    datetime_3 = fields.DatetimeField(default=datetime.datetime.fromtimestamp(0))
    datetime_4 = fields.DatetimeField()
    foreignkey_1 = fields.ForeignKeyField("fast_tmp.For", null=True, related_name="foreignkey_1s")
