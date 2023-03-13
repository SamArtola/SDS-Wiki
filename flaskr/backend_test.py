import pytest
from flaskr.backend import Backend
import pytest, hashlib
from unittest.mock import patch, MagicMock, Mock
from google.cloud import storage

'''
 def get_wiki_page(self, name):
        bucket=self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob('uploaded-pages/'+name)
        with blob.open("r") as f:
            return (f.read())
'''
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
    mock_bucket.get_blob.return_value= None
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

@patch.object(storage,'Client')
def test_get_wiki_page(mock_storage_client):
    #mock_storage_client = MagicMock(spec=storage.Client)
    mock_storage_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    
    mock_storage_client.return_value=mock_storage_client_instance
    mock_storage_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value=mock_blob
    mock_blob.open.return_value.__enter__.return_value.read.return_value="testing page reader"

    backend = Backend()
    page_content = backend.get_wiki_page("test-page")

    mock_storage_client.assert_called_once_with()
    mock_storage_client_instance.bucket.assert_called_once_with(backend.content_bucket)
    mock_bucket.blob.assert_called_once_with("uploaded-pages/test-page")
    mock_blob.open.assert_called_once_with("r")

    assert page_content == "testing page reader"
