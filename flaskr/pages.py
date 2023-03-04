from flask import render_template, request
from flaskr.backend import Backend


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route('/upload')
    def upload():
        return render_template('/upload.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/signup', methods =['GET', 'POST'])
    def signup():
        back_end = Backend()
        display_text = ''
        
        if request.method == 'POST':
            username = request.form['name']
            password = request.form['pwd']
            
            if back_end.check_user(username):
                display_text = "Ooops, that username is taken."

            else:
                back_end.sign_up(username, password)
                display_text = "Successfully registered!"

        return render_template('/signup.html', display_text=display_text)

    @app.route('/pages')
    def page_index():
        return render_template('/page_index.html')

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
            return render_template('main.html', signed_in =True, username = username)
        return render_template('login.html', signed_in = signed_in, err_message = err)
