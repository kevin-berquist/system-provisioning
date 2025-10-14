import importlib

import pytest

from backend.app import create_app

APP_MODULE = importlib.import_module('backend.app.__init__')


@pytest.fixture
def auth_app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY='test',
        ENFORCE_AUTH=False,
    )

    @app.route('/ping')
    def ping():
        return 'pong'

    yield app


def test_request_passes_when_auth_disabled(auth_app):
    client = auth_app.test_client()
    response = client.get('/ping')
    assert response.status_code == 200


def test_request_blocks_when_cookie_missing(auth_app):
    auth_app.config.update(ENFORCE_AUTH=True, AUTH_URL='https://example.com/auth')
    client = auth_app.test_client()
    response = client.get('/ping')
    assert response.status_code == 401


def test_request_blocks_when_auth_denied(auth_app, monkeypatch):
    auth_app.config.update(ENFORCE_AUTH=True, AUTH_URL='https://example.com/auth')

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'NOT AUTH'

    def fake_urlopen(req, timeout=5):
        return FakeResponse()

    monkeypatch.setattr(APP_MODULE.urllib.request, 'urlopen', fake_urlopen)

    client = auth_app.test_client()
    client.set_cookie('UserAccount', 'demo')
    response = client.get('/ping')
    assert response.status_code == 401


def test_request_allows_when_auth_ok(auth_app, monkeypatch):
    auth_app.config.update(ENFORCE_AUTH=True, AUTH_URL='https://example.com/auth')

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'prefix AUTH OK suffix'

    def fake_urlopen(req, timeout=5):
        return FakeResponse()

    monkeypatch.setattr(APP_MODULE.urllib.request, 'urlopen', fake_urlopen)

    client = auth_app.test_client()
    client.set_cookie('UserAccount', 'demo')
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'pong'
