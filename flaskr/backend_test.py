from flaskr.backend import Backend
import pytest, hashlib
from unittest.mock import patch, mock_open, MagicMock, Mock

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

 