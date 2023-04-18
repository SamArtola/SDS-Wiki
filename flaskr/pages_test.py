from flaskr import create_app
from unittest.mock import patch, MagicMock, Mock
from flask import session
from flaskr.backend import Backend
import pytest
from google.cloud import storage


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


@pytest.fixture
def mock_get_all_page_names():
    with patch('flaskr.backend.Backend.get_all_page_names'
              ) as mock_get_all_page_names:
        mock_instance = MagicMock()
        mock_instance.get_all_page_names.return_value = ['Page1', 'Page2']
        mock_get_all_page_names.return_value = mock_instance


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Notable women in stem" in resp.data


def test_login_page_get(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'form action="/login"' in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(False, "Wrong password"))
def test_login_password_mismatch(mock_backend, mock_storage, client):

    resp = client.post("/login",
                       data={
                           "name": "username",
                           "password": "password",
                       })
    assert resp.status_code == 200
    assert b"Wrong password" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(False, "User not found"))
def test_login_no_user(mock_backend, mock_storage, client):

    resp = client.post("/login",
                       data={
                           "name": "username",
                           "password": "password",
                       })
    assert resp.status_code == 200
    assert b"User not found" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(True, None))
def test_login_successful_redirects(mock_backend, mock_storage, client):
    resp = client.post("/login",
                       data={
                           "name": "username",
                           "password": "password",
                       },
                       follow_redirects=True)
    assert resp.status_code == 200
    assert len(resp.history) == 1
    assert resp.request.path == "/"


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_in", return_value=(True, None))
def test_login_successful_displays_user(mock_backend, mock_storage, client):
    with client:
        resp = client.post("/login",
                           data={
                               "name": "username",
                               "password": "password",
                           },
                           follow_redirects=True)
        assert session['username'] == "username"
    assert b"Hi, username" in resp.data
    assert b"Login" not in resp.data


def test_logout(client):
    with client.session_transaction() as session:
        session["username"] = "username"
    resp = client.get("/logout", follow_redirects=True)
    assert not b"Hi, username" in resp.data
    assert resp.request.path == "/login"


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


def ignored_test_page_index(client, mock_get_all_page_names):
    mock_get_all_page_names

    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b'Pages contained in this Wiki' in resp.data
    #assert b'<ul>Page1</ul>' in resp.data
    #assert b'Page2' in resp.data
    #mock_get_all_page_names.assert_called_once_with()


def test_upload(client):
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"Upload" in resp.data


def ignored_test_about(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data


def test_show_wiki(client):
    file = "test file"
    page_name = "testing"
    with patch("flaskr.backend.Backend.get_wiki_page", return_value=file):
        resp = client.get(f"/pages/<{page_name}>")
        assert resp.status_code == 200
        assert file in resp.data.decode("utf-8")


def test_quotes(client):
    resp = client.get("/quotes")
    assert resp.status_code == 200
    assert b"Nichelle Nichols" in resp.data


def test_kathjohn(client):
    resp = client.get("/kathjohn")
    assert resp.status_code == 200
    assert b"Spacecraft Controls Branch" in resp.data


def test_signup_get(client):
    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b"Re-enter Password" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.sign_up", return_value=(True, 'yvette'))
def test_signup_post(mock_backend, mock_storage, client):
    resp = client.post("/signup", data={'name': 'yvette', 'pwd': 'abc'})
    assert resp.status_code == 200
    assert b"Hi, yvette" in resp.data


def test_signup_post_incomplete_form(client):
    resp = client.post("/signup", data={'name': 'Mayo', 'pwd': ''})
    assert resp.status_code == 200
    assert b"Please fill all required fields" in resp.data


@patch("flaskr.backend.Backend.is_username_unique", return_value=False)
def test_signup_user_exist(mock_backend, client):
    resp = client.post("/signup", data={'name': 'Mayo', 'pwd': 'abc'})
    mock_backend.is_username_unique()
    assert b"Ooops, that username is taken." in resp.data

def test_fun_get(client):
    resp = client.get("/fun")
    assert resp.status_code == 200
    assert b"Have fun learning about notable women in STEM" in resp.data

def test_createcard_get(client):
    resp = client.get('/createcard')
    assert resp.status_code == 200
    assert b"Create Flashcard" in resp.data


