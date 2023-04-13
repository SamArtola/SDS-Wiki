from google.cloud import storage
import hashlib, os, logging
import json

DEFAULT_IMAGE_URL = "https://storage.cloud.google.com/wikis-content/DEFAULT%20IMG.png"
class Backend:
    '''
        Backend class connects our web application with our google cloud storage.

        The Backend class functions to retrieve the web application pages and images from the google cloud storage, 
        uploads files to the google cloud storage, authenticates a user who is trying to log in or sign up.

        Attributes:
        storage_client: Initializes the google cloud storage client
        user_bucket: GCS bucket that stores users passwords
        content_bucket: GCS bucket that stores the application contents
        bucket_prefix: Attribute variable that stores the name of user data folder which contains users' passwords
        site_secret: Site secret used in hashing users' passwords
    '''

    def __init__(self,
                 user_bucket="user-pw-bucket",
                 content_bucket="wikis-content"):
        ''' Initializes the instance of the backend class with the names of buckets entered.
        Args:
          user_bucket: This stands for the GCS bucket where we store users sensitive information such as passwords.
          content_bucket: This stands for the GCS bucket where we store the web application content.
    
        '''
        #>Ibby wrapping this is its own class would make this code + test code simpler to read
        self.storage_client = storage.Client()
        self.user_bucket = user_bucket
        self.content_bucket = content_bucket
        # Ibby> Constants should be defined on the file level to make sure that future developers don't change them
        self.bucket_prefix = "users-data/"
        self.site_secret = "siam"

    def get_wiki_page(self, name):
        bucket = self.storage_client.bucket(self.content_bucket)
        # Ibby> Move this bucket prefix into a file level constant
        blob = bucket.blob('uploaded-pages/' + name)
        
        # with blob.open("r") as f:
        #     return (f.read())
        page_data = json.loads(blob.download_as_string())
        return page_data

    def get_all_page_names(self):
        '''
        This method is used to list links to uploaded wiki content.
        '''
        nombre = []
        bucket = self.storage_client.bucket(self.content_bucket)
        pages = set(bucket.list_blobs(prefix='uploaded-pages/'))
        for page in pages:
            name = page.name.split("uploaded-pages/")[1]
            if name == '':
                continue
            else:
                nombre.append(page.name.split("uploaded-pages/")[1])
        return nombre

    def upload_file(self, page_name, username,  user_file, upload_date, image_url=DEFAULT_IMAGE_URL):
        '''
        This method uploads a users file into the wiki content bucket.
        '''
        user_file.save(user_file.filename)
        content = open(user_file.filename, "r")        

        page_info = {
            "Name": page_name,
            "Author": username,
            "Content": content.read(),
            "Image": image_url,
            "Date": upload_date,
            "Edits": []
        }
        content.close()
        page_json = json.dumps(page_info)
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob('uploaded-pages/' + page_name)
        
        blob.upload_from_string(data=page_json, content_type="application/json")
        
        os.remove(user_file.filename)


    def edit_page_data(self, page_name, content, edit_date, editor):
        bucket = self.storage_client.bucket(self.content_bucket)

        blob = bucket.get_blob('uploaded-pages/' + page_name)
        
        page_data = json.loads(blob.download_as_string())

        edit_data = {
            "Content": content,
            "Date": edit_date,
            "Status": 1,
            "Editor": editor            
        }
        
        page_data["Edits"].append(edit_data)
        blob.upload_from_string(data=json.dumps(page_data), content_type="application/json")

            
    def get_users(self):
        '''
        This method returns a list of all user blobs.
        '''
        users = set()
        bucket = self.storage_client.bucket(self.user_bucket)
        blobs = bucket.list_blobs(prefix=self.bucket_prefix)
        for blob in blobs:
            users.add(blob.name.removeprefix(self.bucket_prefix))

        return users

    def hash_pwd(self, username, password):
        '''
        This method takes in a username and password, and returns the hashed password.
        '''
        # Ibby> Consider lowering before passing to the backend in all cases
        user_name = username.lower()
        with_salt = f"{user_name}{self.site_secret}{password}"
        hashed_pwd = hashlib.blake2b(with_salt.encode()).hexdigest()

        return hashed_pwd

    # Ibby> is_username_unique is a better function
    def check_user(self, username):
        '''
        This method is used to check if a username is valid.
        If an account exists with the user name, it returns True, otherwise, it returns False.
        '''
        user_list = self.get_users()

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
        new_user = bucket.blob(self.bucket_prefix + user_name)
        hashed_pwd = self.hash_pwd(user_name, password)

        with new_user.open("w") as f:
            f.write(hashed_pwd)

    def sign_in(self, username, password):
        '''
          Sign_in method performs user login authentication.

          Searches the google cloud storage user bucket for a blob whose name matches the username entered by the user,
          if it exists, it hashes the password passed in by the user and checks if that hashed password matches
          the one saved in that blob.

          Args:
            username: username passed in by the user
            password: password passed in by the user

          Returns:
            A boolean indicating if the sign in was successful and an error message if the sign in was not successful. 
        '''
        bucket = self.storage_client.bucket(self.user_bucket)
        blob_obj = bucket.get_blob(f"{self.bucket_prefix}{username}")
        if blob_obj:
            hashed_password = self.hash_pwd(username, password)
            content = blob_obj.download_as_text()
            if content == hashed_password:
                return True, None
            return False, "Wrong password"
        return False, "User not found"

    #Fix up to actually retrieve from bucket
    #>Ibby this should be named `get_all_images` to be clear it returns many
    def get_image(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.content_bucket)
        # Ibby> typo (sp)
        picture_lst = list(bucket.list_blobs(prefix='About-content/'))
        for blob in picture_lst:
            pic = bucket.get_blob(blob.name)
            #Ibby> remove prints
            print(pic)
        return picture_lst

    def get_all_uploaded_pages(self):
        bucket = self.storage_client.bucket(self.content_bucket)
        blobs = list(bucket.list_blobs(prefix = "uploaded-pages/"))
        uploaded_pages = []
        for blob in blobs[1:]:
            uploaded_pages.append(json.loads(blob.download_as_string()))
        return uploaded_pages
        
    def get_user_edits(self, username):
       
        uploaded_pages = self.get_all_uploaded_pages()
        user_edits = []

        for page in uploaded_pages:
            page["Edits"].reverse()
            for edit in page["Edits"]:
                if edit["Editor"].lower() == username.lower():                      
                    user_edit = {
                        "Name": page["Name"],
                        "Author": page["Author"],
                        "Status": edit["Status"],
                        "Edit": edit["Content"],
                        "Date": edit["Date"]
                    }
                    print("1", user_edit["Edit"])
                    user_edits.append(user_edit)

        return user_edits
    
    def get_user_pages_edits(self, username):
        uploaded_pages = self.get_all_uploaded_pages()
        user_pages = []
        for page in uploaded_pages:
            if page["Author"].lower() == username.lower():
                if len(page["Edits"]) > 0:
                    user_pages.append(page)
        

        user_pages.sort(key=lambda page: page["Edits"][-1]["Status"])

        return user_pages



    def author_edit_action(self, page_name, action):
        page_data =  self.get_wiki_page(page_name)

        if action == "Accept":
            page_data["Content"] = page_data['Edits'][-1]['Content']
            page_data['Edits'][-1]['Status'] =  2
        else:
            page_data['Edits'][-1]['Status'] =  3

        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob('uploaded-pages/' + page_name)
        blob.upload_from_string(data=json.dumps(page_data), content_type="application/json")            
