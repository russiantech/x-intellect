from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField
from wtforms.widgets import HiddenInput

from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from PIL import Image
import re, secrets , os

regex = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)"

cate_choice=[
    ('all','All'),  ('trend','Trending'),  ('new','New Courses'), ('data', 'Data & Data-science'), ('free','Free Courses'), 
    ('analytics','Analytics'),
    ('mobile dev','Moile Development'), ('hacking','Hacking'), ('cyber-security','Cyber Security'), ('programming','Programming'),
    ('web dev','Web Development'),('ml', 'Machine Learning'), ('softwares','Software Development'), ('js','Javascript'), ('basics','Beginner'), 
    ('advanced', 'Advanced'), ('ui-ux', 'UI/UX Designs'), ('marketing', 'Digital Marketing'), ('iot','Internet Of Things'), ('fullstack','Full Stack Development'), ('ai','Artificial Intelligence'), 
    ('py','Python'),  ('game','Game Development'), 
    ]
level_choice = [('','...Course Level....'), ('novice','Novice'), ('beginner','Beginner'), ('expert','Expert'),  ("pro",'Pro'), ("advanced",'Advanced') ]
lang_choice = [('','Course Language'), ('english','English'), ('french','French'), ('spanish','Spanish'), ('latin','Latin'), ('pidgin','Pidgin'), ('other','Other')]
duration_choice = [('','Course Duration'), ('hours','Hours'), ('days','Days'), ('weeks','Weeks'), ('months','Months'), ('years','Years')]

#as alternative to FileAllowed() I can also use this allowed_file()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in os.environ.get('ALLOWED_EXTENSIONS')

def validate_(form, model, row):
    if model.query.filter_by(row=form).first():
        raise ValidationError(f'This very {form} has already been saved with another course.')

class CourseForm(FlaskForm):
    title = StringField('Enter Course Title', validators=[DataRequired(), Length(min=2, max=50)])
    desc = TextAreaField('Course Introduction', validators=[DataRequired(), Length(min=10, max=300)])
    category = SelectField('Course Category', validators=[DataRequired()], choices=cate_choice)
    lang = SelectField('Course Language', choices=lang_choice)
    lev =SelectField('Course Level', choices=level_choice)
    tag = StringField('Tags')
    author = StringField('Instructor\'s Name/Username')
    #duration = IntegerField('Course Duration')
    duration =SelectField('Course Time', choices=duration_choice)
    #dynamic_select = SelectField("Choose an option", validate_choice=False) //skipping choice validations
    fee = IntegerField('Course Fee')

    submit = SubmitField('Next')

class MateriForm(FlaskForm):
    #poster = FileField('Add Course Poster Image', validators=[ DataRequired(), FileAllowed(os.environ.get('ALLOWED_EXTENSIONS'))])
    poster = FileField('Add Course Poster Image', validators=[FileAllowed(['txt', 'pdf', 'webp', 'png', 'jpg', 'jpeg', 'gif'])])
    video = FileField('Upload Tutorial Video', validators=[FileAllowed(['mp4', 'mkv', 'wmv', '3gp', 'f4v', 'avi', 'mp3'])])
    #material = FileField('Materials(Pdfs&Illustrations)', validators=[FileAllowed(os.environ.get('ALLOWED_EXTENSIONS'))])
    material = FileField('Materials(Pdfs&Illustrations)', validators=[FileAllowed(['txt', 'webp',  'pdf', 'png', 'jpg', 'jpeg', 'gif'])])
    
    submit = SubmitField('Next')

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)
            
    def savePoster(poster):
        random_hex = secrets.token_hex(5)
        _, f_ext = os.path.splitext(poster.filename)
        pstr = random_hex + f_ext
        #poster_path = os.path.join(current_app.root_path, 'static/img/posters', pstr)
        poster_path = os.path.join(os.environ.get('UPLOAD_FOLDER')+'posters', pstr)
        output_size = (375, 176)
        i = Image.open(poster)
        i.thumbnail(output_size)
        i.save(secure_filename(poster_path))
        return poster_path

    def saveMateri(materi):
        random_hex = secrets.token_hex(5)
        _, f_ext = os.path.splitext(materi.filename)
        materi = random_hex + f_ext 
        #poster_path = os.path.join(current_app.root_path, 'static/img/posters', pstr)
        materi_path = os.path.join(os.environ.get('UPLOAD_FOLDER')+'posters', materi)
        output_size = (375, 176)
        i = Image.open(materi)
        i.thumbnail(output_size)
        i.save(secure_filename(materi_path))
        return materi_path

    def saveVideo(video):
        random_hex = secrets.token_hex(5)
        _, f_ext = os.path.splitext(video.filename)
        video = random_hex + f_ext
        video_path = os.path.join(os.environ.get('UPLOAD_FOLDER')+'videos', video)
        i = Image.open(video)
        i.save(secure_filename(video_path))
        return video_path

class ChaptForm(FlaskForm):
    lesson = StringField('Lesson-Name', validators=[DataRequired(), Length(min=2, max=50)])
    chapt_desc = TextAreaField('Describe this lesson', validators=[Length(min=0, max=300)])
    #course = HiddenField('CourseID FK', validators=[ DataRequired(), Length(min=1, max=300)]) //added at point of saving to DB
    #submit = SubmitField('Next')

class ChaptFormBackups(FlaskForm):
    #lesson = HiddenField('Lesson-Name', validators=[DataRequired(), Length(min=2, max=50)])
    title = StringField('Add Topic/Heading', validators=[DataRequired(), Length(min=2, max=50)])
    desc = TextAreaField('Add Content For This Topic Here', validators=[DataRequired(), Length(min=10, max=300)])
    delta = HiddenField('delta', validators=[Length(0, 255)], )
    content_length = IntegerField( label='', validators=[ NumberRange(2, 255, "Heading") ], widget=HiddenInput() )
    submit = SubmitField('Next')

class TopicForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=2, max=50)])
    desc = TextAreaField('content', validators=[DataRequired(), Length(min=10, max=300)])
    submit = SubmitField('Next')
