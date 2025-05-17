from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.relationship('Password', backref='user', uselist=False, cascade='all, delete')

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hashed_password = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route("/")
def hello_world():
    return '''
    <h1>Hello, World!</h1>
    <p><a href="/register">Register an Account</a></p>
    '''

# Route for displaying registration form
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return "Username and Email are required!", 400

        if User.query.filter_by(email=email).first():
            return "User with that email already exists!", 409

        # Create New User
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.flush() # Send pending changes to the db without committing them

        # Hash and store password
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        new_password = Password(hashed_password=hashed, user_id=new_user.id)
        db.session.add(new_password)

        db.session.commit()

        return redirect(url_for('hello_world'))

    return render_template("register.html")  # Render HTML form on GET request

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

# set up user table; implement authentication (password checking, JWT package); Create an endpoint so we can send a request to write to the database (we don't want to manually add/modify/delete every user). Set up logging