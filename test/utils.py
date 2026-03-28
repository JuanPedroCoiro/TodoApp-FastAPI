from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..routers.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL = 'sqlite://'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'juanpeco', 'user_id': 1, 'user_role': 'admin'}

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn to code',
        description='Learn to code everyday',
        priority=5,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo

    db.query(Todos).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user():
    user = Users(
        username='juanpeco',
        email='juanpeco@mail.com',
        first_name='juanpeco',
        last_name='juanpeco',
        hashed_password=bcrypt_context.hash('pass123'),
        role='admin',
        phone_number='+1 123 456 789',
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    db.query(Users).delete()
    db.commit()
    db.close()