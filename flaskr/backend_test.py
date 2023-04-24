import pytest
from flaskr.backend import Backend
import os, io, hashlib, werkzeug.datastructures, json
from unittest.mock import patch, Mock, MagicMock, mock_open
from google.cloud import storage

# TODO(Project 1): Write tests for Backend methods.


@patch('hashlib.blake2b')
@patch('flaskr.backend.storage.Client')
def test_sign_in_successful(mock_client, mock_hashlib):
    mock_hashlib.return_value.hexdigest.return_value = 'amara'
    mock_bucket = Mock()
    mock_bucket.get_blob.return_value.download_as_text.return_value = 'amara'
    mock_client().bucket.return_value = mock_bucket

    backend = Backend(user_bucket='test_user_bucket')
    signed_in, err = backend.sign_in('test_user', 'test password')

    assert (signed_in, err) == (True, None)
    mock_client().bucket.assert_called_once_with('test_user_bucket')
    mock_bucket.get_blob.assert_called_once_with('users-data/test_user')
    mock_bucket.get_blob.return_value.download_as_text.assert_called_once()


@patch('hashlib.blake2b')
@patch('flaskr.backend.storage.Client')
def test_sign_in_user_not_found(mock_client, mock_hashlib):
    mock_hashlib.return_value.hexdigest.return_value = 'amara'
    mock_bucket = Mock()
    mock_bucket.get_blob.return_value = None
    mock_client().bucket.return_value = mock_bucket

    backend = Backend(user_bucket='test_user_bucket')
    signed_in, err = backend.sign_in('test_user', 'test password')

    assert (signed_in, err) == (False, "User not found")
    mock_client().bucket.assert_called_once_with('test_user_bucket')
    mock_bucket.get_blob.assert_called_once_with('users-data/test_user')


@patch('hashlib.blake2b')
@patch('flaskr.backend.storage.Client')
def test_sign_in_password_mismatch(mock_client, mock_hashlib):
    mock_hashlib.return_value.hexdigest.return_value = 'amara'
    mock_bucket = Mock()
    mock_bucket.get_blob.return_value.download_as_text.return_value = 'james'
    mock_client().bucket.return_value = mock_bucket

    backend = Backend(user_bucket='test_user_bucket')
    signed_in, err = backend.sign_in('test_user', 'test password')

    assert (signed_in, err) == (False, "Wrong password")
    mock_client().bucket.assert_called_once_with('test_user_bucket')
    mock_bucket.get_blob.assert_called_once_with('users-data/test_user')
    mock_bucket.get_blob.return_value.download_as_text.assert_called_once()


# Sam: Get wiki page, all page names, upload, get image (if time, not being used in general)


@patch('json.loads')
@patch('flaskr.backend.storage.Client')
@patch('flaskr.backend.Backend.translate_page')
def test_get_wiki_page(mock_translate, mock_storage_client, mock_json):
    page_data = {
        "Name": "name",
        "Author": "Author's name",
        "Content": "Content",
        "Image": "",
        "Date": "Date",
        "Edits": []
    }
    mock_translate.return_value = "Content"
    mock_json.return_value = page_data
    mock_bucket = MagicMock()
    mock_bucket.return_value.blob.return_value.download_as_text.return_value = '''{"Name": "name", "Author": "Author's name", "Content":  "Content",
    "Image": "", "Date": "Date", "Edits":[]}'''

    mock_storage_client.return_value.bucket.return_value = mock_bucket

    backend = Backend(content_bucket="test_wikis-content")
    page_content = backend.get_wiki_page("test-page", "EN")

    mock_storage_client.assert_called_once()
    mock_storage_client.return_value.bucket.assert_called_once_with(
        "test_wikis-content")
    mock_bucket.blob.assert_called_once_with("uploaded-pages/test-page")
    mock_bucket.blob.return_value.download_as_text.assert_called_once()
    assert page_content == page_data


@patch.object(storage, 'Client')
def test_get_all_page_names(mock_storage_client):
    #Mock GCS
    mock_storage_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_storage_client.return_value = mock_storage_client_instance
    mock_storage_client_instance.bucket.return_value = mock_bucket

    #creating Mocks to call upon
    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()
    mock_blob1.name = "uploaded-pages/page1"
    mock_blob2.name = "uploaded-pages/page2"

    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

    backend = Backend()
    page_list = backend.get_all_page_names()

    #asserting
    mock_storage_client.assert_called_once_with()
    mock_storage_client_instance.bucket.assert_called_once_with(
        backend.content_bucket)
    mock_bucket.list_blobs.assert_called_once_with(prefix='uploaded-pages/')
    assert "page1" in page_list
    assert "page2" in page_list
    #assert page_list == ["page1","page2"]      #get all page names uses a set() so test fails sometimes


@patch("os.remove")
@patch('json.dumps')
@patch("flaskr.backend.storage.Client")
@patch("werkzeug.datastructures.FileStorage")
def test_upload_file_no_image(mock_file, mock_storage_client, mock_json,
                              mock_os):
    mock_file.filename = "test file.txt"
    file_data = "Women in STEM"

    fake_page = {
        "Name":
            "test-page",
        "Author":
            "Author's name",
        "Content":
            "Women in STEM",
        "Image":
            "https://storage.cloud.google.com/wikis-content/DEFAULT%20IMG.png",
        "Date":
            "Date",
        "Edits": []
    }

    json_string = '''{"Name": "test-page", "Author": "Author's name", "Content": "Women in STEM", "Image": "https://storage.cloud.google.com/wikis-content/DEFAULT%20IMG.png", "Date": "Date", "Edits": []}'''
    mock_json.return_value = json_string

    mock_bucket = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    with patch("builtins.open", mock_open(read_data=file_data)) as mocked_open:
        backend = Backend(content_bucket="test-content-bucket")
        backend.upload_file("test-page", "Author's name", mock_file, "Date")

    mocked_open.assert_called_once_with("test file.txt", "r")
    mock_storage_client.assert_called_once()
    mock_storage_client.return_value.bucket.assert_called_once_with(
        "test-content-bucket")
    mock_bucket.blob.assert_called_once_with("uploaded-pages/test-page")
    mock_bucket.blob.return_value.upload_from_string.assert_called_once_with(
        data=json_string, content_type='application/json')
    mock_os.assert_called_once_with("test file.txt")
    mock_json.assert_called_once_with(fake_page)
    mock_file.save.assert_called_once_with("test file.txt")


@patch("os.remove")
@patch('json.dumps')
@patch("flaskr.backend.storage.Client")
@patch("werkzeug.datastructures.FileStorage")
def test_upload_file_image(mock_file, mock_storage_client, mock_json, mock_os):
    mock_file.filename = "test file.txt"
    file_data = "Women in STEM"

    fake_page = {
        "Name": "test-page",
        "Author": "Author's name",
        "Content": "Women in STEM",
        "Image": "https://image.jpg",
        "Date": "Date",
        "Edits": []
    }

    json_string = '''{"Name": "test-page", "Author": "Author's name", "Content": "Women in STEM", "Image": "https://image.jpg", "Date": "Date", "Edits": []}'''
    mock_json.return_value = json_string

    mock_bucket = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    with patch("builtins.open", mock_open(read_data=file_data)) as mocked_open:
        backend = Backend(content_bucket="test-content-bucket")
        backend.upload_file("test-page", "Author's name", mock_file, "Date",
                            "https://image.jpg")

    mocked_open.assert_called_once_with("test file.txt", "r")
    mock_storage_client.assert_called_once()
    mock_storage_client.return_value.bucket.assert_called_once_with(
        "test-content-bucket")
    mock_bucket.blob.assert_called_once_with("uploaded-pages/test-page")
    mock_bucket.blob.return_value.upload_from_string.assert_called_once_with(
        data=json_string, content_type='application/json')
    mock_os.assert_called_once_with("test file.txt")
    mock_json.assert_called_once_with(fake_page)
    mock_file.save.assert_called_once_with("test file.txt")


@patch('flaskr.backend.storage.Client')
def test_get_users(mock_storage):
    mock_storage_client = MagicMock()
    mock_bucket = MagicMock()
    mock_storage.return_value = mock_storage_client
    mock_storage_client.bucket.return_value = mock_bucket

    mock_user_blob = MagicMock()
    mock_user_blob.name = 'users-data/mayo'
    mock_bucket.list_blobs.return_value = [mock_user_blob]

    backend = Backend()
    users = backend.get_users()

    mock_storage.assert_called_once_with()
    mock_bucket.list_blobs.assert_called_once_with(prefix='users-data/')
    assert users == {'mayo'}


@patch('flaskr.backend.storage.Client')
@patch('flaskr.backend.Backend.get_users', return_value={'mayo', 'samtest'})
def test_is_username_unique_true(mock_users, mock_storage):
    backend = Backend()
    status = backend.is_username_unique('wisdom')

    assert status


@patch('flaskr.backend.storage.Client')
@patch('flaskr.backend.Backend.get_users', return_value={'mayo', 'samtest'})
def test_is_username_unique_false(mock_users, mock_storage):
    backend = Backend()
    status = backend.is_username_unique('mayo')

    assert not status


@patch('hashlib.blake2b')
@patch('flaskr.backend.storage.Client')
def test_hash_pwd(mock_storage, mock_hashlib):
    backend = Backend()
    mock_hashlib.return_value.hexdigest.return_value = 'mayo'
    mock_pwd = backend.hash_pwd('many', 'abc')

    assert mock_pwd == 'mayo'


@patch('flaskr.backend.storage.Client')
@patch('flaskr.backend.Backend.hash_pwd', return_value='mayo')
def test_sign_up(mock_hash, mock_storage):
    mock_storage_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_user = MagicMock()
    mock_user_blob = MagicMock()
    mock_bucket.blob.return_value = mock_user
    mock_user.open.return_value.__enter__.return_value = mock_user_blob
    mock_storage_instance.bucket.return_value = mock_bucket
    mock_storage.return_value = mock_storage_instance

    backend = Backend()
    backend.sign_up('yvette', 'abcd')

    mock_user.open.assert_called_once()
    mock_user_blob.write.assert_called_once_with('mayo')


@patch('json.dumps')
@patch('json.loads')
@patch('flaskr.backend.storage.Client')
def test_edit_page_data(mock_client, mock_json_loads, mock_json_dumps):
    retrieved_page_data = {
        "Name": "test-page",
        "Author": "Author's name",
        "Content": "Women in STEM",
        "Image": "link",
        "Date": "Date",
        "Edits": []
    }
    edited_page_data_string = '''{"Name": "test-page", "Author": "Author's name", "Content": "Women in STEM", "Image": "link", "Date": "Date", "Edits": [{"Content": "edited content", "Date": "edit date", "Status": 1, "Editor": "editor"}]}'''
    retrieved_page_string = '''{"Name": "test-page", "Author": "Author's name", "Content":  "Women in STEM",
    "Image": "link", "Date": "Date", "Edits":[]}'''
    edited_page_data = {
        "Name":
            "test-page",
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

    mock_json_loads.return_value = retrieved_page_data
    mock_json_dumps.return_value = edited_page_data_string

    mock_bucket = MagicMock()
    mock_bucket.get_blob.return_value.download_as_text.return_value = retrieved_page_string
    mock_client.return_value.bucket.return_value = mock_bucket

    backend = Backend(content_bucket="test-wikis-content")
    backend.edit_page_data("test-page", "edited content", "edit date", "editor")

    mock_client.assert_called_once()
    mock_client.return_value.bucket.assert_called_once_with(
        "test-wikis-content")
    mock_bucket.get_blob.assert_called_once_with("uploaded-pages/test-page")
    mock_bucket.get_blob.return_value.download_as_text.assert_called_once()
    mock_json_loads.assert_called_once_with(retrieved_page_string)
    mock_json_dumps.assert_called_once_with(edited_page_data)
    mock_bucket.get_blob.return_value.upload_from_string.assert_called_once_with(
        data=edited_page_data_string, content_type='application/json')


@patch('json.loads')
@patch('flaskr.backend.storage.Client')
def test_get_all_uploaded_pages(mock_client, mock_json):
    default_mock_blob = MagicMock()
    mock_blob = MagicMock()
    edited_page_data_string = '''{"Name": "test-page", "Author": "Author's name", "Content": "Women in STEM", "Image": "link", "Date": "Date", "Edits": [{"Content": "edited content", "Date": "edit date", "Status": 1, "Editor": "editor"}]}'''
    edited_page_data = {
        "Name":
            "test-page",
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

    mock_blob.download_as_text.return_value = edited_page_data_string

    mock_client.return_value.list_blobs.return_value = [
        default_mock_blob, mock_blob
    ]

    mock_json.return_value = edited_page_data
    backend = Backend(content_bucket="test-content-bucket")
    uploaded_pages = backend.get_all_uploaded_pages()

    assert uploaded_pages == [edited_page_data]
    mock_blob.download_as_text.assert_called_once()
    mock_client.assert_called_once()
    mock_client.return_value.list_blobs.assert_called_once_with(
        "test-content-bucket", prefix="uploaded-pages/")
    mock_json.assert_called_once_with(edited_page_data_string)


@patch('flaskr.backend.Backend.get_all_uploaded_pages')
@patch('flaskr.backend.storage.Client')
def test_get_user_edits(mock_client, mock_get_all_uploaded_pages):

    edited_page_data = {
        "Name":
            "test-page",
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

    mock_get_all_uploaded_pages.return_value = [edited_page_data]

    user_edit = {
        "Name": "test-page",
        "Author": "Author's name",
        "Status": 1,
        "Edit": "edited content",
        "Date": "edit date"
    }
    backend = Backend()
    user_edits = backend.get_user_edits("editor")

    assert [user_edit] == user_edits
    mock_client.assert_called_once()
    mock_get_all_uploaded_pages.assert_called_once()


@patch('flaskr.backend.Backend.get_all_uploaded_pages')
@patch('flaskr.backend.storage.Client')
def test_get_user_pages_edits(mock_client, mock_get_all_uploaded_pages):

    edited_page_data = {
        "Name":
            "test-page",
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

    mock_get_all_uploaded_pages.return_value = [edited_page_data]

    backend = Backend()
    user_edits = backend.get_user_pages_edits("Author's name")

    assert [edited_page_data] == user_edits
    mock_client.assert_called_once()
    mock_get_all_uploaded_pages.assert_called_once()


@pytest.mark.parametrize("action,result,page_data", [
    pytest.param(
        "Accept",
        '''{"Name": "test-page", "Author": "Author's name", "Content": "edited content", "Image": "link", "Date": "Date", "Edits": [{"Content": "edited content", "Date": "edit date", "Status": 2, "Editor": "editor"}]}''',
        {
            "Name":
                "test-page",
            "Author":
                "Author's name",
            "Content":
                "edited content",
            "Image":
                "link",
            "Date":
                "Date",
            "Edits": [{
                "Content": "edited content",
                "Date": "edit date",
                "Status": 2,
                "Editor": "editor"
            }]
        },
        id="Accepted edit"),
    pytest.param(
        "Decline",
        '''{"Name": "test-page", "Author": "Author's name", "Content": "Women in STEM", "Image": "link", "Date": "Date", "Edits": [{"Content": "edited content", "Date": "edit date", "Status": 3, "Editor": "editor"}]}''',
        {
            "Name":
                "test-page",
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
                "Status": 3,
                "Editor": "editor"
            }]
        },
        id="Declined edit")
])
@patch('json.dumps')
@patch('flaskr.backend.Backend.get_wiki_page')
@patch('flaskr.backend.storage.Client')
def test_author_edit_action(mock_client, mock_get_wiki_page, mock_json, action,
                            result, page_data):

    edited_page_data = {
        "Name":
            "test-page",
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
    mock_json.return_value = result
    mock_get_wiki_page.return_value = edited_page_data

    mock_bucket = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket

    backend = Backend(content_bucket="test-content-bucket")
    backend.author_edit_action("test-page", action)

    mock_client.assert_called_once()
    mock_get_wiki_page.assert_called_once_with("test-page")
    mock_bucket.blob.assert_called_once_with('uploaded-pages/test-page')
    mock_bucket.blob.return_value.upload_from_string(
        data=result, content_type="application/json")
    mock_json.assert_called_once_with(page_data)
