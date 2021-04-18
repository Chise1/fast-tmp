from typing import List, Type, cast

from pydantic import BaseModel


class A(BaseModel):
    x: int = 0


print(A.__annotations__)
lname = "paging"
properties = {"__annotations__": {"data": List[A], "count": int}}  # type: ignore
# Creating Pydantic class for the properties generated before
model = cast(Type[BaseModel], type(lname, (BaseModel,), properties))
print(model.__annotations__)
s = model(data=[A(x=1), A(x=2)], count=2)
print(s.dict())
