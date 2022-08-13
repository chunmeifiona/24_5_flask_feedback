from crypt import methods
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect ("/register")

@app.route('/register', methods =["GET","POST"])
def register():
    """create a user"""
    form=RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username/email taken.  Please pick another")
            return render_template("register.html", form=form)
        session['username']=new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template("register.html", form=form)

@app.route('/users/<username>')
def secret_user(username):
    """"""
    if "username" in session: 
        flash("It's secret")
        user = User.query.get_or_404(username)
        return render_template("secret.html", user=user)
    return redirect("/login")

@app.route('/login', methods=['GET','POST'])
def login():
    """login a user"""
    form=LoginForm()
    
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!","primary")
            session['username']=user.username
            return redirect(f"/users/{user.username}")
    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    """"logout"""
    session.pop("username")
    flash("Goodbye!","info")
    return redirect('/')


