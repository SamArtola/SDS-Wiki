from flask import render_template, request, session
from flaskr.backend import Backend

 #> Ibby: Please add method-level comments for all public methods
def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        #> Ibby: You can remove TODO comments that are completed
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route('/upload', methods = ['GET','POST'])
    def upload():
        if request.method=="POST":
            backend=Backend()
            file=request.files['file']
            backend.upload_file(file)
        return render_template('/upload.html')

    @app.route('/about')
    def about():
        back=Backend()
        pics=back.get_image()
        return render_template('about.html',pics=pics)

    @app.route('/signup', methods =['GET'])
    def signup_get():
        return render_template('/signup.html')
    
    @app.route('/signup', methods =['POST'])
    def signup_post():
        back_end = Backend()
        display_text = ''

        username = request.form['name']
        password = request.form['pwd']

        if not username or not password:
            display_text = "Please fill all required fields"
            
        elif back_end.check_user(username):
            display_text = "Ooops, that username is taken."

        else:
            session['username'] = username
            back_end.sign_up(username, password)
            display_text = "Successfully registered!"
            return render_template('main.html', signed_in =True, username = username)

        return render_template('/signup.html', display_text=display_text)

    @app.route('/pages')
    def page_index():
        backend = Backend()
        page_list=backend.get_all_page_names()
        return render_template('/page_index.html', page_list=page_list)

    @app.route('/pages/<curpage>')
    def show_wiki(curpage):
        backend=Backend()
        page=curpage
        content=backend.get_wiki_page(page)
        return render_template('/pages.html',contents=content,pagename=page)             

    @app.route('/quotes')
    def quotes():
        return render_template('/quotes.html')
    
    @app.route('/kathjohn')
    def kathjohn():
        return render_template('/kathjohn.html')

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
