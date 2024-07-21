from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required

from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError,InterfaceError, InvalidRequestError, )
from werkzeug.routing import BuildError

from web import db
from web.models import Course, Lesson, Topic, Tag, Category, User
from web.utils.save_image import saveP, saveM, saveV
from web.editor.forms import CourseForm , ChaptForm, MateriForm , TopicForm 

editor = Blueprint('editor', __name__)

@editor.route("/editor", methods=['GET', 'POST'])
@login_required
def course():
    form = CourseForm()
    if form.validate_on_submit():
        try:
            u = User.query.filter((User.id==form.author.data) | (User.id==1)).first()
            c = Category.query.filter_by(title=form.category.data).first() or Category(title=form.category.data)
            t = Tag.query.filter_by(id=form.tag.data).first() or Tag(name=form.tag.data)
                
            db.session.add(c)
            db.session.add(t)
        
            db.session.flush()
            db.session.commit()

            new_course = Course(title=form.title.data, lang=form.lang.data, desc=form.desc.data, level=form.lev.data, \
                                fee=form.fee.data, duration=form.duration.data, category=[c], ctag=[t], usr=[u] )
            new_course.slugify(form.title.data)
            #user.set_password(form.password.data)

            db.session.add(new_course)
            #db.session.refresh(new_course) //it cause not persistent error
            db.session.commit()
            
            flash('Your Course Has Been Created!', 'success')
            return redirect(url_for('editor.update', cid=new_course.id))
        except InvalidRequestError as e:
            db.session.rollback()
            flash(f"{form.data} -> {e} \n Something went wrong!", "danger")
        except IntegrityError as e:
            db.session.rollback()
            flash(f"->-> {e} \n\n\n Item Already exists!. Tips > Create Unique/New Values", "info")
        except DataError as e:
            db.session.rollback()
            flash(f"->-> {e} \n\n\n Invalid Entry", "warning")
        except InterfaceError as e:
            db.session.rollback()
            flash(f"->-> {e} \n\n\n Error connecting to the database", "danger")
        except DatabaseError as e:
            db.session.rollback()
            flash(f"->-> {e} \n\n\n Error connecting to the database", "danger")
        except BuildError as e:
            db.session.rollback()
            flash(f"->-> {e} \n\n\n An error occured !", "danger")
    return render_template("editor/course.html", form=form)

@editor.route("/editor/<int:cid>", methods=['GET', 'POST'])
@login_required
def update(cid):
    c = Course.query.get_or_404(cid)
    form = CourseForm()
    category = Category.query.filter_by(title=form.category.data).first() or Category(title=form.category.data)
    user = User.query.filter((User.id==form.author.data) | (User.id==1)).first()
    tag = Tag.query.filter_by(id=form.tag.data).first() or Tag(name=form.tag.data)
    if form.validate_on_submit():
        c.title = form.title.data
        c.lang = form.lang.data
        c.desc = form.desc.data
        c.level = form.lev.data
        c.fee = form.fee.data
        c.duration = form.duration.data
        c.category = [category]
        c.user = [user]
        c.tag = [tag]
        db.session.commit()
        flash(f'Success {form.title.data} updated!', 'success')
        return redirect(url_for("editor.materi", cid=c.id))
    elif request.method == 'GET':
        form.title.data = c.title
        form.lang.data = c.lang
        form.desc.data = c.desc
        form.lev.data = c.level
        form.fee.data = c.fee
        form.duration.data = c.duration
        form.category.data = c.category
        #form.author.data = [ c.usr.x for c.usr.x in c.author ] 
        form.author.data = [ x.email for x in c.author ] 
        form.tag.data = c.tag
    return render_template("editor/course.html", c = c, form=form)

#course_id
@editor.route("/editor/<cid>/materi", methods=['GET', 'POST'])
@login_required
def materi(cid): 
    course = Course.query.get_or_404(cid)

    form = MateriForm()
    if form.validate_on_submit():
        
        if form.poster.data  or form.material.data or form.video.data:

            m = saveM(form.material.data) or  course.material
            p = saveP(form.poster.data) or course.image
            v = saveV(form.video.data) or course.video
        
            course.image = p
            course.video = v
            course.material = m
            db.session.commit()
            flash('Your Course Has Been Updated!', 'success')
            #return redirect(f'/editor/{course.id}/lesson')
            return redirect(url_for('editor.lesson', cid=course.id))
    elif request.method == 'GET':
        form.poster.data = course.image
        form.video.data = course.video
        form.material.data = course.material

    return render_template('editor/materi.html', form=form, title=f'{course.title}')

#cid --add-lesson
@editor.route('/editor/<cid>/lesson', methods=['GET', 'POST'])
def lesson(cid):
    course = Course.query.get_or_404(cid)
    form = ChaptForm()
    if form.validate_on_submit():
        form = ChaptForm()
        #flash(form.lesson.data + form.chapt_desc.data)
        #u = User.query.filter((User.id==form.author.data) | (User.id==1)).first()
        chapta = Lesson(title=form.lesson.data, desc=form.chapt_desc.data, course=course.id)
        db.session.add(chapta)
        db.session.commit()
        flash(f'Another Lesson Added For {course.title}', 'success')
    return render_template('editor/lesson.html', form=form, course = course)

@editor.route("/editor/<int:cid>/<int:chaptid>/topic", methods=['GET', 'POST'])
def topic(cid, chaptid):
    form = TopicForm()
    Korse = db.session.query(Course, Lesson,).filter(Course.id == cid,).filter(Lesson.id == chaptid,).first()
    #chspt = Course.query.filter(Course.id == cid).first()
    chspt = Korse[0]
    abort(404) if not Korse else flash('Korse Found'), print(Korse)
           #remember-to-come-back-and-add-users/instructors-for-each-sections-perhaps!
    if form.validate_on_submit():
        #u = User.query.filter((User.id==form.author.data) | (User.id==1)).first()
        topick = Topic(title=form.title.data, desc=form.desc.data, course=Korse.Course.id, lesson=Korse.Lesson.id, )
        #->rmember backref 'chspt' from chapter-model-relationship-> (chspt=chspt), add this/fix keyError topiq
        
        db.session.add(topick)
        db.session.commit()
        flash(f'{Korse.Course.title} Course Has Been Created!', 'success')
        return redirect(request.referrer)
    return render_template('editor/topic.html', form=form, Korse = Korse)


@editor.route("/editor/<int:cid>/remove", methods=['POST'])
#@login_required
def remove(cid):
    course = Course.query.get_or_404(cid)
    if course.author != current_user:
        abort(403)
    db.session.delete(course)
    db.session.commit()
    flash('Your Course Has Been Removed!', 'success')
    return redirect(url_for('main.home'))


