from flaskr.backend import Backend
import string
import random


def format_cardname(firstname, lastname):
    '''
        This method returns a formatted version of the cardname details entered by a user.

        Args:
            firstname: firstname is entered by the user.
            lastname: lastname is entered by the user.            
        
        Returns:
            A formatted string of the card name (format: firstname-lastname).
        '''
    cardname = (firstname.strip() + '-' + lastname.strip()).lower()
    return cardname


def create_card(Backend, firstname, lastname, contribution):
    '''
    This method stores the details of a new card created by a user.

    Args:
        Backend
        firstname: firstname is entered by the user.
        lastname: lastname is entered by the user.
        contribution: contribution is entered by the user.
    '''
    card_name = format_cardname(firstname, lastname)
    bucket = Backend.storage_client.bucket(Backend.content_bucket)
    cardblob = bucket.blob(Backend.card_prefix + card_name)

    with cardblob.open("w") as f:
        f.write(contribution)


def does_flashcard_exist(Backend, firstname, lastname):
    '''
    This method is used to check if a flashcard with a cardname already exists.
    If the flashcard exists, it returns True, otherwise, it returns False.

    Args:
        Backend
        firstname: Obtained from the form filled by the user.
        lastname: Obtained from the form filled by the user.
    
    Returns:
        A boolean indicating if the flashcard exists or not.
    '''
    card_name = format_cardname(firstname, lastname)
    flashcards = get_flashcards(Backend)

    if card_name in flashcards:
        return True

    return False


def get_alert_message(Backend, firstname, lastname):
    '''
    This method is used to get an appropriate alert message after a user attempts to create a card.

    Args:
        Backend
        firstname: Obtained from the form filled by the user.
        lastname: Obtained from the form filled by the user.
    
    Returns:
        A string containing a success or failure message for the card creation.
    '''

    if does_flashcard_exist(Backend, firstname, lastname):
        alert_message = "Ooops, there is a flashcard with this name."

    else:
        alert_message = "You have successfully created your flashcard! Create another card!"

    return alert_message


def get_flashcards(Backend):
    '''
    This method returns a set of all flashcards.

    Args:
        Backend
    
    Returns:
        A set containing all the card names stored in the flashcard folder.
    '''
    cards = set()
    bucket = Backend.storage_client.bucket(Backend.content_bucket)
    cardblobs = bucket.list_blobs(prefix=Backend.card_prefix)

    for flashcard in cardblobs:
        cards.add(flashcard.name.removeprefix(Backend.card_prefix))

    return cards


def get_card_name(Backend, letter):
    '''
    This method randomly returns a stored flashcard name for that begins with the letter that is passed in, if such a card exists.
    If there are no cards for that letter, a default message is returned.

    Args:
        Backend
        letter: This is passed in from the users click on the card
    
    Returns:
        The cardname for a flashcard as a string.
    '''
    no_card_name = "Oops! There is no flashcard for this letter yet."
    flashcards = get_flashcards(Backend)
    cards = []
    for name in flashcards:
        if name and letter.lower() == name[0]:
            cards.append(name)

    if not cards:
        return no_card_name

    random_index = random.randint(0, len(cards) - 1)
    name = cards[random_index]
    return name


def get_formatted_display_name(Backend, cardname):
    '''
    This method returns a formatted version of the inputted flashcard name for display.

    Args:
        Backend
        cardname: This is obtained by using the get_card_name function to receive a cardname that corresponds with the user's selected letter
    
    Returns:
        The display cardname for a flashcard as a string.
    '''

    if "Oops!" in cardname:
        return cardname
    formatted_name = cardname.replace('-', ' ')
    formatted_name = string.capwords(formatted_name, ' ')

    return formatted_name


def get_card_display_info(Backend, cardname):
    '''
    This returns the stored information to be displayed on the flashcard.

    Args:
        Backend
        cardname: This is obtained by formating the user's input of first and last name, using the format_cardname method.

    Returns:
        The matching display information for a flashcard as a string.
    '''
    default_info = "..."
    if "Oops!" in cardname:
        return default_info

    bucket = Backend.storage_client.bucket(Backend.content_bucket)
    cardblob = bucket.blob(Backend.card_prefix + cardname)

    with cardblob.open("r") as f:
        card_display_info = (f.read())
        return card_display_info