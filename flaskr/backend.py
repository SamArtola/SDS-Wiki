from google.cloud import storage
import hashlib, os
import string


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

    def get_wiki_page(self, name):
        bucket = self.storage_client.bucket(self.content_bucket)
        # Ibby> Move this bucket prefix into a file level constant
        blob = bucket.blob('uploaded-pages/' + name)
        with blob.open("r") as f:
            return (f.read())

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

    def upload_file(self, file):
        '''
        This method uploads a users file into the wiki content bucket.
        '''
        bucket = self.storage_client.bucket(self.content_bucket)
        new_file = bucket.blob('uploaded-pages/' + file.filename)
        file.save(file.filename)
        new_file.upload_from_filename(file.filename)
        os.remove(file.filename)

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

    def is_username_unique(self, username):
        '''
        This method is used to check if a username is valid.
        If an account exists with the user name, it returns False, otherwise, it returns True.
        '''
        user_name = username.lower()
        user_list = self.get_users()

        if user_name in user_list:
            return  False

        return True

    def sign_up(self, username, password):
        '''
        This method takes in a username and password and stores the username(in lowercase)
        as an object in the users-data folder in the user_bucket.
        This object contains the hashed password
        '''
        user_name = (username.strip()).lower()
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

    def format_cardname(self, firstname, lastname):
        '''
        This method returns a formatted version of the cardname details entered by a user.

        Args:
            self
            firstname: firstname is entered by the user.
            lastname: lastname is entered by the user.            
        
        Returns:
            A formatted string of the card name (format: firstname-lastname).
        '''
        self.cardname = (firstname.strip()+'-'+lastname.strip()).lower()
        return self.cardname
    

    def create_card(self, card_name, contribution):
        '''
        This method stores the details of a new card created by a user.

        Args:
            self
            card_name: card_name is entered by the user.
            contribution: contribution is entered by the user.
        '''
        bucket = self.storage_client.bucket(self.content_bucket)
        cardblob = bucket.blob(self.card_prefix + card_name)

        with cardblob.open("w") as f:
            f.write(contribution)

    def does_flashcard_exist(self, cardname):
        '''
        This method is used to check if a flashcard with a cardname already exists.
        If the flashcard exists, it returns True, otherwise, it returns False.

        Args:
            self
            cardname: Obtained from the form filled by the user.
        
        Returns:
            A boolean indicating if the flashcard exists or not.
        '''
        card_name = self.cardname
        flashcards = self.get_flashcards()

        if card_name in flashcards:
            return True

        return False

    def get_alert_message(self):
        '''
        This method is used to get an appropriate alert message after a user attempts to create a card.

        Args:
            self
        
        Returns:
            A string containing a success or failure message for the card creation.
        '''
        
        if self.does_flashcard_exist(self.cardname()):
            alert_message = "Ooops, there is a flashcard with this name."

        else:
            alert_message = "You have successfully created your flashcard! Create another card!"

        return alert_message

    def get_flashcards(self):
        '''
        This method returns a set of all flashcards.

        Args:
            self
        
        Returns:
            A set containing all the card names stored in the flashcard folder.
        '''
        cards = set()
        bucket = self.storage_client.bucket(self.content_bucket)
        cardblobs = bucket.list_blobs(prefix = self.card_prefix)

        for flashcard in cardblobs:
            cards.add(flashcard.name.removeprefix(self.card_prefix))

        return cards  

    def get_card_name(self, letter):
        '''
        This method returns the stored flashcard name for a letter for display, if a card exists.
        If there are no cards for that letter, a default message is returned.

        Args:
            self
            letter: This is passed in from the users click on the card
        
        Returns:
            The display cardname for a flashcard as a string.
        '''
        self.no_card_name = "Oops! There is no flashcard for this letter yet."
        flashcards = self.get_flashcards()
        for name in flashcards:
            if name and letter.lower() == name[0]:
                return name

        return self.no_card_name

    def get_formatted_display_name(self,letter):
        '''
        This method returns a formatted version of flashcard names for display.

        Args:
            self
            letter: This is passed in from the users click on the card
        
        Returns:
            The display cardname for a flashcard as a string.
        '''
        self.cardname = self.get_card_name(letter)

        if self.cardname == self.no_card_name:
            return self.cardname
        formatted_name = self.cardname.replace('-', ' ')
        formatted_name = string.capwords(formatted_name, ' ')

        return formatted_name

    def get_card_display_info(self):
        '''
        This returns the stored information to be displayed on the flashcard.

        Args:
            self

        Returns:
            The display information for a flashcard as a string.
        '''
        cardname = self.cardname
        default_info = "..."
        if cardname == self.no_card_name:
            return default_info
                
        bucket = self.storage_client.bucket(self.content_bucket)
        cardblob = bucket.blob(self.card_prefix + cardname)

        with cardblob.open("r") as f:
            card_display_info = (f.read())        
            return card_display_info
