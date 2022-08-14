from crypt import methods
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import FeedbackForm, RegisterForm, LoginForm
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
    if "username" in session:
        return redirect(f"/users/{session['username']}")
        
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

@app.route('/users/<username>', methods=['GET','POST'])
def secret_user(username):
    """"""
    if "username" in session: 
        user = User.query.get_or_404(username)
        return render_template("secret.html", user=user)
    return redirect("/login")

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """delete a user"""
    if "username" in session  and username==session["username"]:
        user=User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        return redirect("/login")

    return redirect("/")


@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def add_feedback(username):
    """add feedback"""
    if "username" in session and username==session["username"]:
        form = FeedbackForm()

        if form.validate_on_submit():
            title=form.title.data
            content=form.content.data
            new_feedback=Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            flash("Successfully added your feedback!","success")
            return redirect(f"/users/{username}")
        
        return render_template("feedback.html", form=form)

    return redirect("/login")

@app.route('/login', methods=['GET','POST'])
def login():
    """login a user"""
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
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

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """update feedback"""
    feedback=Feedback.query.get_or_404(feedback_id) 
    if "username" in session and feedback.username==session["username"]:
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title=form.title.data
            feedback.content=form.content.data
            db.session.commit()
            return redirect(f"/users/{feedback.username}")
        else:
            return render_template("feedback.html", form=form)

    return redirect("/login")

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """delete feedback"""
    feedback=Feedback.query.get_or_404(feedback_id) 
    if "username" in session and feedback.username==session["username"]:
        username=feedback.username
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    
    return redirect("/login")


