# Configure les tests asynchrones pour utiliser asyncio.
import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
