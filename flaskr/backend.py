# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib,os


 #> Ibby: Please add tests

class Backend:
    #bucket_name = "wikis-content" 
    #bucket_name = "user-pw-bucket"
    def __init__(self, user_bucket="user-pw-bucket", content_bucket="wikis-content"):
        self.storage_client = storage.Client()
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
    
    def get_users(self):
        '''
        This method returns a list of all user blobs.
        '''
        bucket = self.storage_client.bucket(self.user_bucket)
        blobs = bucket.list_blobs(prefix='users-data/')

        return blobs

    def hash_pwd(self, username, password):
        '''
        This method takes in a username and password, and returns the hashed password.
        '''
        user_name = username.lower()
        with_salt = f"{user_name}{self.site_secret}{password}"
        hashed_pwd = hashlib.blake2b(with_salt.encode()).hexdigest()

        return hashed_pwd

    def check_user(self, username):
        '''
        This method is used to check if a username is valid.
        If an account exists with the user name, it returns True, otherwise, it returns False.
        '''
        user_list = set()
        user_blobs = set(self.get_users())
        for blob in user_blobs:
            user_list.add(blob.name.removeprefix('users-data/'))
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
        bucket = self.storage_client.bucket(self.user_bucket)
        new_user = bucket.blob('users-data/'+ user_name)
        hashed_pwd = self.hash_pwd(user_name,password)

        with new_user.open("w") as f:
            f.write(hashed_pwd)
        

    def sign_in(self, username, password):
        '''
          Returns if user was able to successfully sign in and a specific 
          error message if they were not.  
        '''
        # storage_client = storage.Client()
        # bucket = storage_client.bucket(self.user_bucket)
        # blobs = bucket.list_blobs(prefix='users-data/')
        blobs = self.get_users()

        hashed_password = self.hash_pwd(username,password)

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
            print(pic)
        return picture_lst

