
#from itsdangerous.url_safe import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
import json , time 
from datetime import datetime, timedelta
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
#from itsdangerous import TimedSerializer as Serializer
from flask_login import UserMixin, current_user
#from flask_security import RoleMixin
from sqlalchemy.sql import func
from flask import current_app
import jwt

from slugify import slugify
#from web.chatme.routes import messages

# from web import db, s_manager

Base = declarative_base()
metadata = Base.metadata

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_login import LoginManager
s_manager = LoginManager()

s_manager.login_view = 'auth.signin'
@s_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@s_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#associations <according to bluehost,best-practice is to use is to use a table instead of a database model. db.table()
course_tag_association = db.Table('course_tag_association',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    )

user_course_association = db.Table('user_course_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    )

user_role_association = db.Table(
    'user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    keep_existing=True
)

category_course_association = db.Table('category_course_association',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

# Association table to track completion status of topics for each user
user_topic_progress = db.Table('user_topic_progress',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True),
    db.Column('completed', db.Boolean, default=False)
)

class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    type = db.Column(db.String(100), unique=True, nullable=False, default='a.i & data')
    name = db.Column(db.String(100), unique=True, nullable=False, default='Techa')
    email = db.Column(db.String(100), unique=True, index=True, nullable=False, default='techa@tech.com')
    phone = db.Column(db.String(20), index=True, default='08038958645')
    image = db.Column(db.String(1000))
    title = db.Column(db.String(50))
    logo = db.Column(db.String(50))  
    city = db.Column(db.String(50))
    lang = db.Column(db.String(100))
    us = db.Column(db.String(1000))
    ceo = db.Column(db.String(500))
    hype = db.Column(db.String(10000))  #slogan
    socials = db.Column(db.JSON) #brand.socials = { 'fb': '@russiantechnoloies', 'twitter': '@russiantechnoloies', 'linkedin': '@russiantechnoloies' }
    tutors = db.Column(db.Integer) 
    ratings = db.Column(db.Integer)
    reviews = db.Column(db.Integer)
    bank = db.Column(db.String(100), default='fcmb')
    acct = db.Column(db.Integer, default=5913408010)
    verified = db.Column(db.Boolean(), default=False)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), index=True)
    username = db.Column(db.String(100), index=True, nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)  #str type recommended bcos they're not meant for calculations
    password = db.Column(db.String(500), index=True, nullable=False)
    image = db.Column(db.String(1000), default='default.svg')
    title = db.Column(db.String(50))
    gender = db.Column(db.Text())  # ['male','female','other']
    city = db.Column(db.String(50))
    lang = db.Column(db.String(100))
    about = db.Column(db.String(5000))
    socials = db.Column(db.JSON) # socials: { 'fb': '@chrisjsm', 'insta': '@chris', 'twit': '@chris','linkedin': '', 'whats':'@techa' }
    #type = db.Column(db.Enum('0', '1', '2'), default='2')  # ['admin','tutor','student']
    # instructors
    duration = db.Column(db.Integer(), default=72)  # hours per week
    education = db.Column(db.String(100))
    course_count = db.Column(db.Integer) # course count for instructor
    comment_count = db.Column(db.Integer) # comment count for instructor
    trainee = db.Column(db.Integer)  
    ratings = db.Column(db.Integer)
    reviews = db.Column(db.Integer)
    # students

    ip = db.Column(db.String(50))
    verified = db.Column(db.Boolean(), default=False)  # verified or not(users)
    graduated = db.Column(db.Boolean(), default=False)

    bank = db.Column(db.Integer)
    online = db.Column(db.Boolean(), default=False)  # 1-online, 0-offline
    last_seen = db.Column(db.DateTime)

    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    topic_progress = db.relationship('Topic', secondary=user_topic_progress, backref=db.backref('users', lazy=True))

    payments = db.relationship("Payment", backref="user", lazy=True)  # Payment->course

    roles = db.relationship('Role', secondary=user_role_association, back_populates='users', lazy='dynamic')
    course = db.relationship('Course', secondary=user_course_association, back_populates='user', lazy=True)  # user->course(many-many) // backref='user',
    feedback = db.relationship("Feedback", backref='author', lazy=True)  # feedback->user

    chat = db.relationship('Chat', foreign_keys='Chat._from', backref='user', lazy='dynamic')

    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='author', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)
    
    def is_admin(self):
        return 'admin' in [ r.type for r in self.roles ]
    
    def not_admin(self):
        return not self.is_admin()
    
    # ...
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()
    
    def messages(self):
        #msg = Message.query.filter_by(or_(recipient=self, author=self)).distinct()
        return self.messages_sent and self.messages_received
    @property
    def course_count(self):
        '''Return Course count'''
        return Course.query.filter(Course.user == self.id).count()

    def count_unread(self):
        last_seen = self.last_seen or datetime.date(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.created > last_seen).count()

    def notify(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    #modified to specify types so that this single function can be used for different tokens
    # -> ['reset', 'verify', or 'confirm']
    def generate_token(self, exp=600, type='reset'):
        return jwt.encode({'user_id': self.id, 'exp': time.time() + exp, 'type': type }, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
            user = User.query.get(user_id)
            type = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['type']
        except:
            return
        return user, type

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.image}')"

#class Role(db.Model, RoleMixin):
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), unique=True)
    users = db.relationship('User', secondary=user_role_association, back_populates='roles')  # Use 'users' instead of 'user'
    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    tx_id = db.Column(db.String(100))
    tx_status = db.Column(db.String(100))
    tx_ref = db.Column(db.String(100))
    tx_amount = db.Column(db.Integer())
    currency = db.Column(db.String(100)) #['dollar, naira etc]
    provider = db.Column(db.String(100)) #['dollar, naira etc]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id') )

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    title = db.Column(db.String(45), unique=True, nullable=False)
    desc = db.Column(db.String(100), unique=True)
    image = db.Column(db.String(50))
    slug = db.Column(db.String(130))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def slugify(self, title):
        slug = title.lower()
        self.slug = slugify(slug)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    rating = db.Column(db.Float)
    views = db.Column(db.Integer)
    purchase = db.Column(db.Boolean)
    like = db.Column(db.Boolean)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    is_enrolled = db.Column(db.Boolean)

class Course(db.Model):
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.png')
    title = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.Text)
    video = db.Column(db.String(1000))
    material = db.Column(db.String(100))
    fee = db.Column(db.Integer)
    lang = db.Column(db.String(50), default='en')
    duration = db.Column(db.String(50), default='weeks') #['hours', 'days', 'weeks', 'months', 'years' ]
    level = db.Column(db.String(50), default='pro') # ['Novice',"Beginner","Pro/professional", 'Expert', 'advanced']
    views = db.Column(db.Integer, nullable=True, default=0) # count views
    comment = db.Column(db.Integer, nullable=True)  # comment count
    rating = db.Column(db.Integer, nullable=True)  # ratings count 

    completedby = db.Column(db.Integer, nullable=True)  # count those that complete d course
    status = db.Column(db.String(100), default='published')  # ['published','unpublished','pending']
    slug = db.Column(db.String(50))
    user = db.relationship('User', secondary=user_course_association, back_populates='course')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', secondary=category_course_association, backref=db.backref('course', lazy='dynamic'), lazy='dynamic')
    payment = db.relationship("Payment", backref="course", lazy=True)  # Payment->course
    lessons = db.relationship("Lesson", back_populates="course", lazy=True)  # lesson->course
    topics = db.relationship("Topic", backref="course", lazy=True)  # Topic->course
    feedback = db.relationship("Feedback", backref="course", lazy=True)  # feedback->course
    tags = db.relationship('Tag', secondary=course_tag_association, back_populates='course')

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def calculate_completion_percentage_bak(self, user):
        # Find the enrollment for the user and course
        enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=self.id).first()
        if enrollment:
            # Get the total number of topics in the course
            total_topics = len(self.topics)
            # Query the user_topic_progress table to count the completed topics for the user and course
            completed_topics_count = db.session.query(func.count()).filter(
                user_topic_progress.c.user_id == user.id,
                user_topic_progress.c.topic_id.in_([topic.id for topic in self.topics]),
                #user_topic_progress.c.completed == True #remove/comment-out this bcos there's no completed attribute in user_topic_progress
            ).scalar()
            # Calculate the completion percentage
            return (completed_topics_count / total_topics) * 100 if total_topics > 0 else 0
        return 0

    def calculate_completion_percentage(self, user):
        # Find the enrollment for the user and course
        enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=self.id).first()
        if enrollment:
            # Get the total number of topics in the course
            total_topics = len(self.topics)
            # Query the user_topic_progress table to count the completed topics for the user and course
            completed_topics_count = db.session.query(func.count()).filter(
                user_topic_progress.c.user_id == user.id,
                user_topic_progress.c.topic_id.in_([topic.id for topic in self.topics]),
            ).scalar()
            # Calculate the completion percentage and round it to the nearest whole number
            completion_percentage = round((completed_topics_count / total_topics) * 100) if total_topics > 0 else 0
            return completion_percentage
        return 0

    def serialize(
        self, include_only=None, include_lessons=False, include_topics=False, include_topic_desc=False, current_user=None
        ):
        """Serialize the Course object by dynamically accessing the specified attributes."""
        try:
            if include_only is None:
                include_only = ['id', 'category_id', 'image', 'title', 'desc', 'comment', 'rating', 'fee', 'level', 'rating', 'views', 'duration', 'created', 'slug']

            data = {x: getattr(self, x) for x in include_only}

            data['desc'] = json.loads(self.desc) if self.desc and 'desc' in include_only else None

            # Check if lessons should be included
            if include_lessons:
                # Fetch lessons related to the course
                lessons = [lesson.serialize() for lesson in self.lessons]
                data['lessons'] = lessons
                data['lessons_count'] = len(lessons)

                # Check if topics should be included
                if include_topics:
                    # Fetch topics related to each lesson
                    for lesson in lessons:
                        if 'topics' in lesson and isinstance(lesson['topics'], list) and lesson['topics'] is not None:
                            topics = [topic.serialize() for topic in lesson['topics'] if topic.lesson_id == lesson['id']]
                            lesson['topics'] = topics

            # Check if current_user is provided and add is_enrolled field
            """ if current_user:
                enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=self.id).first()
                payment = Payment.query.filter_by(user_id=current_user.id, course_id=self.id, tx_status='successful').first()
                data['is_enrolled'] = enrollment is not None and payment is not None """
            
            # Check if current_user is provided and add is_enrolled field
            if current_user and current_user.is_authenticated:
                enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=self.id).first()
                payment = Payment.query.filter_by(user_id=current_user.id, course_id=self.id, tx_status='successful').first()
                data['is_enrolled'] = enrollment is not None and payment is not None
            else:
                # If the user is not authenticated, set is_enrolled to False
                data['is_enrolled'] = False


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data['desc'] = None

        return data

    def serialize_bak(self, include_lessons=False, include_topics=False, include_topic_desc=False, current_user=None):
        """Serialize the Course object by dynamically accessing the specified attributes."""
        try:
            included_only = ['id', 'category_id', 'image', 'title', 'comment', 'rating', 'fee', 'level', 'rating', 'views', 'duration', 'created', 'slug']
            data = {x: getattr(self, x) for x in included_only}
            data['desc'] = json.loads(self.desc) if self.desc else None

            # Check if lessons should be included
            if include_lessons:
                # Fetch lessons related to the course
                lessons = [lesson.serialize() for lesson in self.lessons]
                data['lessons'] = lessons
                data['lessons_count'] = len(lessons)

                # Check if topics should be included
                if include_topics:
                    # Fetch topics related to each lesson
                    for lesson in lessons:
                        if 'topics' in lesson and isinstance(lesson['topics'], list) and lesson['topics'] is not None:
                            topics = [topic.serialize() for topic in lesson['topics'] if topic.lesson_id == lesson['id']]
                            lesson['topics'] = topics

            # Check if current_user is provided and add is_enrolled field
            if current_user:
                enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=self.id).first()
                payment = Payment.query.filter_by(user_id=current_user.id, course_id=self.id, tx_status='successful').first()
                data['is_enrolled'] = enrollment is not None and payment is not None

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data['desc'] = None

        return data

class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.png')
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    video = db.Column(db.String(1000))
    material = db.Column(db.String(100))
    fee = db.Column(db.Integer) # optional for chapters
    lang = db.Column(db.String(100), default='en')  #['english','spanish','french','arab','pidgin','chinese']
    duration = db.Column(db.Integer)
    slug = db.Column(db.String(130))

    topics = db.relationship("Topic", back_populates="lessons", lazy=True)  # lesson->course
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # instructor->chapters->foreign-key

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', back_populates='lessons', lazy=True)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def serialize(self):
        """ I use getattr(self, x) to dynamically access the attributes of the lesson object based on the names specified in the included_only list. Returning a dict containing only the specified attributes of the lesson object. """
        try:
            included_only = ['id', 'title', 'topics', 'slug']
            data = { 
                x: getattr(self, x) for x in included_only
            }

            data['desc'] =  json.loads(self.desc) if self.desc else None

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data['desc'] = None

        return data

        
    #DON'T FORET backref 'course' from Course Model when inserting data, even for all others

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.png')
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    video = db.Column(db.String(1000))
    material = db.Column(db.String(100))
    duration = db.Column(db.DateTime(timezone=True))
    slug = db.Column(db.String(130))

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # lesson->course->foreign-key

    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    lessons = db.relationship('Lesson', back_populates = 'topics', lazy=True)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def serialize(self, include_desc=False):
        """ I use getattr(self, x) to dynamically access the attributes of the lesson object based 
        on the names specified in the included_only list. Returning a dict containing only the specified attributes of the lesson object. """
        try:
            included_only = ['id','image', 'title', 'slug', 'lesson_id']
            data = {x: getattr(self, x) for x in included_only}
            """ print(include_desc)
            print(self.desc) """
            data['course_slug'] = self.lessons.course.slug
            # Conditionally include desc if it's not empty and include_desc is True
            if include_desc and self.desc:
                data['desc'] =  json.loads(self.desc) if self.desc else None
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data['desc'] = None
        
        return data

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    descr = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    topic = db.relationship('Topic', backref=db.backref('contents', lazy=True))

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completed_topics = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

"""
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    step = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False)

    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    lesson = db.relationship('Lesson', backref=db.backref('topics', lazy=True))
 
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref=db.backref('lessons', lazy=True))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
 """

class Badge(db.Model):
    __tablename__ = 'badge'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    level = db.Column(db.Integer)
    icon = db.Column(db.String(100))
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # student-Fk
    course = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # course Fk

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    rating = db.Column(db.Integer)  # ranges from 1(worst) to 5(best)
    comment = db.Column(db.Text)  # comment/feed-back texts
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # user->feedback
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # user->course

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    course = db.relationship('Course', secondary=course_tag_association, back_populates='tags')
    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f'<Tag "{self.name}">' 

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    is_seen = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return '<Message {}>'.format(self.body)
    # Remember to define the relationship between the `Message` and `User` models.

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True, nullable=False)
    _from = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _text = db.Column(db.String(140))
    _media = db.Column(db.String(140))
    _sticker = db.Column(db.String(140))
    _from_del = db.Column(db.Boolean(), default=False, nullable=False)
    _to_del = db.Column(db.Boolean(), default=False, nullable=False)
    _seen = db.Column(db.Boolean(), default=False, nullable=False)
    
    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return '<Message {}>'.format(self._text)
    # Remember to define the relationship between the `Message` and `User` models.

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #timestamp = db.Column(db.Float, index=True, default=func.now())
    payload_json = db.Column(db.Text)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    active =  db.Column(db.Boolean(), default=True)

    def get_data(self):
        return json.loads(str(self.payload_json))
#user_datastore = SQLAlchemyUserDatastore(db, User, Role)


