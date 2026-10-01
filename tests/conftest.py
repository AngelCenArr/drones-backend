import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import collections, collections.abc
collections.MutableMapping = collections.abc.MutableMapping

from app.main import app
from app.db.base_class import Base
from app.api import deps
from app.core.security import get_password_hash, create_access_token
from app.models.user import Rol, Usuario

# Base de datos SQLite en memoria para tests aislados
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Crear roles iniciales
    admin_rol = Rol(id=1, nombre="ADMIN", descripcion="Administrador")
    guardia_rol = Rol(id=2, nombre="GUARDIA", descripcion="Guardia de seguridad")
    db.add_all([admin_rol, guardia_rol])

    # Crear usuarios de prueba
    admin_user = Usuario(
        id=1,
        nombre="Admin Test",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        rol_id=1,
        activo=True
    )
    guardia_user = Usuario(
        id=2,
        nombre="Guardia Test",
        email="guardia@test.com",
        password_hash=get_password_hash("password123"),
        rol_id=2,
        activo=True
    )
    db.add_all([admin_user, guardia_user])
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token():
    return create_access_token(subject=1)

@pytest.fixture
def guardia_token():
    return create_access_token(subject=2)