import os
import tempfile
import shutil

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from backend import create_app
from backend.database.util import init_db, get_session


@pytest.fixture
def app() -> Flask:
    """
    A fixture to yield a new SMARTSexplore app connected to a temporary database.
    """
    with tempfile.TemporaryDirectory() as tmp_instance_dir:
        db_fd, db_filename = tempfile.mkstemp()
        try:
            app = create_app({
                'DATABASE': 'sqlite:///' + db_filename,
                'TESTING': True
            }, instance_path=tmp_instance_dir)
            with app.app_context():
                init_db()
                yield app
        finally:
            os.close(db_fd)
            os.unlink(db_filename)


@pytest.fixture
def full_app() -> Flask:
    """
    A fixture to yield a SMARTSexplore app connected to a previously prepared instance directory,
    containing a populated SQLite database and pre-rendered SVG images (tests/_instance).
    """
    test_instance_path = os.path.join(os.path.dirname(__file__), 'tests', '_instance')

    with tempfile.TemporaryDirectory() as tmp_instance_dir:
        shutil.copytree(test_instance_path, tmp_instance_dir, dirs_exist_ok=True)
        assert os.path.isfile(os.path.join(tmp_instance_dir, 'db.sqlite')),\
            "db.sqlite not present in temporary instance dir for some reason!"

        app = create_app({
            'DATABASE': 'sqlite:///' + os.path.join(tmp_instance_dir, 'db.sqlite'),
            'TESTING': True
        }, instance_path=tmp_instance_dir)
        with app.app_context():
            yield app


@pytest.fixture
def session(app: Flask) -> Session:
    """
    A fixture to yield an SQLAlchemy database session to the temporary database as created
    internally by the :func:`app` fixture.
    """
    yield get_session()


@pytest.fixture
def full_session(full_app: Flask) -> Session:
    """
    A fixture to yield an SQLAlchemy database session to the populated database of the
    :func:`full_app` fixture.
    """
    yield get_session()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """
    A fixture to yield a FlaskClient within the appcontext of a "fake" SMARTSexplore app,
    i.e., an app where the database is a temporary file used as an SQLite database.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def full_client(full_app: Flask) -> FlaskClient:
    """
    A fixture to yield a FlaskClient within the appcontext of the :func:`full_app` pre-populated
    test application.
    """
    with full_app.test_client() as client:
        yield client
