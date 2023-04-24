from google.cloud import storage
import hashlib, os, logging
import json
from werkzeug.utils import secure_filename

DEFAULT_IMAGE_URL = "https://storage.cloud.google.com/wikis-content/DEFAULT%20IMG.png"
SITE_SECRET = "siam"

# Content bucket folders
USER_PASSWORD_FOLDER = "users-data/"
UPLOADED_PAGES_FOLDER = "uploaded-pages/"

# Uploaded page access keys
PAGE_EDITS = "Edits"
PAGE_NAME = "Name"
PAGE_CONTENT = "Content"
EDIT_CONTENT = "Content"
PAGE_AUTHOR = "Author"
DATE = "Date"
EDIT_STATUS = "Status"
EDIT_AUTHOR = "Editor"
EN_ES_BUCKET_ADDRESS = 'translations/en-es.json'

# Page edit status keys
PENDING = 1
ACCEPTED = 2
DECLINED = 3


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
        self.card_prefix = "flashcards/"
        self.site_secret = "siam"

    def get_content_bucket(self):
        return self.storage_client.bucket(self.content_bucket)

    def get_content_blob(self, filename):
        return self.get_content_bucket().blob(filename)

    def add_translations(self,
                         word1,
                         word2,
                         translation_bucket=EN_ES_BUCKET_ADDRESS):
        jsonblob = self.get_content_blob(translation_bucket)

        with jsonblob.open("r") as json_file:
            data = json.load(json_file)

        with jsonblob.open("w") as json_file:
            if word1 not in data:
                data[word1] = word2

            json.dump(data, json_file)

    def translate_page(self,
                       content,
                       lang,
                       translation_bucket=EN_ES_BUCKET_ADDRESS):
        if lang == "EN":
            return content
        lines = []
        file_content = content.split()

        #OPEN/LOAD JSON DATA WITH EN-ES TRANSLATIONS
        jsonblob = self.get_content_blob(translation_bucket)

        with jsonblob.open("r") as json_file:
            data = json.load(json_file)
            for word in file_content:
                if word in data:
                    word = data[word]
                lines.append(word)

            return " ".join(lines)

    def get_wiki_page(self, name, lang):
        '''
            This method returns the data of a uploaded page. 

        '''
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob(UPLOADED_PAGES_FOLDER + name)
        page_data = json.loads(blob.download_as_text())
        page_data["Content"] = self.translate_page(page_data["Content"], lang)
        return page_data

    def get_all_page_names(self):
        '''
        This method is used to list links to uploaded wiki content.
        '''
        nombre = []
        pages = set(
            self.get_content_bucket().list_blobs(prefix=UPLOADED_PAGES_FOLDER))
        for page in pages:
            name = page.name.split(UPLOADED_PAGES_FOLDER)[1]
            if name == '':
                continue
            nombre.append(name)
        return nombre

    def upload_file(self,
                    page_name,
                    username,
                    user_file,
                    upload_date,
                    image_url=DEFAULT_IMAGE_URL):
        '''
            Upload_file method allows users to upload a wiki page.

            It accepts a page name, display image link and a file which holds the page content from the user
            and uploads it to the uploaded-pages folder in our content bucket.

            Args:
                page_name: name for the page to be created from the user's content.
                username:  username of the user.
                user_file: a .txt extension file that contains the content to be displayed on the page.
                upload_datee: date of the upload
                image_url: display image url for the page. This would be set to a default image if the user did not upload one.

            
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
        blob = self.get_content_bucket().blob(UPLOADED_PAGES_FOLDER + page_name)

        blob.upload_from_string(data=page_json, content_type="application/json")

        os.remove(user_file.filename)

    def edit_page_data(self, page_name, content, edit_date, editor):
        bucket = self.storage_client.bucket(self.content_bucket)

        blob = bucket.get_blob(UPLOADED_PAGES_FOLDER + page_name)

        page_data = json.loads(blob.download_as_text())

        edit_data = {
            "Content": content,
            "Date": edit_date,
            "Status": 1,
            "Editor": editor
        }

        page_data["Edits"].append(edit_data)
        blob.upload_from_string(data=json.dumps(page_data),
                                content_type="application/json")

    def get_users(self):
        '''
        This method returns a list of all user blobs.
        '''
        users = set()
        bucket = self.storage_client.bucket(self.user_bucket)
        blobs = bucket.list_blobs(prefix=USER_PASSWORD_FOLDER)
        for blob in blobs:
            users.add(blob.name.removeprefix(USER_PASSWORD_FOLDER))

        return users

    def hash_pwd(self, username, password):
        '''
        This method takes in a username and password, and returns the hashed password.
        '''
        # Ibby> Consider lowering before passing to the backend in all cases
        user_name = username.lower()
        with_salt = f"{user_name}{SITE_SECRET}{password}"
        hashed_pwd = hashlib.blake2b(with_salt.encode()).hexdigest()

        return hashed_pwd

    def is_username_unique(self, username):
        '''
        This method is used to check if a username is valid.
        If an account exists with the user name, it returns False, otherwise, it returns True.
        '''
        user_name = username.lower()
        user_list = self.get_users()

        if user_name in user_list:
            return False

        return True

    def sign_up(self, username, password):
        '''
        This method takes in a username and password and stores the username(in lowercase)
        as an object in the users-data folder in the user_bucket.
        This object contains the hashed password
        '''
        user_name = (username.strip()).lower()
        bucket = self.storage_client.bucket(self.user_bucket)
        new_user = bucket.blob(USER_PASSWORD_FOLDER + user_name)
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
        blob_obj = bucket.get_blob(f"{USER_PASSWORD_FOLDER}{username}")
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
        return picture_lst

    def get_all_uploaded_pages(self):
        '''
            Get_all_uploaded_pages method gets all the pages that have been uploaded
            in our wiki.

            Returns:
                A list of json objects which hold the data of all uploaded pages.
                They contain the name, author, date uploaded,page's content, author's username 
                and a list of dictionaries which contain the information of all edits made to the page.

        '''

        blobs = list(
            self.storage_client.list_blobs(self.content_bucket,
                                           prefix=UPLOADED_PAGES_FOLDER))
        uploaded_pages = []
        for blob in blobs[1:]:
            uploaded_pages.append(json.loads(blob.download_as_text()))
        return uploaded_pages

    def get_user_edits(self, username):
        '''
            Get_user_edits function gets all the edits a user has suggested in any of the uploaded
            wiki pages.

            Args:
                username: This is the username of the user

            Returns:
                A list of dictionaries containing the name of the page the user made an edit on,
                the page author's name, the status of the user edit, the edited content
                suggested by the user, and the date of the edit.
        '''

        uploaded_pages = self.get_all_uploaded_pages()
        user_edits = []

        for page in uploaded_pages:
            page[PAGE_EDITS].reverse()
            for edit in page[PAGE_EDITS]:
                if edit[EDIT_AUTHOR].lower() == username.lower():
                    user_edit = {
                        "Name": page[PAGE_NAME],
                        "Author": page[PAGE_AUTHOR],
                        "Status": edit[EDIT_STATUS],
                        "Edit": edit[EDIT_CONTENT],
                        "Date": edit[DATE]
                    }
                    user_edits.append(user_edit)

        return user_edits

    def get_user_pages_edits(self, username):
        '''
            Get_user_pages_edits function gets all the edits made on all of the pages a user has uploaded 
            (authored) to the wiki. 

            Args:
                username: username of the user.

            Returns:
                A list of json objects which contain the name of the page, author's name (user), 
                page content, date of upload, the page's display image url, and a list of dictionaries
                which contain all edits ever made on the page. The dictionaries comprises
                of the editor's name, the date of the edit, the status of the edit and the edited content.
        '''
        uploaded_pages = self.get_all_uploaded_pages()
        user_pages = []
        for page in uploaded_pages:
            if page[PAGE_AUTHOR].lower() == username.lower():
                if len(page[PAGE_EDITS]) > 0:
                    user_pages.append(page)

        return user_pages

    def author_edit_action(self, page_name, action):
        '''
            Author_edit_action fucntion updates the a page's json object according to the 
            action the author of a page decides on an edit made on the page. 

            The author can choose to accept or decline an edit. The author_edit_action
            sets the status of the edit to the author's decision.

            Args:
                page_name: name of the page.
                action: the actor's decision on the edit.               
        '''
        page_data = self.get_wiki_page(page_name)

        if action == "Accept":
            page_data[PAGE_CONTENT] = page_data[PAGE_EDITS][-1][EDIT_CONTENT]
            page_data[PAGE_EDITS][-1][EDIT_STATUS] = ACCEPTED
        else:
            page_data[PAGE_EDITS][-1][EDIT_STATUS] = DECLINED

        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob(UPLOADED_PAGES_FOLDER + page_name)
        blob.upload_from_string(data=json.dumps(page_data),
                                content_type="application/json")
