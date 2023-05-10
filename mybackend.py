import smtplib
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from email.message import EmailMessage
from smsc.api import SMSC
from smsc.messages import SMSMessage
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, 
)
from flask import session
from smsc import SMSC
from flask_jwt_extended import get_jwt
from datetime import datetime
import base64
from sqlalchemy import Column, Integer, String, ForeignKey, Time, CheckConstraint
from flask_mail import Mail, Message
import random
import time
from sqlalchemy.orm import joinedload
import random
import string
from flask_mail import Message, Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:a0a65e9085b36e6b3f86fe9cf5401f6d03b9880f@localhost:5432/fok_kometa_backend_py'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'


db = SQLAlchemy(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
blacklist = set()
login = 'dumilin'
password = 'MX3-b2s-SBK-NTi'
sender = 'ФОК Комета' 
charset = 'utf-8'
client = SMSC(login='dumilin', password='MX3-b2s-SBK-NTi')
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/forgot_password', methods=['GET'])
def forgot_password():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Пользователь с такой почтой не найден.'}), 404

    personal_data = PersonalData.query.filter_by(user_id=user.id_user).first()

    if personal_data is None or personal_data.Mobile_number is None:
        return jsonify({'message': 'Номер телефона пользователя не найден.'}), 404

    phone_number = personal_data.Mobile_number.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')[1:]
    code = generate_code()
    user.password_reset_code = code
    session['reset_password_code'] = code
    db.session.commit()
    response = client.send(to = phone_number, message=SMSMessage(text=f'Уважаемый пользователь, код: {code}'))
    if jsonify:
        return jsonify({'message': 'Ошибка при отправке SMS-сообщения.'}), 500
    return jsonify({'message': 'Код для смены пароля был отправлен на ваш телефон.'}), 200


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    code = data['code']
    new_password = data['new_password']

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Пользователь с такой почтой не найден.'}), 404
    
    personal_data = PersonalData.query.filter_by(user_id=user.id_user).first()

    if personal_data is None or personal_data.Mobile_number is None:
        return jsonify({'message': 'Номер телефона пользователя не найден.'}), 404

    phone_number = personal_data.Mobile_number.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')[1:]

    if code != session.get('reset_password_code'):
        return jsonify({'message': 'Неверный код для смены пароля.'}), 400
    hashed_password = generate_password_hash(new_password, method='sha256')

    user.password = hashed_password
    user.password_reset_code = None
    db.session.commit()

    return jsonify({'message': 'Пароль успешно изменен.'}), 200

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    personal_data = db.relationship('PersonalData', backref='user', uselist=False)

    def get(self):
        personal_data = PersonalData.query.filter_by(user_id=self.id_user).first()
        if personal_data is not None:
            return {
                'id_user': self.id_user,
                'email': self.email,
                'role': self.role,
                'personal_data': {
                    'ID_Personal_data': personal_data.ID_Personal_data,
                    'Second_name': personal_data.Second_name,
                    'First_name': personal_data.First_name,
                    'Patronymic': personal_data.Patronymic,
                    'Mobile_number': personal_data.Mobile_number
                }
            }
        else:
            return {
                'id_user': self.id_user,
                'email': self.email,
                'role': self.role,
                'personal_data': {
                    'ID_Personal_data': None,
                    'Second_name': None,
                    'First_name': None,
                    'Patronymic': None,
                    'Mobile_number': None
                }
            }


class PersonalData(db.Model):
    ID_Personal_data = db.Column(db.Integer, primary_key=True)
    Second_name = db.Column(db.String(50), nullable=True)
    First_name = db.Column(db.String(50), nullable=True)
    Patronymic = db.Column(db.String(50), nullable=True)
    Mobile_number = db.Column(db.String(18), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    
    
class Coach(db.Model):
    ID_Coach = db.Column(db.Integer, primary_key=True)
    Coachs_second_name = db.Column(db.String(50), nullable=False)
    Coachs_first_Name = db.Column(db.String(50), nullable=False)
    Coachs_patronymic = db.Column(db.String(50), nullable=True)
    Specialization = db.Column(db.String(300), nullable=False)
    Work_experience = db.Column(db.Integer, nullable=False)
    
    
    
class Group_workout_category(db.Model):
    ID_Group_workout_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)
    
    
class Group_workout(db.Model):
    ID_Group_workout = db.Column(db.Integer, primary_key=True)
    Event_date = db.Column(db.String(10), nullable=False)
    Start_time = db.Column(db.Time, nullable=False)
    End_time = db.Column(db.Time, nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(300), nullable=False)
    Load_score = db.Column(db.Integer, nullable=False)
    Recommended_age = db.Column(db.Integer, nullable=False)
    Group_workout_category_ID = db.Column(db.Integer, db.ForeignKey('group_workout_category.ID_Group_workout_category'), nullable=False)
    Coach_ID = db.Column(db.Integer, db.ForeignKey('coach.ID_Coach'), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    
    
    
    
class Service(db.Model):
    ID_Service = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Cost = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(200), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    Service_category_ID = db.Column(db.Integer, db.ForeignKey('service_category.ID_Service_category'), nullable=False)
    service_category = db.relationship('Service_category', backref='services')


class Service_category(db.Model):
    ID_Service_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)

class News_category(db.Model):
    ID_News_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)

class News(db.Model):
    ID_News = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), nullable=False, unique=True)
    Content = db.Column(db.String(500), nullable=False)
    News_category_ID = db.Column(db.Integer, db.ForeignKey('news_category.ID_News_category'), nullable=False)
    Create_date = db.Column(db.String(20), default=datetime.utcnow().strftime('%d.%m.%Y %H:%M'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Create_date = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    

    
class Feedback_message(db.Model):
    ID_Feedback_message = db.Column(db.Integer, primary_key=True)
    Message = db.Column(db.String(500), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    Create_date = db.Column(db.String(20), default=datetime.utcnow().strftime('%d.%m.%Y %H:%M'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Create_date = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    

class Diet_category(db.Model):
    ID_Diet_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)

class Diet(db.Model):
    ID_Diet = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Diet_category_ID = db.Column(db.Integer, db.ForeignKey('diet_category.ID_Diet_category'), nullable=False)
    category = db.relationship('Diet_category', backref='diets')


class Dish_category(db.Model):
    ID_Dish_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    
class Dish(db.Model):
    ID_Dish = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    KCal = db.Column(db.Integer, nullable=False)
    PFC_ID = db.Column(db.Integer, db.ForeignKey('pfc.ID_PFC'), nullable=False)
    Diet_ID = db.Column(db.Integer, db.ForeignKey('diet.ID_Diet'), nullable=False)
    Dish_category_ID = db.Column(db.Integer, db.ForeignKey('dish_category.ID_Dish_category'), nullable=False)
    category = db.relationship('Dish_category', backref='dishes')

    
class PFC(db.Model):
    ID_PFC = db.Column(db.Integer, primary_key=True)
    Proteins = db.Column(db.Integer, nullable=False)
    Fats = db.Column(db.Integer, nullable=False)
    Carbohydrates = db.Column(db.Integer, nullable=False)
    

class Person_workout(db.Model):
    ID_Person_workout = db.Column(Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)
    Description = db.Column(db.String(300), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    
class Exercise(db.Model):
    ID_Exercise = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Description = Column(String(500), nullable=False)
    Load_score = Column(Integer, nullable=False)
    Exercise_category_id = Column(Integer, ForeignKey('exercise_category.ID_Exercise_category'), nullable=False)
    Exercise_plan_id = Column(Integer, ForeignKey('exercise_plan.ID_Exercise_plan'), nullable=False)
    Person_workout_id = Column(Integer, ForeignKey('person_workout.ID_Person_workout'), nullable=False)
    
    

class Exercise_category(db.Model):
    ID_Exercise_category = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False, unique=True)

class Exercise_plan(db.Model):
    ID_Exercise_plan = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Description = Column(String(100), nullable=False)
    Number_of_repetitions = Column(Integer, nullable=False)
    Number_of_approaches = Column(Integer, nullable=False)
    Rest_time = Column(Time, nullable=False)


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
    return jsonify({'access_token': access_token, 'email': email}), 200


# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     current_user_id = get_jwt_identity()
#     current_user = User.query.filter_by(id_user=current_user_id).first()
#     return jsonify({'message': f'Hello, {current_user.email}!'}), 200


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Вы успешно вышли из системы'}), 200


@app.route('/clients', methods=['GET'])
def get_clients():
    clients = User.query.filter_by(role='Client').all()
    result = []
    for client in clients:
        result.append(client.get())
    return jsonify(result)


@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id_user=current_user).first()
    return jsonify(user.get()), 200

@app.route('/update_user', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.get_json()
    email = data['email']
    second_name = data['second_name']
    first_name = data['first_name']
    patronymic = data['patronymic']
    mobile_number = data['mobile_number']

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Пользователь не найден!'}), 404

    personal_data = PersonalData.query.filter_by(user_id=user.id_user).first()
    personal_data.Second_name = second_name
    personal_data.First_name = first_name
    personal_data.Patronymic = patronymic
    personal_data.Mobile_number = mobile_number

    db.session.commit()

    return jsonify({'message': 'Данные пользователя успешно изменены!'}), 200

@app.route('/coach', methods=['POST'])
def add_coach():
    data = request.get_json()
    coach = Coach(Coachs_second_name=data['second_name'],
                  Coachs_first_Name=data['first_name'],
                  Coachs_patronymic=data['patronymic'],
                  Specialization=data['specialization'],
                  Work_experience=data['work_experience'])
    db.session.add(coach)
    db.session.commit()
    return jsonify({'message': 'Добавление тренера прошло успешно!'})

@app.route('/coach/<int:coach_id>', methods=['PUT'])
def update_coach(coach_id):
    coach = Coach.query.get(coach_id)
    if not coach:
        return jsonify({'message': 'Тренер не найден'})
    data = request.get_json()
    coach.Coachs_second_name = data['second_name']
    coach.Coachs_first_Name = data['first_name']
    coach.Coachs_patronymic = data['patronymic']
    coach.Specialization = data['specialization']
    coach.Work_experience = data['work_experience']
    
    db.session.commit()
    return jsonify({'message': 'Изменение тренера прошло успешно'})

@app.route('/coach/<int:coach_id>', methods=['DELETE'])
def delete_coach(coach_id):
    coach = Coach.query.get(coach_id)
    if not coach:
        return jsonify({'message': 'Тренер не найден'})
    db.session.delete(coach)
    db.session.commit()
    return jsonify({'message': 'Удаление тренера прошло успешно!'})

@app.route('/group_workout_categories', methods=['GET'])
def get_group_workout_categories():
    group_workout_categories = Group_workout_category.query.all()
    result = []
    for category in group_workout_categories:
        category_data = {
            'ID_Group_workout_category': category.ID_Group_workout_category,
            'Name': category.Name
        }
        result.append(category_data)
    return jsonify(result)

@app.route('/group_workout_category', methods=['POST'])
def add_group_workout_category():
    data = request.get_json()
    group_workout_category = Group_workout_category(Name=data['name'])
    db.session.add(group_workout_category)
    db.session.commit()
    return jsonify({'message': 'Добавление категории групповой тренировки прошло успешно!'})

@app.route('/group_workout_category/<int:id>', methods=['PUT'])
def update_group_workout_category(id):
    category = Group_workout_category.query.get_or_404(id)
    data = request.get_json()
    Name = data['name']
    category.name = Name
    db.session.commit()
    return {'message': 'Изменение категории групповой тренировки прошло успешно!'}

@app.route('/group_workout_category/<int:id>', methods=['DELETE'])
def delete_group_workout_category(id):
    category = Group_workout_category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return {'message': 'Удаление категории групповой тренировки прошло успешно!'}



@app.route('/group_workout', methods=['POST'])
def add_group_workout():
    data = request.get_json()
    event_date = datetime.strptime(data['event_date'], '%d.%m.%Y').strftime('%d.%m.%Y')
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    name = data['name']
    description = data['description']
    load_score = data['load_score']
    recommended_age = data['recommended_age']
    group_workout_category_id = data['group_workout_category_id']
    coach_id = data['coach_id']
    user_id = data['user_id']
    
    new_group_workout = Group_workout(Event_date=event_date, Start_time=start_time, End_time=end_time,
                                      Name=name, Description=description, Load_score=load_score,
                                      Recommended_age=recommended_age, Group_workout_category_ID=group_workout_category_id,
                                      Coach_ID=coach_id, User_id=user_id)
    
    db.session.add(new_group_workout)
    db.session.commit()
    
    return {'message': 'Добавление групповой тренировки прошло успешно!'}



@app.route('/group_workout/<id>', methods=['PUT'])
def update_group_workout(id):
    group_workout = Group_workout.query.get(id)
    if not group_workout:
        return {'message': 'Групповая тренировка не найдена'}
    
    data = request.get_json()
    if 'event_date' in data:
        group_workout.Event_date = datetime.strptime(data['event_date'], '%d.%m.%Y').strftime('%d.%m.%Y')
    if 'start_time' in data:
        group_workout.Start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    if 'end_time' in data:
        group_workout.End_time = datetime.strptime(data['end_time'], '%H:%M').time()
    if 'name' in data:
        group_workout.Name = data['name']
    if 'description' in data:
        group_workout.Description = data['description']
    if 'load_score' in data:
        group_workout.Load_score = data['load_score']
    if 'recommended_age' in data:
        group_workout.Recommended_age = data['recommended_age']
    if 'group_workout_category_id' in data:
        group_workout.Group_workout_category_ID = data['group_workout_category_id']
    if 'coach_id' in data:
        group_workout.Coach_ID = data['coach_id']
    if 'user_id' in data:
        group_workout.User_id = data['user_id']
    
    db.session.commit()
    
    return {'message': 'Изменение групповой тренировки прошло успешно!'}



@app.route('/group_workout/<id>', methods=['DELETE'])
def delete_group_workout(id):
    group_workout = Group_workout.query.get(id)
    if not group_workout:
        return {'message': 'Групповая тренировка не найдена'}
    
    db.session.delete(group_workout)
    db.session.commit()
    
    return {'message': 'Удаление групповой тренировки прошло успешно!'}


@app.route('/service_categories', methods=['GET'])
def get_service_categories():
    service_categories = Service_category.query.all()
    result = []
    for category in service_categories:
        category_data = {
            'ID_Service_category': category.ID_Service_category,
            'Name': category.Name
        }
        result.append(category_data)
    return jsonify(result)


@app.route('/service_category', methods=['POST'])
def add_service_category():
    data = request.get_json()
    name = data['name']
    category = Service_category(Name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Добавление категории услуг прошло успешно!'})


@app.route('/service_category/<int:id>', methods=['PUT'])
def update_service_category(id):
    category = Service_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория услуг не найдена'})
    data = request.get_json()
    name = data['name']
    category.Name = name
    db.session.commit()
    return jsonify({'message': 'Изменение категории услуг прошло успешно!'})


@app.route('/service_category/<int:id>', methods=['DELETE'])
def delete_service_category(id):
    category = Service_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория услуг не найдена'})
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Удаление категории услуг прошло успешно!'})






@app.route('/service', methods=['POST'])
def add_service():
    data = request.get_json()
    name = data['name']
    cost = data['cost']
    description = data['description']
    user_id = data['user_id']
    category_id = data['category_id']
    service = Service(Name=name, Cost=cost, Description=description, User_id=user_id, Service_category_ID=category_id)
    db.session.add(service)
    db.session.commit()
    return jsonify({'message': 'Добавление услуги прошло успешно!'})




@app.route('/service/<int:id>', methods=['PUT'])
def update_service(id):
    service = Service.query.get(id)
    if not service:
        return jsonify({'message': 'Услуга не найдена'})
    data = request.get_json()
    name = data['name']
    cost = data['cost']
    description = data['description']
    user_id = data['user_id']
    category_id = data['category_id']
    service.Name = name
    service.Cost = cost
    service.Description = description
    service.User_id = user_id
    service.Service_category_ID = category_id
    db.session.commit()
    return jsonify({'message': 'Изменение услуги прошло успешно!'})



@app.route('/service/<int:id>', methods=['DELETE'])
def delete_service(id):
    service = Service.query.get(id)
    if not service:
        return jsonify({'message': 'Услуга не найдена'})
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Удаление услуги прошло успешно!'})



@app.route('/news_categories', methods=['POST'])
def add_news_category():
    data = request.get_json()
    name = data['name']
    category = News_category(Name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Добавление категории новостей прошло успешно!'})

@app.route('/news_categories/<int:id>', methods=['PUT'])
def update_news_category(id):
    category = News_category.query.get_or_404(id)
    data = request.get_json()
    category.Name = data['name']
    db.session.commit()
    return jsonify({'message': 'Изменение категории новостей прошло успешно!'})

@app.route('/news_categories/<int:id>', methods=['DELETE'])
def delete_news_category(id):
    category = News_category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Удаление категории новостей прошло успешно!'})


@app.route('/news_categories', methods=['GET'])
def get_news_categories():
    news_categories = News_category.query.all()
    output = []
    for news_category in news_categories:
        category_data = {}
        category_data['id'] = news_category.ID_News_category
        category_data['name'] = news_category.Name
        output.append(category_data)
    return jsonify({'news_categories': output})

@app.route('/news', methods=['POST'])
def add_news():
    data = request.get_json()
    title = data['title']   
    content = data['content']
    category_id = data['category_id']
    news = News(Title=title, Content=content, News_category_ID=category_id)
    db.session.add(news)
    db.session.commit()
    return jsonify({'message': 'Добавление новости прошло успешно!'})

@app.route('/news/<int:id>', methods=['PUT'])
def update_news(id):
    news = News.query.get_or_404(id)
    data = request.get_json()
    news.Title = data['title']
    news.Content = data['content']
    news.News_category_ID = data['category_id']
    db.session.commit()
    return jsonify({'message': 'Изменение новости прошло успешно!'})

@app.route('/news/<int:id>', methods=['DELETE'])
def delete_news(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    return jsonify({'message': 'Удаление новости прошло успешно!'})


@app.route('/feedback', methods=['POST'])
def create_feedback():
    data = request.get_json()
    new_feedback = Feedback_message(Message=data['message'], User_id=data['user_id'])
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify({'message': 'Добавление сообщения обратной связи прошло успешно!'}), 201

@app.route('/feedback/<int:id>', methods=['PUT'])
def update_feedback(id):
    feedback = Feedback_message.query.get_or_404(id)
    data = request.get_json()
    feedback.Message = data['message']
    feedback.User_id = data['user_id']
    db.session.commit()
    return jsonify({'message': 'Изменение сообщения обратной связи прошло успешно!'}), 200

@app.route('/feedback/<int:id>', methods=['DELETE'])
def delete_feedback(id):
    feedback = Feedback_message.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'message': 'Удаление сообщения обратной связи прошло успешно!'}), 200



@app.route('/person_workout', methods=['POST'])
def add_person_workout():
    data = request.get_json()
    new_person_workout = Person_workout(Name=data['name'], Description=data['description'], User_id=data['user_id'])
    db.session.add(new_person_workout)
    db.session.commit()
    return jsonify({'message': 'Добавление персональной тренировки прошло успешно!'})


@app.route('/person_workout/<int:id>', methods=['PUT'])
def update_person_workout(id):
    person_workout = Person_workout.query.get(id)
    if not person_workout:
        return jsonify({'message': 'Персональная тренировка не найдена'}), 404
    data = request.get_json()
    person_workout.Name = data['name']
    person_workout.Description = data['description']
    person_workout.User_id = data['user_id']
    db.session.commit()
    return jsonify({'message': 'Изменение персональной тренировки прошло успешно!'})

@app.route('/person_workout/<int:id>', methods=['DELETE'])
def delete_person_workout(id):
    person_workout = Person_workout.query.get(id)
    if not person_workout:
        return jsonify({'message': 'Персональная тренировка не найдена'}), 404
    db.session.delete(person_workout)
    db.session.commit()
    return jsonify({'message': 'Удаление персональной тренировки прошло успешно!'})

@app.route('/exercise', methods=['POST'])
def add_exercise():
    try:
        exercise_data = request.get_json()
        new_exercise = Exercise(
            Name=exercise_data['name'],
            Description=exercise_data['description'],
            Load_score=exercise_data['load_score'],
            Exercise_category_id=exercise_data['exercise_category_id'],
            Exercise_plan_id=exercise_data['exercise_plan_id'],
            Person_workout_id=exercise_data['person_workout_id']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return {'message': 'Добавление упражнения прошло успешно!'}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500


@app.route('/exercise/<int:id>', methods=['PUT'])
def update_exercise(id):
    try:
        exercise_data = request.get_json()
        exercise = Exercise.query.filter_by(ID_Exercise=id).first()
        if exercise:
            exercise.Name = exercise_data['name']
            exercise.Description = exercise_data['description']
            exercise.Load_score = exercise_data['load_score']
            exercise.Exercise_category_id = exercise_data['exercise_category_id']
            exercise.Exercise_plan_id = exercise_data['exercise_plan_id']
            db.session.commit()            
            return {'message': 'Изменение упражнения прошло успешно!'}
        
        else:
            return {'message': 'Упражнение не найдено'}, 404
        
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500



@app.route('/exercise/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    try:
        exercise = Exercise.query.filter_by(ID_Exercise=id).first()
        if exercise:
            db.session.delete(exercise)
            db.session.commit()
            return {'message': 'Удаление упражнения прошло успешно!'}
        else:
            return {'message': 'Упражнение не найдено'}, 404
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500




@app.route('/exercise_category', methods=['POST'])
def add_exercise_category():
    name = request.json['name']
    new_category = Exercise_category(Name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Добавление категории упражнения прошло успешно!'})

@app.route('/exercise_category/<int:id>', methods=['PUT'])
def update_exercise_category(id):
    category = Exercise_category.query.get_or_404(id)
    name = request.json['name']
    category.Name = name
    db.session.commit()
    return jsonify({'message': 'Изменение категории упражнения прошло успешно!'})


@app.route('/exercise_category/<int:id>', methods=['DELETE'])
def delete_exercise_category(id):
    category = Exercise_category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Удаление категории упражнения прошло успешно!'})




@app.route('/exercise_plan', methods=['POST'])
def add_exercise_plan():
    name = request.json['name']
    description = request.json['description']
    num_repetitions = request.json['number_of_repetitions']
    num_approaches = request.json['number_of_approaches']
    rest_time = request.json['rest_time']
    new_plan = Exercise_plan(Name=name, Description=description,
                             Number_of_repetitions=num_repetitions,
                             Number_of_approaches=num_approaches,
                             Rest_time=rest_time)

    db.session.add(new_plan)
    db.session.commit()
    return jsonify({'message': 'Добавление плана тренировок прошло успешно!'})



@app.route('/exercise_plan/<int:id>', methods=['PUT'])
def update_exercise_plan(id):
    plan = Exercise_plan.query.get_or_404(id)

    name = request.json['name']
    description = request.json['description']
    num_repetitions = request.json['number_of_repetitions']
    num_approaches = request.json['number_of_approaches']
    rest_time = request.json['rest_time']

    plan.Name = name
    plan.Description = description
    plan.Number_of_repetitions = num_repetitions
    plan.Number_of_approaches = num_approaches
    plan.Rest_time = rest_time

    db.session.commit()

    return jsonify({'message': 'Изменение плана тренировок прошло успешно!'})




@app.route('/exercise_plan/<int:id>', methods=['DELETE'])
def delete_exercise_plan(id):
    plan = Exercise_plan.query.get_or_404(id)

    db.session.delete(plan)
    db.session.commit()

    return jsonify({'message': 'Удаление плана тренировок прошло успешно!'})


@app.route('/coaches', methods=['GET'])
def get_all_coaches():
    coaches = Coach.query.all()
    result = []
    for coach in coaches:
        coach_data = {
            'id': coach.ID_Coach,
            'second_name': coach.Coachs_second_name,
            'first_name': coach.Coachs_first_Name,
            'patronymic': coach.Coachs_patronymic,
            'specialization': coach.Specialization,
            'work_experience': str(coach.Work_experience)
        }
        result.append(coach_data)
    return jsonify({'coach': result})

@app.route('/services', methods=['GET'])
def get_all_services():
    services = db.session.query(Service, Service_category.Name).join(Service_category).all()
    result = []
    for service, category_name in services:
        service_data = {
            'id': service.ID_Service,
            'name': service.Name,
            'cost': service.Cost,
            'description': service.Description,
            'user_id': service.User_id,
            'service_category': category_name
        }
        result.append(service_data)
    return jsonify({'services': result})


@app.route('/news', methods=['GET'])
def get_news():
    news = News.query.all()
    news_list = []

    for n in news:
        news_category = News_category.query.filter_by(ID_News_category=n.News_category_ID).first()
        news_list.append({
            'id': n.ID_News,
            'title': n.Title,
            'content': n.Content,
            'category': news_category.Name,
            'create_date': n.Create_date
        })

    return jsonify({'news': news_list})

@app.route('/group_workouts', methods=['GET'])
def get_group_workouts():
    group_workouts = Group_workout.query.all()
    group_workouts_list = []

    for gw in group_workouts:
        group_workout_category = Group_workout_category.query.filter_by(ID_Group_workout_category=gw.Group_workout_category_ID).first()
        coach = Coach.query.filter_by(ID_Coach=gw.Coach_ID).first()
        group_workouts_list.append({
            'id': gw.ID_Group_workout,
            'event_date': str(gw.Event_date),
            'start_time': gw.Start_time.strftime('%H:%M:%S'),
            'end_time': gw.End_time.strftime('%H:%M:%S'),
            'name': gw.Name,
            'description': gw.Description,
            'load_score': gw.Load_score,
            'recommended_age': gw.Recommended_age,
            'group_workout_category': group_workout_category.Name,
            'coach': coach.Coachs_second_name + ' ' + coach.Coachs_first_Name + ' ' + coach.Coachs_patronymic,
            'user_id': gw.User_id
        })

    return jsonify({'group_workouts': group_workouts_list})



@app.route('/diet_categories', methods=['POST'])
def add_diet_category():
    data = request.get_json()
    name = data['name']
    category = Diet_category(Name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Категория диет добавлена успешно!'})

@app.route('/diet_categories/<int:id>', methods=['PUT'])
def update_diet_category(id):
    category = Diet_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория диет не найдена'})
    data = request.get_json()
    name = data['name']
    category.Name = name
    db.session.commit()
    return jsonify({'message': 'Категория диет изменена успешно!'})

@app.route('/diet_categories/<int:id>', methods=['DELETE'])
def delete_diet_category(id):
    category = Diet_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория диет не найдена'})
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Категория диет удалена успешно!'})

@app.route('/diet_categories', methods=['GET'])
def get_diet_categories():
    categories = Diet_category.query.all()
    result = []
    for category in categories:
        category_data = {}
    category_data['id'] = category.ID_Diet_category
    category_data['name'] = category.Name
    result.append(category_data)
    return jsonify(result)






@app.route('/dish_categories', methods=['POST'])
def add_dish_category():
    data = request.get_json()
    name = data['name']
    category = Dish_category(Name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Категория блюд добавлена успешно!'})

@app.route('/dish_categories/<int:id>', methods=['PUT'])
def update_dish_category(id):
    category = Dish_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория блюд не найдена'})
    data = request.get_json()
    name = data['name']
    category.Name = name
    db.session.commit()
    return jsonify({'message': 'Категория блюд изменена успешно!'})

@app.route('/dish_categories/<int:id>', methods=['DELETE'])
def delete_dish_category(id):
    category = Dish_category.query.get(id)
    if not category:
        return jsonify({'message': 'Категория блюд не найдена'})
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Категория блюд удалена успешно!'})

@app.route('/dish_categories', methods=['GET'])
def get_dish_categories():
    categories = Dish_category.query.all()
    result = []
    for category in categories:
        category_data = {}
    category_data['id'] = category.ID_Dish_category
    category_data['name'] = category.Name
    result.append(category_data)
    return jsonify(result)



@app.route('/pfc', methods=['POST'])
def add_pfc():
    data = request.get_json()
    proteins = data['proteins']
    fats = data['fats']
    carbohydrates = data['carbohydrates']
    pfc = PFC(Proteins=proteins, Fats=fats, Carbohydrates=carbohydrates)
    db.session.add(pfc)
    db.session.commit()
    return jsonify({'message': 'Добавление БЖУ прошло успешно!'})

@app.route('/pfc/<int:id>', methods=['PUT'])
def update_pfc(id):
    pfc = PFC.query.get(id)
    if not pfc:
        return jsonify({'message': 'БЖУ не найден'})
    data = request.get_json()
    proteins = data['proteins']
    fats = data['fats']
    carbohydrates = data['carbohydrates']
    pfc.Proteins = proteins
    pfc.Fats = fats
    pfc.Carbohydrates = carbohydrates
    db.session.commit()
    return jsonify({'message': 'Изменение БЖУ прошло успешно!'})

@app.route('/pfc/<int:id>', methods=['DELETE'])
def delete_pfc(id):
    pfc = PFC.query.get(id)
    if not pfc:
        return jsonify({'message': 'БЖЦ не найден'})
    db.session.delete(pfc)
    db.session.commit()
    return jsonify({'message': 'Удаление БЖУ прошло успешно!'})

@app.route('/pfc', methods=['GET'])
def get_pfc():
    pfc = PFC.query.all()
    result = []
    for item in pfc:
        item_data = {}
    item_data['id'] = item.ID_PFC
    item_data['proteins'] = item.Proteins
    item_data['fats'] = item.Fats
    item_data['carbohydrates'] = item.Carbohydrates
    result.append(item_data)
    return jsonify(result)



@app.route('/diet', methods=['POST'])
def add_diet():
    data = request.get_json()
    name = data['name']
    duration = data['duration']
    diet_category_id = data['diet_category_id']
    diet = Diet(Name=name, Duration=duration, Diet_category_ID=diet_category_id)
    db.session.add(diet)
    db.session.commit()
    return jsonify({'message': 'Диета добавлена успешно!'})

@app.route('/diet/<int:id>', methods=['PUT'])
def update_diet(id):
    diet = Diet.query.get(id)
    if not diet:
        return jsonify({'message': 'Диета не найдена'})
    data = request.get_json()
    name = data['name']
    duration = data['duration']
    diet_category_id = data['diet_category_id']
    diet.Name = name
    diet.Duration = duration
    diet.Diet_category_ID = diet_category_id
    db.session.commit()
    return jsonify({'message': 'Диета изменена успешно!'})

@app.route('/diet/<int:id>', methods=['DELETE'])
def delete_diet(id):
    diet = Diet.query.get(id)
    if not diet:
        return jsonify({'message': 'Диета не найдена'})
    db.session.delete(diet)
    db.session.commit()
    return jsonify({'message': 'Диета удалена успешно!'})

@app.route('/diet', methods=['GET'])
def get_diet():
    diet = Diet.query.all()
    result = []
    for item in diet:
        item_data = {}
    item_data['id'] = item.ID_Diet
    item_data['name'] = item.Name
    item_data['duration'] = item.Duration
    item_data['diet_category_id'] = item.Diet_category_ID
    result.append(item_data)
    return jsonify(result)





@app.route('/dish', methods=['POST'])
def add_dish():
    data = request.get_json()
    name = data['name']
    kcal = data['kcal']
    pfc_id = data['pfc_id']
    diet_id = data['diet_id']
    dish_category_id = data['dish_category_id']
    dish = Dish(Name=name, KCal=kcal, PFC_ID=pfc_id, Diet_ID=diet_id, Dish_category_ID=dish_category_id)
    db.session.add(dish)
    db.session.commit()
    return jsonify({'message': 'Блюдо добавлено успешно!'})

@app.route('/dish/<int:id>', methods=['PUT'])
def update_dish(id):
    dish = Dish.query.get(id)
    if not dish:
        return jsonify({'message': 'Блюдо не найдено'})
    data = request.get_json()
    name = data['name']
    kcal = data['kcal']
    pfc_id = data['pfc_id']
    diet_id = data['diet_id']
    dish_category_id = data['dish_category_id']
    dish.Name = name
    dish.KCal = kcal
    dish.PFC_ID = pfc_id
    dish.Diet_ID = diet_id
    dish.Dish_category_ID = dish_category_id
    db.session.commit()
    return jsonify({'message': 'Блюдо изменено успешно!'})

@app.route('/dish/<int:id>', methods=['DELETE'])
def delete_dish(id):
    dish = Dish.query.get(id)
    if not dish:
        return jsonify({'message': 'Блюдо не найдено'})
    db.session.delete(dish)
    db.session.commit()
    return jsonify({'message': 'Блюдо удалено успешно!'})

@app.route('/dish', methods=['GET'])
def get_dish():
    dish = Dish.query.all()
    result = []
    for item in dish:
        item_data = {}
    item_data['id'] = item.ID_Dish
    item_data['name'] = item.Name
    item_data['kcal'] = item.KCal
    item_data['pfc_id'] = item.PFC_ID
    item_data['diet_id'] = item.Diet_ID
    item_data['dish_category_id'] = item.Dish_category_ID
    result.append(item_data)
    return jsonify(result)



@app.route('/dishes', methods=['GET'])
def get_dishes():
    dishes = Dish.query.all()
    result = []
    for dish in dishes:
        pfc = PFC.query.get(dish.PFC_ID)
        diet = Diet.query.get(dish.Diet_ID)
        dish_category = Dish_category.query.get(dish.Dish_category_ID)
        result.append({
            'id': dish.ID_Dish,
            'name': dish.Name,
            'kcal': dish.KCal,
            'pfc': {
                'proteins': pfc.Proteins,
                'fats': pfc.Fats,
                'carbohydrates': pfc.Carbohydrates
            },
            'diet': {
                'name': diet.Name,
                'duration': diet.Duration,
                'category': diet.category.Name
            },
            'category': dish_category.Name
        })
    return jsonify(result)

@app.route('/exercise', methods=['GET'])
def get_exercise():
    exercise_data = db.session.query(Exercise, Exercise_plan, Exercise_category, Person_workout).join(Exercise_plan).join(Exercise_category).join(Person_workout).all()
    result = []
    for exercise, exercise_plan, exercise_category, person_workout in exercise_data:
        exercise_dict = {}
        exercise_dict['ID_Exercise'] = exercise.ID_Exercise
        exercise_dict['Name'] = exercise.Name
        exercise_dict['Description'] = exercise.Description
        exercise_dict['Load_score'] = exercise.Load_score
        
        exercise_dict['Exercise_category'] = exercise_category.Name
        
        exercise_dict['Exercise_plan'] = exercise_plan.Name
        exercise_dict['Number_of_repetitions'] = exercise_plan.Number_of_repetitions
        exercise_dict['Number_of_approaches'] = exercise_plan.Number_of_approaches
        exercise_dict['Exercise_plan_Description'] = exercise_plan.Description
        exercise_dict['Rest_time'] = exercise_plan.Rest_time.strftime('%M:%S')
        
        exercise_dict['Person_workout'] = person_workout.Name
        exercise_dict['Person_workout_Description'] = person_workout.Description
        result.append(exercise_dict)
    return jsonify(result)


with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)