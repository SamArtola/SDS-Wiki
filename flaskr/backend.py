# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib

class Backend:
    #bucket_name = "wikis-content" 
    #bucket_name = "user-pw-bucket"

    def __init__(self, user_bucket="user-pw-bucket", content_bucket="wikis-content"):
        self.user_bucket = user_bucket
        self.content_bucket = content_bucket
        self.site_secret = "siam"
        
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        #Instantiates a client
        storage_client = storage.Client()
        pages = storage_client.list_blobs(self.content_bucket)
        pass

    def upload(self):
        pass
    
    def check_user(self, username):
        '''
        This method is used to check if a username is valid.
        If an account exists with the user name, it returns True, otherwise, it returns False.
        '''
        user_list = set()
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.user_bucket)
        user_blobs = set(bucket.list_blobs(prefix='users-data/'))
        for blob in user_blobs:
            user_list.add(blob.name.strip('users-data/'))
        if username not in user_list:
            return False
        return True

    def sign_up(self, username, password):
        '''
        This method takes in a username and password and stores the username(in lowercase)
        as an object in the users-data folder in the user_bucket.
        This object contains the hashed password
        '''
        user_name = username.lower()
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.user_bucket)
        new_user = bucket.blob('users-data/'+ user_name)

        with_salt = f"{user_name}{self.site_secret}{password}"
        hashed_pwd = hashlib.blake2b(with_salt.encode()).hexdigest()

        with new_user.open("w") as f:
            f.write(hashed_pwd)
        

    def sign_in(self, username, password):
        '''
          Returns if user was able to successfully sign in and 
          error message if they were not.  
        '''
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.user_bucket)
        blobs = bucket.list_blobs(prefix='users-data/')

        with_salt = f"{username}{self.site_secret}{password}"
        hashed_password = hashlib.blake2b(with_salt.encode()).hexdigest()

        for blob in blobs:
            if blob.name == 'users-data/' + username:
                with blob.open("r") as content:
                    if content.read() == hashed_password:
                        return True, None
                    return False, "Wrong password"
        return False, "User not found"

    def get_image(self):
        pass

