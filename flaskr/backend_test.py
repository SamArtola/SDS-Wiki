from flaskr.backend import Backend
import unittest, os, io
from unittest.mock import patch,Mock,MagicMock
from google.cloud import storage

# TODO(Project 1): Write tests for Backend methods.
# Sam: Get wiki page, all page names, upload, get image (if time, not being used in general)

@patch.object(storage,'Client')
def test_get_wiki_page(mock_storage_client):
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

@patch.object(storage,'Client')
def test_get_all_page_names(mock_storage_client):
    #Mock GCS
    mock_storage_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_storage_client.return_value = mock_storage_client_instance
    mock_storage_client_instance.bucket.return_value=mock_bucket

    #creating Mocks to call upon
    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()
    mock_blob1.name="uploaded-pages/page1"
    mock_blob2.name="uploaded-pages/page2"

    mock_bucket.list_blobs.return_value = [mock_blob1,mock_blob2]

    backend = Backend()
    page_list = backend.get_all_page_names()
    
    #asserting
    mock_storage_client.assert_called_once_with()
    mock_storage_client_instance.bucket.assert_called_once_with(backend.content_bucket)
    mock_bucket.list_blobs.assert_called_once_with(prefix='uploaded-pages/')
    assert "page1" in page_list
    assert "page2" in page_list
    #assert page_list == ["page1","page2"]      #get all page names uses a set() so test fails sometimes

           


@patch.object(storage,'Client')
@patch("flaskr.backend.Backend.upload_file", return_value = None)
def test_upload_file(mock_upload_file,mock_storage_client):
    #Mock GCS
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    #file mock
    file = MagicMock()
    file.filename = "test_file.txt"

    #backend mock
    db=Backend()
    db.upload_file(file)

    #asserting
    mock_storage_client.assert_called_once_with()
    mock_storage_client.return_value.bucket.assert_called_once_with(db.storage_client)
    mock_bucket.blob.assert_called_once_with('uploaded-pages/test_file.txt')
    mock_blob.upload_from_filename.assert_called_once_with('test_file.txt')
    os.remove.assert_called_once_with('test_file.txt')
    