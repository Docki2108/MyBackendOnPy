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
from datetime import datetime
import base64
from sqlalchemy import Column, Integer, String, ForeignKey, Time, CheckConstraint


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
    Mobile_number = db.Column(db.String(17), nullable=True, unique=True)
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
    Event_date = db.Column(db.Date, nullable=False)
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
    Create_date = db.Column(db.TIMESTAMP, default=db.func.now())
    

class Client(db.Model):
    ID_Client = db.Column(db.Integer, db.ForeignKey('user.id_user'), primary_key=True)
    Growth = db.Column(db.Integer, nullable=True)
    Weight = db.Column(db.Integer, nullable=True)  
    Age_person = db.Column(db.Integer, nullable=True)
    user = db.relationship("User", backref="client")
    
class Feedback_message(db.Model):
    ID_Feedback_message = db.Column(db.Integer, primary_key=True)
    Message = db.Column(db.String(500), nullable=False)
    Create_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    Client_ID = db.Column(db.Integer, db.ForeignKey('client.ID_Client'), nullable=False)
    

class DietCategory(db.Model):
    ID_Diet_category = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)

class Diet(db.Model):
    ID_Diet = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Diet_category_ID = db.Column(db.Integer, db.ForeignKey('diet_category.ID_Diet_category'), nullable=False)
    User_ID = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    Created_date = db.Column(db.TIMESTAMP, default=db.func.now())

    category = db.relationship('DietCategory', backref='diets')

   

class PFC(db.Model):
    ID_PFC = db.Column(db.Integer, primary_key=True)
    Proteins = db.Column(db.Integer, nullable=False)
    Fats = db.Column(db.Integer, nullable=False)
    Carbohydrates = db.Column(db.Integer, nullable=False)
    

class Dish(db.Model):
    ID_Dish = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    KCal = db.Column(db.Integer, nullable=False)
    PFC_ID = db.Column(db.Integer, db.ForeignKey('pfc.ID_PFC'), nullable=False)


class Eating(db.Model):
    ID_Eating = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)
    Eating_time = db.Column(db.Time, nullable=False)


class Eating_Dish(db.Model):
    ID_Eating_Dish = db.Column(db.Integer, primary_key=True)
    Eating_ID = db.Column(db.Integer, db.ForeignKey('eating.ID_Eating'), nullable=False)
    Dish_ID = db.Column(db.Integer, db.ForeignKey('dish.ID_Dish'), nullable=False)



class Diet_Eating(db.Model):
    ID_Diet_Eating = db.Column(db.Integer, primary_key=True)
    Eating_ID = db.Column(db.Integer, db.ForeignKey('eating.ID_Eating'), nullable=False)
    Diet_ID = db.Column(db.Integer, db.ForeignKey('diet.ID_Diet'), nullable=False)



class Person_workout(db.Model):
    ID_Person_workout = db.Column(Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)
    Description = db.Column(db.String(100), nullable=False)
    Client_id = db.Column(db.Integer, db.ForeignKey('client.ID_Client'), nullable=False)

class Person_workout_Exercise(db.Model):
    ID_Person_workout_exercise = db.Column(db.Integer, primary_key=True)
    Person_workout_id = db.Column(db.Integer, db.ForeignKey('person_workout.ID_Person_workout'), nullable=False)
    Exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.ID_Exercise'), nullable=False)

class Exercise(db.Model):
    ID_Exercise = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False, unique=True)
    Description = Column(String(100), nullable=False)
    Load_score = Column(Integer, nullable=False)
    Exercise_category_id = Column(Integer, ForeignKey('exercise_category.ID_Exercise_category'), nullable=False)
    Exercise_plan_id = Column(Integer, ForeignKey('exercise_plan.ID_Exercise_plan'), nullable=False)

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



#групповые тренировки и тренеры

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
    return {'message': 'Удалени категории групповой тренировки прошло успешно!'}


@app.route('/group_workout', methods=['POST'])
def add_group_workout():
    data = request.get_json()
    event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
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
        group_workout.Event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
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




@app.route('/client', methods=['POST'])
def add_client():
    data = request.get_json()
    id_user = data['id_user']
    growth = data['growth']
    weight = data['weight']
    age_person = data['age_person']
    client = Client(ID_Client=id_user, Growth=growth, Weight=weight, Age_person=age_person)
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'Клиент успешно добавлен!'})

@app.route('/client/<int:id>', methods=['PUT'])
def update_client(id):
    client = Client.query.get(id)
    if not client:
        return jsonify({'message': 'Клиент не найден!'})
    
    data = request.get_json()
    growth = data.get('growth')
    weight = data.get('weight')
    age_person = data.get('age_person')
    
    if growth is not None:
        client.Growth = growth
    if weight is not None:
        client.Weight = weight
    if age_person is not None:
        client.Age_person = age_person
    
    db.session.commit()
    return jsonify({'message': 'Данные клиента успешно обновлены!'})


@app.route('/client/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get(id)
    if not client:
        return jsonify({'message': 'Клиент не найден!'})
    
    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Клиент успешно удален!'})





@app.route('/feedback', methods=['POST'])
def add_feedback():
    data = request.get_json()
    message = data['message']
    client_id = data['client_id']
    feedback = Feedback_message(Message=message, Client_ID=client_id)
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'message': 'Отзыв добавлен успешно!'})



@app.route('/feedback/<int:id>', methods=['PUT'])
def update_feedback(id):
    feedback = Feedback_message.query.get_or_404(id)
    data = request.get_json()
    message = data['message']
    feedback.Message = message
    db.session.commit()
    return jsonify({'message': 'Отзыв успешно изменен!'})


@app.route('/feedback/<int:id>', methods=['DELETE'])
def delete_feedback(id):
    feedback = Feedback_message.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'message': 'Отзыв успешно удален!'})

from flask import jsonify

@app.route('/diet', methods=['GET'])
def get_diets():
    diets = Diet.query.all()
    result = []
    for diet in diets:
        diet_data = {
            'id': diet.ID_Diet,
            'name': diet.Name,
            'duration': diet.Duration,
            'category': diet.category.Name,
            'user_id': diet.User_ID,
            'created_date': diet.Created_date
        }
        result.append(diet_data)

    return jsonify({'diets': result})



@app.route('/diet_category', methods=['POST'])
def add_diet_category():
    data = request.get_json()
    name = data['name']
    diet_category = DietCategory(Name=name)
    db.session.add(diet_category)
    db.session.commit()
    return jsonify({'message': 'Добавление категории диеты прошло успешно!'})


@app.route('/diet_category/<int:id>', methods=['PUT'])
def update_diet_category(id):
    data = request.get_json()
    diet_category = DietCategory.query.get(id)
    if not diet_category:
        return jsonify({'message': 'Категория диеты не найдена!'}), 404
    diet_category.Name = data['name']
    db.session.commit()
    return jsonify({'message': 'Изменение категории диеты прошло успешно!'})


@app.route('/diet_category/<int:id>', methods=['DELETE'])
def delete_diet_category(id):
    diet_category = DietCategory.query.get(id)
    if not diet_category:
        return jsonify({'message': 'Категория диеты не найдена!'}), 404
    db.session.delete(diet_category)
    db.session.commit()
    return jsonify({'message': 'Удаление категории диеты прошло успешно!'})



@app.route('/diet', methods=['POST'])
def add_diet():
    data = request.get_json()
    name = data['name']
    duration = data['duration']
    diet_category_id = data['diet_category_id']
    user_id = data['user_id']
    diet = Diet(Name=name, Duration=duration, Diet_category_ID=diet_category_id, User_ID=user_id)
    db.session.add(diet)
    db.session.commit()
    return jsonify({'message': 'Добавление диеты прошло успешно!'})


@app.route('/diet/<int:id>', methods=['PUT'])
def update_diet(id):
    data = request.get_json()
    diet = Diet.query.get(id)
    if not diet:
        return jsonify({'message': 'Диета не найдена!'}), 404
    diet.Name = data['name']
    diet.Duration = data['duration']
    diet.Diet_category_ID = data['diet_category_id']
    diet.User_ID = data['user_id']
    db.session.commit()
    return jsonify({'message': 'Изменение диеты прошло успешно!'})


@app.route('/diet/<int:id>', methods=['DELETE'])
def delete_diet(id):
    diet = Diet.query.get(id)
    if not diet:
        return jsonify({'message': 'Диета не найдена!'}), 404
    db.session.delete(diet)
    db.session.commit()
    return jsonify({'message': 'Удаление диеты прошло успешно!'})




@app.route('/pfc', methods=['POST'])
def add_pfc():
    data = request.json
    new_pfc = PFC(
        Proteins=data['proteins'],
        Fats=data['fats'],
        Carbohydrates=data['carbohydrates']
    )
    db.session.add(new_pfc)
    db.session.commit()
    return jsonify({'message': 'PFC added successfully'})

@app.route('/pfc/<int:id>', methods=['PUT'])
def update_pfc(id):
    pfc = PFC.query.get(id)
    if not pfc:
        return jsonify({'message': 'PFC not found'})
    data = request.json
    pfc.Proteins = data['proteins']
    pfc.Fats = data['fats']
    pfc.Carbohydrates = data['carbohydrates']
    db.session.commit()
    return jsonify({'message': 'PFC updated successfully'})

@app.route('/pfc/<int:id>', methods=['DELETE'])
def delete_pfc(id):
    pfc = PFC.query.get(id)
    if not pfc:
        return jsonify({'message': 'PFC not found'})
    db.session.delete(pfc)
    db.session.commit()
    return jsonify({'message': 'PFC deleted successfully'})


@app.route('/pfc', methods=['GET'])
def get_all_pfc():
    pfcs = PFC.query.all()
    output = []
    for pfc in pfcs:
        pfc_data = {}
        pfc_data['id_pfc'] = pfc.ID_PFC
        pfc_data['proteins'] = pfc.Proteins
        pfc_data['fats'] = pfc.Fats
        pfc_data['carbohydrates'] = pfc.Carbohydrates
        output.append(pfc_data)
    return jsonify({'PFCs': output})



@app.route('/dish', methods=['POST'])
def add_dish():
    name = request.json['name']
    kcal = request.json['kcal']
    pfc_id = request.json['pfc_id']
    new_dish = Dish(Name=name, KCal=kcal, PFC_ID=pfc_id)
    db.session.add(new_dish)
    db.session.commit()
    return jsonify({'message': 'Блюдо успешно добавлено!'})

@app.route('/dish/<id>', methods=['PUT'])
def update_dish(id):
    dish = Dish.query.get(id)
    dish.Name = request.json['name']
    dish.KCal = request.json['kcal']
    dish.PFC_ID = request.json['pfc_id']
    db.session.commit()
    return jsonify({'message': 'Блюдо успешно изменено!'})

@app.route('/dish/<id>', methods=['DELETE'])
def delete_dish(id):
    dish = Dish.query.get(id)
    db.session.delete(dish)
    db.session.commit()
    return jsonify({'message': 'Блюдо успешно удалено!'})

@app.route('/dish', methods=['GET'])
def get_all_dishes():
    dishes = Dish.query.all()
    result = []
    for dish in dishes:
        pfc = PFC.query.get(dish.PFC_ID)
        dish_data = {
            'id': dish.ID_Dish,
            'name': dish.Name,
            'kcal': dish.KCal,
            'pfc': {
                'id': pfc.ID_PFC,
                'proteins': pfc.Proteins,
                'fats': pfc.Fats,
                'carbohydrates': pfc.Carbohydrates
            }
        }
        result.append(dish_data)
    return jsonify(result)


@app.route('/eating', methods=['POST'])
def add_eating():
    name = request.json.get('name')
    eating_time = request.json.get('eating_time')
    
    if not name or not eating_time:
        return jsonify({'error': 'Name and eating_time are required fields'}), 400
    
    new_eating = Eating(Name=name, Eating_time=eating_time)
    db.session.add(new_eating)
    db.session.commit()
    
    return jsonify({'message': 'New Eating has been created successfully!'}), 201


@app.route('/eating', methods=['GET'])
def get_all_eating():
    eating_list = []
    
    for eating in Eating.query.all():
        eating_list.append({
            'id': eating.ID_Eating,
            'name': eating.Name,
            'eating_time': str(eating.Eating_time)
        })
    
    return jsonify({'eatings': eating_list})

@app.route('/eating/<int:eating_id>', methods=['PUT'])
def update_eating(eating_id):
    eating = Eating.query.get(eating_id)
    
    if not eating:
        return jsonify({'error': 'Eating not found'}), 404
    
    name = request.json.get('name')
    eating_time = request.json.get('eating_time')
    
    if not name and not eating_time:
        return jsonify({'error': 'Name or eating_time should be provided'}), 400
    
    if name:
        eating.Name = name
        
    if eating_time:
        eating.Eating_time = eating_time
        
    db.session.commit()
    
    return jsonify({'message': 'Eating has been updated successfully!'})

@app.route('/eating/<int:eating_id>', methods=['DELETE'])
def delete_eating(eating_id):
    eating = Eating.query.get(eating_id)
    
    if not eating:
        return jsonify({'error': 'Eating not found'}), 404
    
    db.session.delete(eating)
    db.session.commit()
    
    return jsonify({'message': 'Eating has been deleted successfully!'})



@app.route('/eating_dish', methods=['POST'])
def add_eating_dish():
    data = request.get_json()
    new_eating_dish = Eating_Dish(Eating_ID=data['eating_id'], Dish_ID=data['dish_id'])
    db.session.add(new_eating_dish)
    db.session.commit()
    return jsonify({'message': 'New eating dish created!'})


@app.route('/eating_dish/<int:id>', methods=['PUT'])
def update_eating_dish(id):
    eating_dish = Eating_Dish.query.get(id)
    if not eating_dish:
        return jsonify({'message': 'Eating dish not found'})
    data = request.get_json()
    eating_dish.Eating_ID = data['eating_id']
    eating_dish.Dish_ID = data['dish_id']
    db.session.commit()
    return jsonify({'message': 'Eating dish updated successfully!'})

@app.route('/eating_dish/<int:id>', methods=['DELETE'])
def delete_eating_dish(id):
    eating_dish = Eating_Dish.query.get(id)
    if not eating_dish:
        return jsonify({'message': 'Eating dish not found'})
    db.session.delete(eating_dish)
    db.session.commit()
    return jsonify({'message': 'Eating dish deleted successfully!'})



@app.route('/diet_eating', methods=['GET'])
def get_all_diet_eatings():
    diet_eatings = Diet_Eating.query.all()
    output = []
    for diet_eating in diet_eatings:
        output.append({'ID_Diet_Eating': diet_eating.ID_Diet_Eating,
                       'Eating_ID': diet_eating.Eating_ID,
                       'Diet_ID': diet_eating.Diet_ID})
    return jsonify({'diet_eatings': output})


@app.route('/diet_eating', methods=['POST'])
def add_diet_eating():
    eating_id = request.json['eating_id']
    diet_id = request.json['diet_id']
    new_diet_eating = Diet_Eating(Eating_ID=eating_id, Diet_ID=diet_id)
    db.session.add(new_diet_eating)
    db.session.commit()
    return jsonify({'message': 'Diet Eating created successfully!'})

@app.route('/diet_eating/<int:diet_eating_id>', methods=['PUT'])
def update_diet_eating(diet_eating_id):
    diet_eating = Diet_Eating.query.filter_by(ID_Diet_Eating=diet_eating_id).first()
    if not diet_eating:
        return jsonify({'message': 'Diet Eating not found'}), 404
    eating_id = request.json['eating_id']
    diet_id = request.json['diet_id']
    diet_eating.Eating_ID = eating_id
    diet_eating.Diet_ID = diet_id
    db.session.commit()
    return jsonify({'message': 'Diet Eating updated successfully!'})


@app.route('/diet_eating/<int:diet_eating_id>', methods=['DELETE'])
def delete_diet_eating(diet_eating_id):
    diet_eating = Diet_Eating.query.filter_by(ID_Diet_Eating=diet_eating_id).first()
    if not diet_eating:
        return jsonify({'message': 'Diet Eating not found'}), 404
    db.session.delete(diet_eating)
    db.session.commit()
    return jsonify({'message': 'Diet Eating deleted successfully!'})



@app.route('/person_workout', methods=['POST'])
def add_person_workout():
    data = request.get_json()
    new_person_workout = Person_workout(Name=data['name'], Description=data['description'], Client_id=data['client_id'])
    db.session.add(new_person_workout)
    db.session.commit()
    return jsonify({'message': 'New person workout created!'})


@app.route('/person_workout/<int:id>', methods=['PUT'])
def update_person_workout(id):
    person_workout = Person_workout.query.get(id)
    if not person_workout:
        return jsonify({'message': 'Person workout not found!'}), 404
    data = request.get_json()
    person_workout.Name = data['name']
    person_workout.Description = data['description']
    person_workout.Client_id = data['client_id']
    db.session.commit()
    return jsonify({'message': 'Person workout updated!'})

@app.route('/person_workout/<int:id>', methods=['DELETE'])
def delete_person_workout(id):
    person_workout = Person_workout.query.get(id)
    if not person_workout:
        return jsonify({'message': 'Person workout not found!'}), 404
    db.session.delete(person_workout)
    db.session.commit()
    return jsonify({'message': 'Person workout deleted!'})


@app.route('/exercise', methods=['POST'])
def add_exercise():
    try:
        exercise_data = request.get_json()
        new_exercise = Exercise(
            Name=exercise_data['name'],
            Description=exercise_data['description'],
            Load_score=exercise_data['load_score'],
            Exercise_category_id=exercise_data['exercise_category_id'],
            Exercise_plan_id=exercise_data['exercise_plan_id']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return {'message': 'Exercise added successfully!'}
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
            return {'message': 'Exercise updated successfully!'}
        
        else:
            return {'message': 'Exercise not found.'}, 404
        
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
            return {'message': 'Exercise deleted successfully!'}
        else:
            return {'message': 'Exercise not found.'}, 404
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500




@app.route('/exercise_category', methods=['POST'])
def add_exercise_category():
    name = request.json['name']
    new_category = Exercise_category(Name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'New exercise category added successfully!'})

@app.route('/exercise_category/<int:id>', methods=['PUT'])
def update_exercise_category(id):
    category = Exercise_category.query.get_or_404(id)
    name = request.json['name']
    category.Name = name
    db.session.commit()
    return jsonify({'message': 'Exercise category updated successfully!'})


@app.route('/exercise_category/<int:id>', methods=['DELETE'])
def delete_exercise_category(id):
    category = Exercise_category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Exercise category deleted successfully!'})




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
    return jsonify({'message': 'New exercise plan added successfully!'})



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

    return jsonify({'message': 'Exercise plan updated successfully!'})




@app.route('/exercise_plan/<int:id>', methods=['DELETE'])
def delete_exercise_plan(id):
    plan = Exercise_plan.query.get_or_404(id)

    db.session.delete(plan)
    db.session.commit()

    return jsonify({'message': 'Exercise plan deleted successfully!'})




@app.route('/feedback_messages', methods=['GET'])
def get_feedback_messages():
    feedback_messages = Feedback_message.query.all()
    result = []
    for feedback_message in feedback_messages:
        client = Client.query.get(feedback_message.Client_ID)
        user = User.query.get(client.ID_Client)
        
        feedback_message_data = {
            'id': feedback_message.ID_Feedback_message,
            'message': feedback_message.Message,
            'create_date': feedback_message.Create_date,
            'client': {
                'user': {
                    'email': user.email,
                }
            }
        }
        result.append(feedback_message_data)
    return jsonify(result)


# @app.route('/feedback_messages', methods=['GET'])
# def get_feedback_messages():
#     feedback_messages = Feedback_message.query.all()
#     result = []
#     for feedback_message in feedback_messages:
#         client = Client.query.get(feedback_message.Client_ID)
        
#         feedback_message_data = {
#             'id': feedback_message.ID_Feedback_message,
#             'message': feedback_message.Message,
#             'create_date': feedback_message.Create_date,
#             'client': {
#                 'age_person': client.Age_person,
#             }
#         }
#         result.append(feedback_message_data)
#     return jsonify(result)


with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)