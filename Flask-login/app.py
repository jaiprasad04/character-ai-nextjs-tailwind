# Import necessary modules
from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from config import ApplicationConfig
from model import db, User

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)

CORS(app, supports_credentials=True)

server_session = Session(app)

db.init_app(app)

with app.app_context():
    db.create_all()

# Route to get current user information
@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(id=user_id).first()

    if user:
        return jsonify({
            "id": user.id,
            "email": user.email
        })

# Route to register a new user
@app.route('/register', methods=['POST'])
def register_user():
    email = request.json["email1"]
    password = request.json["password1"]

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({
        'message': 'User registered successfully',
        'id': new_user.id,
        'email': new_user.email
    }), 201

# Route to log in a user
@app.route('/login', methods=['POST'])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    session["user_id"] = user.id

    return jsonify({
        'message': 'Login successful',
        'id': user.id,
        "email": user.email
    }), 200

# Route to log out a user
@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return jsonify({"message": "Logout successful"}), 200

# Route to get list of users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = []

    for user in users:
        users_list.append({
            "id": user.id,
            "email": user.email
        })

    return jsonify(users_list)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
