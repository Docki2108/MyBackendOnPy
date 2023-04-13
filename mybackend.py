# import sys
# import hashlib
# import random

# from functools import wraps
# import jwt
# from flask import Flask, request, jsonify, current_app
# from werkzeug.exceptions import Unauthorized
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, timedelta

# print()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.email}', '{self.role}')"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    role = data['role']

    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(email=email, password=hashed_password, role=role)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully!'}), 201
    except:
        return jsonify({'message': 'Something went wrong!'}), 500

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify!'}), 401

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return jsonify({'message': 'Could not verify!'}), 401

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return jsonify({'message': 'Could not verify!'}), 401

if __name__ == '__main__':
    app.run(debug=True)
