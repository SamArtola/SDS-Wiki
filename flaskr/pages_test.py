from flaskr import create_app
from unittest.mock import patch, MagicMock, Mock
from flask import session
from flaskr.backend import Backend 
import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Notable women in stem" in resp.data

# TODO(Project 1): Write tests for other routes.
def test_login_page_get(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'form action="/login"' in resp.data

@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(False, "Wrong password"))
def test_login_password_mismatch(mock_backend, mock_storage, client):

    resp = client.post("/login", data = {
        "name": "username",
        "password": "password",
    })
    assert resp.status_code == 200
    assert b"Wrong password" in resp.data

@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(False, "User not found"))
def test_login_no_user(mock_backend, mock_storage, client):

    resp = client.post("/login", data = {
        "name": "username",
        "password": "password",
    })
    assert resp.status_code == 200
    assert b"User not found" in resp.data

@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(True, None))
def test_login_successful_redirects(mock_backend, mock_storage, client):
    resp = client.post("/login", data = {
        "name": "username",
        "password": "password",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert len(resp.history) == 1    
    assert resp.request.path == "/"
    
@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(True, None))
def test_login_successful_displays_user(mock_backend, mock_storage, client):
    with client:
        resp = client.post("/login", data = {
            "name": "username",
            "password": "password",
        }, follow_redirects=True)
        assert session['username'] == "username"
    assert b"Hi, username" in resp.data

def test_scholarship_page(client):
    resp = client.get("/pages/scholarships")
    assert resp.status_code == 200
    assert b"Below are some interesting scholarship opportunities for women studying STEM in North America." in resp.data

def test_opportunities_page(client):
    resp = client.get("/pages/opportunities")
    assert resp.status_code == 200
    assert b"Below are some interesting growth opportunities for women studying STEM in North America." in resp.data

def test_joy_buolamwini_page(client):
    resp = client.get("/pages/joy_buolamwini")
    print(resp.data)
    assert resp.status_code == 200
    assert b"Dr. Joy Buolamwini, recognized by Fortune Magazine" in resp.data