from application import app, db, api
from flask import render_template, request, json, Response, flash, redirect, url_for, session, jsonify
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restplus import Resource


#################################################
## API ####

@api.route('/api','/api/')
class GetAndPost(Resource):

    #GET ALL
    def get(self):
        return jsonify(User.objects.all())
    
    #POST
    def post(self):
        postdata = api.payload
        new_user1 = User(userid=postdata['userid'], email=postdata['email'], first_name=postdata['first_name'], last_name=postdata['last_name'])
        new_user1.set_password(postdata['password'])
        new_user1.save()
        return jsonify(User.objects(userid=postdata['userid']))

    
    

@api.route('/api/<idx>')
class GetUpdateDelete(Resource):

    #GET ONE
    def get(self, idx):
        return jsonify(User.objects(userid=idx))

    #PUT
    def put(self, idx):
        data = api.payload
        User.objects(userid= idx).update(**data)
        return jsonify(User.objects(userid= idx))


    #DELETE    
    def delete(self, idx):
        User.objects(userid= idx).delete()
        return jsonify("User is Deleted!")


####################################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/courses/")
@app.route("/courses/<variable>")
def courses(variable="Spring 2019"):

    courseData = Course.objects.order_by("+courseID")

    # + assending order  and - decending order of the given fieldname  ....no order Course.objects.all()
    return render_template("courses.html", courseData = courseData, courses=True, variable = variable)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for("index"))
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        user_id = User.objects.count()
        user_id += 1

        first_name = registerform.first_name.data
        last_name = registerform.last_name.data
        email = registerform.email.data
        password = registerform.password.data

        new_user = User(userid=user_id, email=email, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        # flash("You Are Successfully Registered","success")
        return redirect(url_for("index"))

    return render_template("register.html", registerformtitle="New User Registration", registerform=registerform, register= True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        return redirect(url_for("index"))
    loginform = LoginForm()
    if loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data


        user = User.objects(email=email).first()
        #for hashed password check
        if user and user.get_password(password):
            # flash(f"{user.first_name}, You are Successfully logged in","success")
            session['userid'] = user.userid
            session['username'] = user.first_name
            return redirect(url_for("index"))
        else:
            # flash("Sorry, Something went wrong","danger")
            print("Sorry, Something went wrong")
    return render_template("login.html", loginformtitle="Login", loginform=loginform, login=True)

@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for("login"))
    #in get  method, use  request.args.get() and  in post method, use  request.form.get() or  request.form[] (must have some value) and methods=["GET", "POST"] in the route
    courseID = request.form.get('courseID')
    title = request.form.get('title')
    description = request.form.get('description')
    credits1 = request.form.get('credits')
    term1 = request.form.get('term1')
    userid = session.get('userid')
    if courseID:
        if Enrollment.objects(userid = userid, courseID = courseID):
            # flash(f"You are already enrolled in {title} course","danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(userid = userid, courseID = courseID).save()
            # flash(f"You are sucessfully enrolled in {title} course","success")


    classes = list( User.objects.aggregate(*[
        {
            '$lookup': {
            'from': 'enrollment', 
            'localField': 'userid', 
            'foreignField': 'userid', 
            'as': 'r1'
        }
        }, {
            '$unwind': {
            'path': '$r1', 
            'includeArrayIndex': 'r1_id', 
            'preserveNullAndEmptyArrays': False
        }
        }, {
           '$lookup': {
            'from': 'course', 
            'localField': 'r1.courseID', 
            'foreignField': 'courseID', 
            'as': 'r2'
        }
        }, {
           '$unwind': {
            'path': '$r2', 
            'preserveNullAndEmptyArrays': False
        }
        }, {
           '$match': {
            'userid': userid
        }
        }, {
            '$sort': {
            'courseID': 1
        }
        }
        ]))

    return render_template("enrollment.html", enrollment=True, templatetitle="Enrollment", classes=classes)


#API 
@app.route("/api/")
@app.route("/api/<idx>")
def api(idx=None):
    if (idx == None):
        jdata = courseData
    else:
        jdata = courseData[int(idx)]
    return Response(json.dumps(jdata), mimetype="application/json")






@app.route("/user")
def user():

    #User(user_id=1, first_name="Gaurab", last_name="Roy", email="gaurabroycse@gmail.com", password="123").save()
    #User(user_id=2, first_name="Swagoto", last_name="Sen", email="swagotosen@gmail.com", password="456").save()
    users = User.objects.all()
    return render_template("user.html", users=users)


@app.route("/logout")
def logout():
    session['userid']= False
    session.pop('username', None)
    return redirect(url_for("index"))






