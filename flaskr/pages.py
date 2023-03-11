from flask import render_template, request, session
from flaskr.backend import Backend

 #> Ibby: Please add method-level comments for all public methods
def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        #> Ibby: You can remove TODO comments that are completed
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
    #> Ibby: Write tests for all routes
    @app.route('/upload')
    def upload():
        return render_template('/upload.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/signup', methods =['GET', 'POST'])
    def signup():
        #> Ibby: Have you considered creating the backed once, in the constructor (__init__) instead of everytime this is called? It could be used in `login` as well
        back_end = Backend()
        display_text = ''
        
    #> Ibby: This code will be easier to understand at a glance if its split into two. `signup_get` for 'GET' and `signup_post` for 'POST'
        if request.method == 'POST':
            username = request.form['name']
            password = request.form['pwd']
            
            if back_end.check_user(username):
                display_text = "Ooops, that username is taken."

            else:
                session['username'] = username
                back_end.sign_up(username, password)
                display_text = "Successfully registered!"
                return render_template('main.html', signed_in =True, username = username)

        return render_template('/signup.html', display_text=display_text)

    @app.route('/pages')
    def page_index():
        return render_template('/page_index.html')

     #> Ibby: Same comment as above re: splitting into login_get and login_post
    @app.route('/login', methods = ['GET', 'POST'])
    def login():
        backend = Backend()

        if request.method == "POST":
            username = request.form.get("name").lower()
            password = request.form.get("password")

            signed_in, err = backend.sign_in(username, password)

        else:
            signed_in, err = False, False

        if signed_in:
            session['username'] = username
            return render_template('main.html')
        return render_template('login.html', signed_in = signed_in, err_message = err)
    
    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return render_template('login.html')
