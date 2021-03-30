import os

import pytest
from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
    initializer(["tests.testmodels", "fast_tmp.models"], db_url=db_url, app_label="fast_tmp")
    request.addfinalizer(finalizer)
