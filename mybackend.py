import jwt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, 
)
from flask_jwt_extended import get_jwt


# конфигурация бд
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:a0a65e9085b36e6b3f86fe9cf5401f6d03b9880f@localhost:5432/fok_kometa_backend_py'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
blacklist = set()

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    personal_data = db.relationship('PersonalData', backref='user', uselist=False)

class PersonalData(db.Model):
    ID_Personal_data = db.Column(db.Integer, primary_key=True)
    Second_name = db.Column(db.String(50), nullable=True)
    First_name = db.Column(db.String(50), nullable=True)
    Patronymic = db.Column(db.String(50), nullable=True)
    Mobile_number = db.Column(db.String(16), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)

    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    role = data['role']
    second_name = data['second_name']
    first_name = data['first_name']
    patronymic = data['patronymic']
    mobile_number = data['mobile_number']

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_password, role=role)

    new_personal_data = PersonalData(Second_name=second_name, First_name=first_name, Patronymic=patronymic, Mobile_number=mobile_number)
    new_user.personal_data = new_personal_data

    try:
        db.session.add(new_user)
        db.session.add(new_personal_data)
        db.session.commit()
        return jsonify({'message': 'Пользователь успешно зарегистрирован!'}), 201
    except:
        return jsonify({'message': 'Ошибка! Что-то не так...'}), 500



@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Пользователь не найден!'}), 404

    personal_data = PersonalData.query.filter_by(user_id=user.id_user).first()
    db.session.delete(user)
    db.session.delete(personal_data)
    db.session.commit()

    return jsonify({'message': 'Пользователь успешно удален!'}), 200



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Неверный логин или пароль!'}), 401

    access_token = create_access_token(identity=user.id_user)
    return jsonify({'access_token': access_token}), 200


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(id_user=current_user_id).first()
    return jsonify({'message': f'Hello, {current_user.email}!'}), 200


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Вы успешно вышли из системы'}), 200




with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)






# class Coach(db.Model):    
#     ID_Coach = db.Column(db.Integer, primary_key=True)
#     Coachs_second_name = db.Column(db.String(50), nullable=True)
#     Coachs_first_Name = db.Column(db.String(50), nullable=True)
#     Coachs_patronymic = db.Column(db.String(50), nullable=True)
#     Specialization = db.Column(db.String(200), nullable=False)
#     Work_experience = db.Column(db.Integer, nullable=False)
#     Sporting_achievements = db.Column(db.String(200), nullable=False)

# class GroupWorkoutCategory(db.Model):
#     ID_Group_workout_category = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(50), nullable=False, unique=True)

# class GroupWorkout(db.Model):
#     ID_Group_workout = db.Column(db.Integer, primary_key=True)
#     Event_date = db.Column(db.Date, nullable=False)
#     Start_time = db.Column(db.Time, nullable=False)
#     End_time = db.Column(db.Time, nullable=False)
#     Name = db.Column(db.String(50), nullable=False)
#     Description = db.Column(db.String(150), nullable=False)
#     Load_score = db.Column(db.Integer, nullable=False)
#     Recommended_age = db.Column(db.Integer, nullable=False)
#     Group_workout_category_ID = db.Column(db.Integer, db.ForeignKey('group_workout_category.ID_Group_workout_category'), nullable=False)
#     User_ID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     Coach_ID = db.Column(db.Integer, db.ForeignKey('coach.ID_Coach'), nullable=False)

# class DietCategory(db.Model):
#     ID_Diet_category = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(50), nullable=False)

# class Diet(db.Model):
#     ID_Diet = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(100), nullable=False)
#     Duration = db.Column(db.Integer, nullable=False)
#     Diet_category_ID = db.Column(db.Integer, db.ForeignKey('diet_category.ID_Diet_category'), nullable=False)
#     User_ID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# class PFC(db.Model):
#     ID_PFC = db.Column(db.Integer, primary_key=True)
#     Proteins = db.Column(db.Integer, nullable=False)
#     Fats = db.Column(db.Integer, nullable=False)
#     Carbohydrates = db.Column(db.Integer, nullable=False)

# class Dish(db.Model):
#     ID_Dish = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(50), nullable=False)
#     KCal = db.Column(db.Integer, nullable=False)




# # Create route to register a new user
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     email = data['email']
#     password = data['password']
#     role = data['role']

#     hashed_password = generate_password_hash(password, method='sha256')
#     new_user = User(email=email, password=hashed_password, role=role)

#     try:
#         db.session.add(new_user)
#         db.session.commit()
#         return jsonify({'message': 'Пользователь успешно зарегистрирован!'}), 201
#     except:
#         return jsonify({'message': 'Ошибка! Что-то не так...'}), 500

# # Create route to log in a user
# @app.route('/login', methods=['POST'])
# def login():
#     auth = request.authorization

#     if not auth or not auth.username or not auth.password:
#         return jsonify({'message': 'Could not verify!'}), 401

#     user = User.query.filter_by(email=auth.username).first()

#     if not user:
#         return jsonify({'message': 'Could not verify!'}), 401

#     if check_password_hash(user.password, auth.password):
#         token = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
#         return jsonify({'token': token.decode('UTF-8')})

#     return jsonify({'message': 'Could not verify!'}), 401


# # удаление существующего пользователя по его айди в запросе
# @app.route('/user/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({'message': 'User not found!'}), 404
#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({'message': 'Удаление пользователя прошло успешно!'})