from flaskr import create_app
from flaskr.backend import Backend
import pytest,unittest
from unittest.mock import MagicMock,patch
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
    with patch('flaskr.backend.Backend.get_all_page_names') as mock_get_all_page_names: 
        mock_instance=MagicMock()
        mock_instance.get_all_page_names.return_value = ['Page1','Page2']
        mock_get_all_page_names.return_value=mock_instance
        

        yield mock_instance

           


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Notable women in stem" in resp.data

# TODO(Project 1): Write tests for other routes.



def test_page_index(client,mock_get_all_page_names):
        mock_get_all_page_names()
        
        resp=client.get("/pages")
        assert resp.status_code == 200
        assert b'Pages contained in this Wiki'in resp.data
        #assert b'<ul>Page1</ul>' in resp.data
        #assert b'Page2' in resp.data
        #mock_get_all_page_names.assert_called_once_with()

def test_upload(client):
    resp=client.get("/upload")
    assert resp.status_code == 200
    assert b"Upload" in resp.data

def test_about(client):
    resp=client.get("/about")
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data

def test_show_wiki(client):
    resp=client.get("/pages")
    assert resp.status_code == 200    
