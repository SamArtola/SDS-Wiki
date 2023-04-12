from flask import render_template, request, session, redirect, url_for
from flaskr.backend import Backend


#> Ibby: Please add method-level comments for all public methods
def make_endpoints(app):
    back_end = Backend()
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        '''
            Home function renders the main.html to the index route "/" when the Flask API call is a GET method.

            Returns:
                A template rendered from the main.html file to the assigned '/' route.
        '''
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        #Ibby> Consider splitting into separate methods for get and post
        if request.method == "POST":
            backend = Backend()
            file = request.files['file']
            backend.upload_file(file)
            #>Ibby consider passing in the page header name instead of defining it in the template.
        return render_template('/upload.html')

    @app.route('/about')
    def about():
        #>Ibby Use the backend already in the class
        back = Backend()
        pics = back.get_image()
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
            session['username'] = username
            back_end.sign_up(username, password)
            display_text = "Successfully registered!"
            return render_template('main.html',
                                   signed_in=True,
                                   username=username)

        return render_template('/signup.html', display_text=display_text)

    @app.route('/pages')
    def page_index():
        backend = Backend()
        page_list = backend.get_all_page_names()
        return render_template('/page_index.html', page_list=page_list)

    @app.route('/pages/<curpage>')
    def show_wiki(curpage):
        backend = Backend()
        page = curpage
        content = backend.get_wiki_page(page)
        return render_template('/pages.html', contents=content, pagename=page)

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
            session['username'] = username
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

    @app.route('/fun')
    def fun():
        card_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']        
        return render_template('/fun.html', card_list=card_list)

    @app.route('/createcard', methods=['GET'])
    def createcard_get():
        return render_template('/createcard.html')
        

    @app.route('/createcard', methods=['POST'])
    def createcard_post():

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        card_content = request.form['contribution']

        card_name = back_end.format_cardname(firstname, lastname)

        if back_end.does_flashcard_exist(card_name):
            display_text = back_end.get_alert_message(card_name)

        else:
            display_text = back_end.get_alert_message(card_name)
            back_end.create_card(card_name, card_content)
            return render_template('/createcard.html', display_text=display_text)
        
        return render_template('/createcard.html', display_text=display_text)