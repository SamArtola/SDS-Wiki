from flask import render_template, request, session, redirect, url_for
from flaskr.backend import Backend

 #> Ibby: Please add method-level comments for all public methods
def make_endpoints(app):
    back_end = Backend()
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
        # back_end = Backend() // Back end already created in constructor - Angel
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

    @app.route('/login')
    def login_get():
        return render_template('login.html')

    @app.route('/login', methods = ['POST'])
    def login_post():
        username = request.form.get("name").lower()
        password = request.form.get("password")

        signed_in, err = back_end.sign_in(username, password)

        if signed_in:
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', err_message = err)
    
    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('login_get'))

    @app.route('/pages/scholarships')
    def scholarships_page():
        return render_template('/scholarships.html')
    
    @app.route('/pages/opportunities')
    def opportunities_page():
        return render_template('/opportunities.html')

    @app.route('/pages/joy_buolamwini')
    def joy_buolamwini_page():
        return render_template('/joy_buolamwini.html')