from pydantic import BaseModel


class A(BaseModel):
    a: str


class B(A):
    b: str


class C(BaseModel):
    a: A


print(C(a=B(a="a", b="b")).json())
