#data = Course.query.filter().all()

def badger(level):
    match level:
        case 1:
            return '1.svg'
        case 2:
            return '2.svg'
        case 3:
            return '3.svg'
        case 4:
            return '4.svg'
        case _:
            return '0.svg'


#check if student started-learning-or-not
progr = False
if progr:
        progress = {
        "1": {
            "icon" : 'course-1.webp',
            "level" : 77,
            "course": "React Web Developer Course"
        },
        "2":{
            "icon" : 'course-2.webp',
            "level" : 100,
            "course": "Python: From Zero to Expert"
            },
        "3":{
            "icon" : 'course-3.webp',
            "level" : 15,
            "course": "Learn and Understand NodeJS"
            },
        '4': {
            "icon" : 'course-4.webp',
            "level" : 47,
            "course": "Getting Started with Gulpjs"
            },
        '5': {
            "icon" : 'course-1.webp',
            "level" : 63,
            "course": "HTML 5 - The Complete Guide"
            }
            }
else:
        progress = {
        "1": {
            "icon" : 'empty.svg',
            "level" : 0,
            "course": "As You Begin Learning, Your Progress Will Be Tracked Here"
        },
        "2":{
            "icon" : 'empty.svg',
            "level" : 0,
            "course": "Browse Courses Now"
            },
        "3":{
            "icon" : 'empty.svg',
            "level" : 0,
            "course": "Choose A Course & We're Ready To Support You"
            },
        '4': {
            "icon" : 'empty.svg',
            "level" : 0.00,
            "course": "Learn From Experts Today!"
            },
        '5': {
            "icon" : 'empty.svg',
            "level" : 0,
            "course": "We Are Rusian Technologies"
            }
            }

        
badge = {
    "1": {
        "icon" : 'course-1.webp',
        "level" : 1,
        "course": "Javascript novice"
    },
    "2":{
        "icon" : 'course-2.webp',
        "level" : 2,
        "course": "Python: From Zero to Expert"
        },
    "3":{
        "icon" : 'course-3.webp',
        "level" : 3,
        "course": "Learn and Understand NodeJS"
        },
    '4': {
        "icon" : 'course-5.webp',
        "level" : 4,
        "course": "Getting Started with Gulpjs"
        },
    '5': {
        "icon" : 'course-4.webp',
        "level" : 5,
        "course": "HTML 5 - The Complete Guide"
        }
        }

badge = {
    "1": {
        "icon" : '0.svg',
        "level" : 0,
        "course": "Track Your Archievements Here"
    },
    "2":{
        "icon" : '0.svg',
        "level" : 0,
        "course": "See Recommendations"
        },
    "3":{
        "icon" : '0.svg',
        "level" : 0,
        "course": "Start Archieving Now"
        },
    '4': {
        "icon" : '0.svg',
        "level" : 0,
        "course": "No Archievement Yet"
        },
    '5': {
        "icon" : '0.svg',
        "level" : 0,
        "course": "You're Just One Click Away"
        }
        }


time = {
'labels' : ['React', 'Python', 'FastAPI'],
'icons':['loaf', 'cupcake', 'burger'],
'data':[780, 475, 450]
}

recomend = {
        "title": "Complete Web Developer Zero to Mastery",
        "intro": "Learn to build scalable & responsive web sites and applications with the latest technologies..",
        "photo": "cta-standard-3.webp",
        "fee": 37.20,
        "rating": 5,
        "count_rating":867
}