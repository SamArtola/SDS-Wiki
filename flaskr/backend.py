# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
class Backend:
    #bucket_name = "wikis-content" 
    #bucket_name = "user-pw-bucket"

    def __init__(self,user_bucket,content_bucket):
        self.user_bucket = user_bucket
        self.content_bucket = content_bucket
        
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        #Instantiates a client
        storage_client = storage.Client()
        pages =storage_client.list_blobs(self.content_bucket)
        pass

    def upload(self):
        pass

    def sign_up(self):
        storage_client=storage.Client()
        
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass

