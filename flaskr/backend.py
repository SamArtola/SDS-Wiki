# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib,os


 #> Ibby: Please add tests

class Backend:
    #bucket_name = "wikis-content" 
    #bucket_name = "user-pw-bucket"
    def __init__(self, user_bucket="user-pw-bucket", content_bucket="wikis-content"):
         #> Ibby: Have you considered creating the Client here so that its created once instead of everytime a method is called?
        self.user_bucket = user_bucket
        self.content_bucket = content_bucket
        self.site_secret = "siam"
        
        
    def get_wiki_page(self, name):
        storage_client = storage.Client()
        bucket=storage_client.bucket(self.content_bucket)
        blob = bucket.blob('uploaded-pages/'+name)
        with blob.open("r") as f:
            return (f.read())

    def get_all_page_names(self):
        '''
        This method is used to list links to uploaded wiki content.
        '''
        storage_client = storage.Client()
        nombre = []
        bucket=storage_client.bucket(self.content_bucket)
        pages = set(bucket.list_blobs(prefix='uploaded-pages/'))
        for page in pages:
            nombre.append(page.name.split("uploaded-pages/")[1])
        return nombre

    def upload_file(self, file):
        '''
        This method uploads a users file into the wiki content bucket.
        '''
        storage_client = storage.Client()
        bucket=storage_client.bucket(self.content_bucket)
        new_file=bucket.blob('uploaded-pages/'+file.filename)
        file.save(file.filename)
        new_file.upload_from_filename(file.filename)
        os.remove(file.filename)
    
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
         #> Ibby: This code is also used below (line 70) have you considered using a helper method?
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.user_bucket)
        new_user = bucket.blob('users-data/'+ user_name)

        #> Ibby: This code is also used below (line 73) have you considered creating a helper method for this?
        with_salt = f"{user_name}{self.site_secret}{password}"
        hashed_pwd = hashlib.blake2b(with_salt.encode()).hexdigest()

        with new_user.open("w") as f:
            f.write(hashed_pwd)
        

    def sign_in(self, username, password):
        '''
          Returns if user was able to successfully sign in and a specific 
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
        storage_client = storage.Client()
        bucket=storage_client.bucket(self.content_bucket)
        picture_lst = list(bucket.list_blobs(prefix='About-content/'))
        for blob in picture_lst:
            pic=bucket.get_blob(blob.name)

        return picture_lst

