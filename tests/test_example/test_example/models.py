"""
This is the testing Models
"""
import binascii
import datetime
import os
from enum import Enum, IntEnum

from tortoise import fields
from tortoise.models import Model


def generate_token():
    return binascii.hexlify(os.urandom(16)).decode("ascii")


class Author(Model):
    name = fields.CharField(max_length=255)


class Book(Model):
    name = fields.CharField(max_length=255)
    author = fields.ForeignKeyField("fast_tmp.Author", related_name="books")
    rating = fields.FloatField()


class BookNoConstraint(Model):
    name = fields.CharField(max_length=255)
    author = fields.ForeignKeyField("fast_tmp.Author", db_constraint=False)
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
    """ Whom is assigned as the reporter """

    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ReverseRelation["Event"]

    class Meta:
        table = "re_port_er"

    def __str__(self):
        return self.name


class Event(Model):
    """ Events on the calendar """

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
    parent = fields.ForeignKeyField("fast_tmp.Node", related_name="parent_trees")
    child = fields.ForeignKeyField("fast_tmp.Node", related_name="children_trees")


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
        unique_together = ("name",)

    def __str__(self):
        return self.name


class Gender(str, Enum):
    male = "male"
    womale = "womale"


class Degree(IntEnum):
    unknow = 0
    bachelor = 1  # 学士
    master = 2  # 硕士
    doctor = 3  # 博士


class FieldTesting(Model):
    name = fields.CharField(max_length=32)
    age = fields.IntField()
    desc = fields.TextField()
    # birthday = fields.DateField()
    # created_time = fields.DatetimeField(auto_now_add=True,null=True)
    money = fields.DecimalField(max_digits=10, decimal_places=2)
    height = fields.FloatField()
    married = fields.BooleanField(default=False)
    gender = fields.CharEnumField(Gender)
    degree = fields.IntEnumField(Degree, )
    game_length = fields.BigIntField(default=0)  # 游戏时长，按秒计算
    avator = fields.BinaryField()  # 头像
    config = fields.JSONField()
    waiting_length = fields.TimeDeltaField()  # 等待时长
    max_time_length = fields.TimeField(default=datetime.time())  # 最长游戏时长
    uuid = fields.UUIDField()
    level = fields.SmallIntField(default=0)
    name_inline = fields.CharField(max_length=32)
    age_inline = fields.IntField()
    desc_inline = fields.TextField()
    # birthday_inline = fields.DateField()
    # update_time_inline = fields.DatetimeField(auto_now=True,null=True)
    money_inline = fields.DecimalField(max_digits=10, decimal_places=2)
    height_inline = fields.FloatField()
    married_inline = fields.BooleanField(default=False)
    gender_inline = fields.CharEnumField(Gender)
    degree_inline = fields.IntEnumField(Degree, )
    game_length_inline = fields.BigIntField(default=0)  # 游戏时长，按秒计算
    avator_inline = fields.BinaryField()  # 头像
    config_inline = fields.JSONField()
    waiting_length_inline = fields.TimeDeltaField()  # 等待时长
    max_time_length_inline = fields.TimeField(default=datetime.time())  # 最长游戏时长
    uuid_inline = fields.UUIDField()
    level_inline = fields.SmallIntField(default=0)