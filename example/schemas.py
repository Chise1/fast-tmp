# 这里主要保存根据model生成的schema
from fast_tmp.utils.pydantic import pydantic_model_creator

from .models import Book

x1 = pydantic_model_creator(Book, name="x1", include=("name", "author_id", "author", "author.id"))
x2 = pydantic_model_creator(
    Book, name="x2", include=("name", "author_id", "author", "author.id", "author.name")
)
a1 = x1.schema()
a2 = x2.schema()
# a1 = {'title': 'x1', 'type': 'object', 'properties': {
#     'name': {'title': 'Name', 'maxLength': 255, 'type': 'string'},
#     'author': {'title': 'Author', 'allOf': [
#         {'$ref': '#/definitions/test_example.models.Author.leaf'}]}},
#       'required': ['name', 'author'], 'additionalProperties': False,
#       'definitions': {'test_example.models.Author.leaf': {'title': 'Author',
#                                                           'type': 'object',
#                                                           'properties': {'id': {
#                                                               'title': 'Id',
#                                                               'minimum': 1,
#                                                               'maximum': 2147483647,
#                                                               'type': 'integer'}},
#                                                           'required': ['id'],
#                                                           'additionalProperties': False}}}
# a2 = {'title': 'x2', 'type': 'object', 'properties': {
#     'name': {'title': 'Name', 'maxLength': 255, 'type': 'string'},
#     'author': {'title': 'Author', 'allOf': [
#         {'$ref': '#/definitions/test_example.models.Author.leaf'}]}},
#       'required': ['name', 'author'], 'additionalProperties': False,
#       'definitions': {'test_example.models.Author.leaf': {'title': 'Author',
#                                                           'type': 'object',
#                                                           'properties': {'id': {
#                                                               'title': 'Id',
#                                                               'minimum': 1,
#                                                               'maximum': 2147483647,
#                                                               'type': 'integer'}},
#                                                           'required': ['id'],
#                                                           'additionalProperties': False}}}
