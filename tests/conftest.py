from typing import Generator

from fast_tmp.models import Base, User
import pytest
from fast_tmp.db import engine, get_db_session


@pytest.fixture(autouse=True, scope="function")
def prepare_database() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)
    session=next(get_db_session())
    user=User(username="root")
    user.set_password("root")
    session.add(user)
    session.commit()
    yield
    Base.metadata.drop_all(engine)

def test_init():
    pass