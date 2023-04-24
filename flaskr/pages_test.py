from flaskr import create_app
from unittest.mock import patch, MagicMock, Mock
from flask import session
from flaskr.pages import is_logged_in
from flaskr.backend import Backend
import pytest, io
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


def test_upload_get(client):
    with client.session_transaction() as session:
        session["username"] = "user"
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"Upload" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.upload_file")
def test_upload_post_no_image(mock_backend, mock_storage, client):
    with client.session_transaction() as session:
        session["username"] = "user"
    resp = client.post("/upload",
                       data={
                           "page_name": "test",
                           "image_url": "",
                           "file": (io.BytesIO(b"this is a test"), "file.txt")
                       })
    assert resp.status_code == 200
    assert b"user" in resp.data
    assert b"Upload" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.Backend.upload_file")
def test_upload_post_image(mock_backend, mock_storage, client):
    with client.session_transaction() as session:
        session["username"] = "user"
    resp = client.post("/upload",
                       data={
                           "page_name": "test",
                           "image_url": "link",
                           "file": (io.BytesIO(b"this is a test"), "file.txt")
                       })
    assert resp.status_code == 200
    assert b"user" in resp.data
    assert b"Upload" in resp.data


def ignored_test_about(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.edit_page_data")
@patch("flaskr.pages.date")
def test_edit_form(mock_date, mock_edit_data, mock_json, mock_backend, client):
    mock_date.return_value.today.return_value.strftime = "4/12/23"
    with client.session_transaction() as session:
        session["username"] = "user"
    resp = client.post("/edit-form",
                       data={
                           "page-name": "test",
                           "editor": "user",
                           "content": "edit content"
                       },
                       follow_redirects=True)

    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert resp.request.path == "/pages/test"
    assert b"TEST" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
def test_edit_page_user_edits(mock_pages_edit, mock_user_edits, mock_json,
                              mock_backend, client):

    user_edit = {
        "Name": "test-page",
        "Author": "Author's name",
        "Status": 1,
        "Edit": "my edit",
        "Date": "edit date"
    }

    edited_page_data = {
        "Name":
            "author-page",
        "Author":
            "Author's name",
        "Content":
            "Women in STEM",
        "Image":
            "link",
        "Date":
            "Date",
        "Edits": [{
            "Content": "edited content",
            "Date": "edit date",
            "Status": 1,
            "Editor": "editor"
        }]
    }

    mock_pages_edit.return_value = [edited_page_data]
    mock_user_edits.return_value = [user_edit]
    with client.session_transaction() as session:
        session["username"] = "user"
        session["show_user_edits"] = True
    resp = client.get("/edit-page")
    assert resp.status_code == 200
    assert b'test-page' in resp.data
    assert b"author-page" not in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
def test_edit_page_author_pages_edits(mock_pages_edit, mock_user_edits,
                                      mock_json, mock_backend, client):

    user_edit = {
        "Name": "test-page",
        "Author": "Author's name",
        "Status": 1,
        "Edit": "my edit",
        "Date": "edit date"
    }

    edited_page_data = {
        "Name":
            "author-page",
        "Author":
            "Author's name",
        "Content":
            "Women in STEM",
        "Image":
            "link",
        "Date":
            "Date",
        "Edits": [{
            "Content": "edited content",
            "Date": "edit date",
            "Status": 1,
            "Editor": "editor"
        }]
    }

    mock_pages_edit.return_value = [edited_page_data]
    mock_user_edits.return_value = [user_edit]
    with client.session_transaction() as session:
        session["username"] = "user"
        session["show_user_edits"] = False
    resp = client.get("/edit-page")
    assert resp.status_code == 200
    assert b'test-page' not in resp.data
    assert b"author-page" in resp.data


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
@patch("flaskr.backend.Backend.is_username_unique", return_value=True)
@patch("flaskr.backend.Backend.sign_up")
def test_signup_post(mock_backend, mock_is_unique, mock_storage, client):
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


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
def test_show_user_edits(mock_pages_edit, mock_user_edits, mock_json,
                         mock_backend, client):

    with client.session_transaction() as sess:
        sess["username"] = "user"
        sess["show_user_edits"] = False

    with client:
        resp = client.get("/show-user-edits", follow_redirects=True)

        assert len(resp.history) == 1
        assert resp.status_code == 200
        assert resp.request.path == "/edit-page"
        assert session["show_user_edits"] == True


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
def test_show_page_edits(mock_pages_edit, mock_user_edits, mock_json,
                         mock_backend, client):

    with client.session_transaction() as sess:
        sess["username"] = "user"
        sess["show_user_edits"] = True

    with client:
        resp = client.get("/show-page-edits", follow_redirects=True)

        assert len(resp.history) == 1
        assert resp.status_code == 200
        assert resp.request.path == "/edit-page"
        assert session["show_user_edits"] == False


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
@patch("flaskr.backend.Backend.author_edit_action")
def test_upload_edit_accepted(mock_edit_action, mock_pages_edit,
                              mock_user_edits, mock_json, mock_backend, client):

    user_edit = {
        "Name": "test",
        "Author": "Author's name",
        "Status": 2,
        "Edit": "my edit",
        "Date": "edit date"
    }

    mock_user_edits.return_value = [user_edit]

    with client.session_transaction() as session:
        session["username"] = "user"
        session["show_user_edits"] = True

    resp = client.post("/update-edit",
                       data={
                           "edit-page-name": "test",
                           "edit-action": "Accept",
                       },
                       follow_redirects=True)

    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert resp.request.path == "/edit-page"
    assert b"green" in resp.data
    assert b"Accepted" in resp.data


@patch("flaskr.backend.storage")
@patch("flaskr.backend.json")
@patch("flaskr.backend.Backend.get_user_edits")
@patch("flaskr.backend.Backend.get_user_pages_edits")
@patch("flaskr.backend.Backend.author_edit_action")
def test_upload_edit_declined(mock_edit_action, mock_pages_edit,
                              mock_user_edits, mock_json, mock_backend, client):

    user_edit = {
        "Name": "test",
        "Author": "Author's name",
        "Status": 3,
        "Edit": "my edit",
        "Date": "edit date"
    }

    mock_user_edits.return_value = [user_edit]

    with client.session_transaction() as session:
        session["username"] = "user"
        session["show_user_edits"] = True

    resp = client.post("/update-edit",
                       data={
                           "edit-page-name": "test",
                           "edit-action": "Declined",
                       },
                       follow_redirects=True)

    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert resp.request.path == "/edit-page"
    assert b"red" in resp.data
    assert b"Declined" in resp.data


def test_page_not_found(client):
    resp = client.get("/random-page")
    assert resp.status_code == 404
    assert b"The page you are looking for does not exist" in resp.data


def test_is_logged_in(client):

    @is_logged_in
    def assert_false():
        assert False

    assert_false


def test_upload_translation(client):
    with client.session_transaction() as session:
        session["username"] = "user"
        session["show_user_edits"] = True

    resp = client.get("/translation")

    assert resp.request.path == "/translation"
    assert resp.status_code == 200
    assert b"Please enter new translations:" in resp.data
