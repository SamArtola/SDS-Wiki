from flask import render_template, request, session, redirect, url_for
from flaskr.backend import Backend
from flaskr.flashcard import *
from functools import wraps
from flaskr.custom_filters import get_status_color, get_status_name
from datetime import date
import time

PAGE_EDITS = "Edits"
EDIT_STATUS = "Status"
PENDING = 1


def is_logged_in(function):
    ''' 
            Is_logged_in is a decorator that ensures that users cannot access routes such as 
            upload and edits which require user authentication without being logged in. 

            Args:
                function: the function to be wrapped by the decorator

            Returns:
                Redirects to the login page if user is not logged in, else
                returns the function.
        '''

    @wraps(function)
    def wrapped_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login_get"))
        return function(*args, **kwargs)

    return wrapped_function


#> Ibby: Please add method-level comments for all public methods
def make_endpoints(app):
    '''
        Make_endpoints 
    '''
    back_end = Backend()

    #Custom template filters to assign the appropriate color and name to a specific status.
    app.add_template_filter(get_status_color)
    app.add_template_filter(get_status_name)

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.

    def initialize_sessions(username):
        '''
            Initialize_sessions function set the session parameters in our code to the their
            appropriate values whenever a user logs or signs in.

            Args:
                username: This is the username entered by tht user.            
        '''
        session["username"] = username
        session["show_user_edits"] = True

    @app.route("/")
    def home():
        '''
            Home function renders the main.html to the index route "/" when the Flask API call is a GET method.

            Returns:
                A template rendered from the main.html file to the assigned '/' route.
        '''
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route('/upload', methods=['GET'])
    @is_logged_in
    def upload_get():
        return render_template('/upload.html')

    @app.route('/upload', methods=['POST'])
    @is_logged_in
    def upload_post():
        #Ibby> Consider splitting into separate methods for get and post

        backend = Backend()
        page_name = request.form["page_name"]
        image_url = request.form["image_url"]
        user_file = request.files['file']
        username = session['username'].lower()
        upload_date = date.today().strftime("%m/%d/%Y")

        if image_url:
            backend.upload_file(page_name, username, user_file, upload_date,
                                image_url)
        else:
            backend.upload_file(page_name, username, user_file, upload_date)
            #>Ibby consider passing in the page header name instead of defining it in the template.
        return render_template('/upload.html')

    @app.route('/about')
    def about():
        pics = back_end.get_image()
        return render_template('about.html', pics=pics)

    @app.route('/signup', methods=['GET'])
    def signup_get():

        return render_template('/signup.html')

    @app.route('/signup', methods=['POST'])
    def signup_post():
        display_text = ''

        username = request.form['name']
        password = request.form['pwd']

        if not username or not password:
            display_text = "Please fill all required fields"

        elif not back_end.is_username_unique(username):
            display_text = "Ooops, that username is taken."

        else:
            initialize_sessions(username)
            back_end.sign_up(username, password)
            display_text = "Successfully registered!"
            return render_template('main.html',
                                   signed_in=True,
                                   username=username)

        return render_template('/signup.html', display_text=display_text)

    @app.route('/pages', methods=['GET', 'PUT'])
    def page_index():
        page_list = back_end.get_all_page_names()
        return render_template('/page_index.html', page_list=page_list)

    @app.route('/pages/<curpage>', methods=['GET', 'PUT'])
    def show_wiki(curpage):
        '''
            Show_wiki function displays the content of an uploaded page. 

            The show_wiki function would display the content of an uploaded page,
            along with the date it was uploaded, the author/uploaders name, page name, 
            and the page's display image if one was uploaded. If not, the defaut display image would
            be shown. The show_wiki function would also enable the user to make an edit on the current page if
            the page being displayed doesn't already havea pending edit, i.e an edit that the 
            author of the page hasn't reviewed, the edit button would be disabled. 
            This is so that a page can only have a single pending edit.

            Args:
                curpage: the name of the page.

            Returns:
                A template rendered from pages.html file with the page's data.     
        '''
        backend = Backend()
        page = curpage
        page_data = backend.get_wiki_page(page, "EN")

        if page_data[PAGE_EDITS] and page_data[PAGE_EDITS][-1][
                EDIT_STATUS] == PENDING:
            edit_button = False
        else:
            edit_button = True

        return render_template('/pages.html',
                               content=page_data["Content"],
                               author=page_data["Author"],
                               image=page_data["Image"],
                               date=page_data["Date"],
                               pagename=page,
                               edit_button=edit_button)

    @app.route('/quotes')
    def quotes():
        return render_template('/quotes.html')

    @app.route('/kathjohn')
    def kathjohn():
        return render_template('/kathjohn.html')

    @app.route('/login')
    def login_get():
        """
            Login_get function renders the login.html to the assigned "/login" when the Flask API call is a GET method.

            Returns:
                A template rendered from the login.html file to the assigned "/login" route.
        """

        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login_post():
        """
            Login_post function authenticates a user and renders an html file to the assigned route when the Flask API call is a POST method.

            Login_post retrieves the username and password of a user submitted in the html form rendered on the "/login" route,
            authenticates the user by calling the sign_in fucntion from the Backend class, and returns a specific html template and passes a
            variable to the assigned route depending on if the user is successful or not.

            Returns:
                If the user successfully logs in, redirects the user to the home page, route "/"
                If the user is unsucessful, renders the template for the login.html to the "/login" route and passes the error message
                to that route.
        """
        username = request.form.get("name").lower()
        password = request.form.get("password")

        signed_in, err = back_end.sign_in(username, password)

        if signed_in:
            initialize_sessions(username)
            return redirect(url_for('home'))
        return render_template('login.html', err_message=err)

    @app.route('/logout')
    def logout():
        """
            Logout function pops the username from the flask session and redirects the user 
            to the login page when the Flask API call is a GET method.

            Returns:
                
        """
        session.pop('username', None)
        return redirect(url_for('login_get'))

    @app.route('/pages/scholarships')
    def scholarships_page():
        '''
            Scholarships_page function renders the scholarships.html to the '/pages/scholarships' route 
            when the Flask API call is a GET method.

            Returns:
                A template rendered from the scholarships.html file to the assigned '/pages/scholarship' route.
        '''
        return render_template('/scholarships.html')

    @app.route('/pages/opportunities')
    def opportunities_page():
        '''
            Opportunities_page function renders the opportunities.html to the '/pages/opportunities' route 
            when the Flask API call is a GET method.

            Returns:
                A template rendered from the opportunities.html file to the assigned '/pages/opportunities' route.
        '''
        return render_template('/opportunities.html')

    @app.route('/pages/joy_buolamwini')
    def joy_buolamwini_page():
        '''
            Joy_buolamwini_page function renders the joy_buolamwini.html to the '/pages/joy_buolamwini' route
            when the Flask API call is a GET method.

            Returns:
                A template rendered from the joy_buolamwini.html file to the assigned '/pages/joy_buolamwini' route.
        '''
        return render_template('/joy_buolamwini.html')

    @app.route('/fun', methods=['GET'])
    def fun_get():
        card_list = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        return render_template('/fun.html',
                               card_list=card_list,
                               show_modal="none")

    @app.route('/fun', methods=['POST'])
    def fun_post():
        card_list = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        current_card = request.form['current']
        show_modal = request.form['showModal']

        card_name = get_card_name(back_end, current_card)
        matching_card = get_formatted_display_name(back_end, card_name)
        matching_info = get_card_display_info(back_end, card_name)

        return render_template('/fun.html',
                               card_list=card_list,
                               matching_card=matching_card,
                               matching_info=matching_info,
                               show_modal=show_modal)

    @app.route('/createcard', methods=['GET'])
    def createcard_get():
        return render_template('/createcard.html')

    @app.route('/createcard', methods=['POST'])
    def createcard_post():

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        card_content = request.form['contribution']

        if does_flashcard_exist(back_end, firstname, lastname):
            display_text = get_alert_message(back_end, firstname, lastname)

        else:
            display_text = get_alert_message(back_end, firstname, lastname)
            create_card(back_end, firstname, lastname, card_content)
            return render_template('/createcard.html',
                                   display_text=display_text)

        return render_template('/createcard.html', display_text=display_text)

    @app.route('/edit-form', methods=['POST'])
    @is_logged_in
    def edit_form():

        page_name = request.form["page-name"]
        editor = request.form["editor"].lower()
        content = request.form["content"]
        edit_date = date.today().strftime("%m/%d/%Y")

        back_end.edit_page_data(page_name, content, edit_date, editor)

        page_url = f"/pages/{page_name}"

        return redirect(page_url)

    @app.route('/edit-page', methods=['GET', 'PUT'])
    @is_logged_in
    def edit_page():
        username = session['username']

        user_edits = back_end.get_user_edits(username)
        user_page_edits = back_end.get_user_pages_edits(username)

        return render_template('/edit.html',
                               user_edits_list=user_edits,
                               page_edits=user_page_edits)

    @app.route('/translation')
    @is_logged_in
    def upload_translation():
        return render_template("translation.html")

    @app.route('/show-user-edits')
    @is_logged_in
    def show_user_edits():

        session["show_user_edits"] = True
        return redirect("/edit-page")

    @app.route('/show-page-edits')
    @is_logged_in
    def show_page_edits():

        session["show_user_edits"] = False
        return redirect("/edit-page")

    @app.route('/update-edit', methods=['POST'])
    @is_logged_in
    def update_edit():

        page_name = request.form['edit-page-name']
        edit_action = request.form['edit-action']

        back_end.author_edit_action(page_name, edit_action)

        return redirect("/edit-page")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
