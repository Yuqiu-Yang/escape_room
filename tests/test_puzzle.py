import pytest
from escape_room.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log in" in response.data

    auth.login()
    response = client.get('/')
    assert b'Ready' in response.data
    assert b'href="/puzzle/1"' in response.data

@pytest.mark.parametrize('path', (
    '/puzzle/1',
))
def test_login_required(client, path):
    response = client.get('/')
    response = client.get(path)
    assert b"login" in response.data