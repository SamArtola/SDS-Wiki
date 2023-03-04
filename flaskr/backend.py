# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import logging

class Backend:
    #bucket_name = "wikis-content" 
    #bucket_name = "user-pw-bucket"

    def __init__(self,user_bucket="user-pw-bucket",content_bucket="wikis-content"):
        self.user_bucket = user_bucket
        self.content_bucket = content_bucket
        
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        #Instantiates a client
        storage_client = storage.Client()
        pages = storage_client.list_blobs(self.content_bucket)
        pass

    def upload(self):
        pass

    def sign_up(self):
        storage_client=storage.Client()
        
        pass

    def sign_in(self, username, password):
        '''
          Returns if user was able to successfully sign in and 
          error message if they were not.  
        '''
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.user_bucket)
        blobs = bucket.list_blobs(prefix='users-data/')
        for blob in blobs:
            logging.info(blob.name)
            if blob.name == 'users-data/' + username:
                with blob.open("r") as content:
                    if content.read() == password:
                        return True, None
                    return False, "Wrong password"
        return False, "User not found"

    def get_image(self):
        pass

