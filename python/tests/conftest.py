import pytest
from data import store


@pytest.fixture(autouse=True)
def clear_store():
    store.clear()
    yield
    store.clear()
