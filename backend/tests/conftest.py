import shutil
import tempfile

import pgserver
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import get_db
from app.main import app
from app.models import Base


@pytest.fixture(scope="session")
def pg_server():
    tmp_dir = tempfile.mkdtemp(prefix="sales_intelligence_test_pg_")
    server = pgserver.get_server(tmp_dir)
    yield server
    server.cleanup()
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def engine(pg_server):
    uri = pg_server.get_uri().replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine):
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
