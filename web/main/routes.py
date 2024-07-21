import logging
from flask import abort, current_app, flash, jsonify, render_template, Blueprint, request, url_for
from flask_login import current_user, login_required

from slugify import slugify
from sqlalchemy import asc, desc
from web.utils.decorators import enrollment_required
from web.utils.decorators import confirm_email

from web.models import db, Brand, User, Course, Lesson, Topic, Enrollment
from web.apis import course as test_course, user as test_user
from web.editor.forms import duration_choice

from web.extensions import mail

main = Blueprint('main', __name__)

""" # Download 'punkt' resource during app initialization
nltk.download('punkt', download_dir='path/to/your/nltk_data')
 """
# import nltk
# nltk.download('punkt')

#courses -> landing ->
#@main.route("/"), v->view
@main.route('/explore')
@main.route('/welcome/<int:offset>', methods=['post', 'get'])
@main.route('/welcome', methods=['post', 'get'])
def welcome(v=None):

    page = request.args.get('page', 1, type=int)

    match v:
        case 'latest':
            course = Course.query.order_by(Course.created.desc()).paginate(page=page, per_page=8)
        case 'oldest':
            course = Course.query.order_by(Course.created.asc()).paginate(page=page, per_page=8)
        case 'asc':
            course = Course.query.order_by(Course.title.asc()).paginate(page=page, per_page=8)
        case 'desc':
            course = Course.query.order_by(Course.title.desc()).paginate(page=page, per_page=8)
        case 'cat':
            cat = v.cat
            course = Course.query.filter(Course.cat.in_([c for c in cat]) ).all()
        case 'time':
            time = v.time
            course = Course.query.filter(Course.duration.in_([ t for t in time]) ).all()
        case 'price':
            min = v.min
            max = v.max
            course = Course.query.filter(Course.price >= min).filter(Course.price <= max) or \
                Course.query.filter(Course.price.in_(range(min, max)) ).all()
        case 'kword':
            kword = v.kword
            course = Course.query.msearch(kword, fields=['title','desc'] , limit=8)
        case 'rate':
            rate = v.rate
            course = Course.query.filter(Course.rating >= rate).all()
        case 'more':
            course = Course.query.order_by(Course.id.asc()).offset(5).all()
        case _:
            all = Course.query.all()
            course = all[0 : 4]
            total = len(all)
        
    brand = Brand.query.filter_by(id=2).first()

    context = { 
        'brand': brand, 
        'course': course, 
        'total' : total,
        'time' : duration_choice }

    return render_template("welcome/welcome.html", **context)

@main.route("/us")
def us():
    brand = Brand.query.filter_by(id=2).first()
    support_amount = "30, 40, 50, 70, 80, 90, 100, 200, 300, 400, 500"
    support_interval = "daily, weekly, monthly, quarterly, yearly"
    context = {
        "brand":brand, 
        "title" :'Us . Intellect',
        "support_amount" : support_amount, 
        "support_interval" : support_interval, 
    }
    return render_template('welcome/us.html', **context)

""" @main.route("/")
def us():
    brand = Brand.query.filter_by(id=2).first()
    return render_template('welcome/us.html', brand=brand, title='Intellect')
 """
 
@main.route("/")
@login_required
#@confirm_email
def user():

    # Get the current user
    user = User.query.get(current_user.id)

    # Fetch all enrollments of the user
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()

    # Prepare the response data
    response_data = []

    for enrollment in enrollments:
        # Get the course associated with the enrollment
        course = enrollment.course

        # Calculate the completion percentage for the course
        completion_percentage = course.calculate_completion_percentage(user)

        # Serialize the course data
        serialized_course = course.serialize(include_only=['title', 'image', 'slug'])

        # Add completion percentage to the serialized course data
        serialized_course['progress'] = completion_percentage
        serialized_course['percent_complete'] = completion_percentage

        # Append the serialized course to the response data
        response_data.append(serialized_course)

    # Return the response as JSON
    progress_data = response_data
    #print(progress_data)
    context = {
        'rater' :  test_course.rater, 
        'progress': test_user.progress,
        'badger' : test_user.badger, 
        'badge' : test_user.badge, 
        'time' : test_user.time, 
        'recomend' : test_user.recomend,
        'progress_data': progress_data
    }

    return render_template('index.html', **context )

@main.route('/explore')
def explore():
    course = Course.query.all()
    brand = Brand.query.filter_by(id=2).first()
    return render_template("courses/explore.html", brand=brand, course=course, data = course.courses)

#-> Preview Here
@main.route('/prev_/<string:slug>')
def prev_(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    course.views += 1
    db.session.commit()

    topiq = Topic.query.filter(Topic.course_id == course.id).first()

    #return f'{course.__dict__}'

    context = {
        'course': course,
        'topiq': topiq.title if topiq else '0-topic',
        #'data': course.__dict__  # Convert Course object to a dictionary
        'data': test_course.course_data  
    }
    #print(context['data'])
    return render_template('courses/prev.html', **context)

@main.route('/learn_/<string:slug>')
def learn_(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    _chapt = [c for c in course.lesson]
    _topiq = [ t for t in course.topic]
    context = {
        '_chapt': _chapt, '_topic':_topiq,
        'data': course,
    }

    return render_template("courses/learn3.html", **context)

@main.route("/blog")
def blog():
    return render_template('blog.html')

@main.route('/school')
@login_required
#@confirm_email
def school():
    return render_template("school.html")

#quiz
@main.route('/quiz')
@login_required
#@confirm_email
def quiz():
    return render_template("quiz/quiz.html")
    
@main.route('/qdetail', defaults={'one':'one'})
@main.route('/qdetail/<string:one>', defaults={'one':'one'})
@login_required
#@confirm_email
def qdetails(one):
    return render_template("quiz/qdetail.html")

@main.route('/qresult')
@login_required
#@confirm_email
def qresult():
    return render_template("quiz/qresult.html")

#path
@main.route('/paths')
@login_required
#@confirm_email
def path():
    return render_template("path/path.html")

@main.route('/path', defaults={'one':'one'})
@main.route('/path-of/<string:one>', defaults={'one':'one'})
@login_required
#@confirm_email
def path_of(one):
    return render_template("path/path-of.html")


#instructors
@main.route('/tutors')
@login_required
#@confirm_email
def tutor_list():
    return render_template("instructor/tutors.html", tutors = 't')

@main.route('/tutor', defaults={'t':'t'})
@main.route('/tutor/<string:t>', defaults={'t':'t'})
@login_required
#@confirm_email
def tut(t):
    return render_template("instructor/tutor.html", tutor = tutor.info )

@main.route('/play')
@login_required
#@confirm_email
def player():
    return render_template("misc/play.html")

@main.route('/materi')
@login_required
#@confirm_email
def materi():
    return render_template("misc/material.html")

@main.route('/syllabus')
@login_required
#@confirm_email
def syllabus():
    return render_template("misc/syllabus.html")

@main.route('/../json/search.json')
@main.route('/json/search.json')
def search():
    r = [
    {
        "title": "settings",
        "url": f"/{current_user.username}/update" if current_user.is_authenticated else url_for('auth.signin')
    },
    {
        "title": "dashboards > elearning",
        "url": "/"
    },
    {
        "title": "dashboards > School",
        "url": "/school"
    },
    ]
  
    c = Course.query.all() 
    return jsonify([ { 'label': c.title, 'url': url_for('main.prev', slug=str(c.slug) ) } for c in c] ) 

""" ========================================================================== """

# Actual learning interface
#-> Preview Here
@main.route('/prev/<string:slug>')
def prev(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    course.views += 1
    db.session.commit()

    return render_template('xcourse/prev.html')

@main.route('/learn/<string:slug>')
@login_required
@enrollment_required
def learn(slug):
    return render_template("xcourse/learn.html")

# Course insertion interface
@main.route('/x-insert')
def x_insert():
    return render_template("xcourse/x_insert.html")

# Course update interface
@main.route('/x-update')
def x_update():
    return render_template("xcourse/x_update.html")

# Lesson insertion interface
@main.route('/x-insert/lesson')
def x_insert_lesson():
    return render_template("xcourse/x_insert_lesson.html")

# Lesson update interface
@main.route('/x-update/lesson')
def x_update_lesson():
    return render_template("xcourse/x_update_lesson.html")

# Topic insertion interface
@main.route('/x-insert/topic')
def x_insert_topic():
    return render_template("xcourse/x_insert_topic.html")

# Topic update interface
@main.route('/x-update/topic')
def x_update_topic():
    return render_template("xcourse/x_update_topic.html")



import os
import psycopg2

# Function to execute SQL script against the database
def execute_sql_script(sql_script):
    try:
        # Connect to your PostgreSQL database
        """ conn = psycopg2.connect(
            host="localhost",
            database="russiant",
            user="root",
            password=""
        ) """

        conn = psycopg2.connect(
            host="dpg-co72lev109ks73816rcg-a",
            database="intellect",
            user="techa",
            password="RLJpQdUmIOvDXBu0oubBWGMGN5auYbtx"
        )
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute the SQL script
        cursor.execute(sql_script)
        
        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        return 'SQL script executed successfully'
    except Exception as e:
        return f'Error executing SQL script: {str(e)}'

# Route for executing SQL script from a file
@main.route('/execute_sql', methods=['POST', 'GET'])
def execute_sql_from_file():
    try:
        # Specify the directory where the .sql file is located
        sql_file_path = './intellect.sql'

        # Check if the file exists
        if not os.path.exists(sql_file_path):
            return f'SQL file not found at -> {sql_file_path}'

        # Read the contents of the file
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        # Execute SQL script against the database
        return execute_sql_script(sql_script)
    except Exception as e:
        return f'Error executing SQL script from file: {str(e)}'


