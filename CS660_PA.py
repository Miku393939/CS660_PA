import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

app = Flask(__name__)
app.secret_key = "bakakitty"
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'CS660_PA'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config["DEBUG"] = True
mysql.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM User")
users = cursor.fetchall()


class User(flask_login.UserMixin):
    pass

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@app.route('/')
def index():
    return render_template('index.html')

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

@app.route("/register/", methods = ['GET'])
def register():
    print("get!")
    return render_template("register.html")

# @app.route("/register", methods = ["POST"])
# def register_post():
#     registerUserName = request.form.get('username')
#     registerPassword = request.form.get('password')
#     cursor = conn.cursor()
#     #Need to add some more information
#     query = "Insert into User (email,password,FNAME,LNAME)" "VALUES ('{0}','{1}','WAR3','WAR4')".format(registerUserName,registerPassword)
#     #Need to add some more information
#     # query = "Insert into User (email,password) VALUES (%s,%s)", (registerUserName, registerPassword)
#     print(query)
#     cursor.execute(query)
#     conn.commit()
#     print("finished!")
#     return render_template("register.html")

@app.route("/register/", methods=['POST'])
def register_user():
    try:
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        password = request.form.get('password')
    except:
        print("register failed: couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)

    if test:
        print(cursor.execute("INSERT INTO User (fname,lname,email,dob,hometown,gender,password) "
                             "VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(fname, lname, email, dob,
                                                                                         hometown, gender, password)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        album_name = "Album of "+ fname + " " + lname   #set album name “Album of FirstName LastName”
        flask_login.login_user(user)

        uid = getUserIdFromEmail(flask_login.current_user.id)
        createDefaultAlbum(uid,album_name)#auto create the default album when user register

        # cursor.execute("INSERT INTO ALBUM (name,uid)""VALUES ('{0}','{1}')".format(album_name, uid))


        return render_template('index.html', name=fname, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return render_template("error.html")


def createDefaultAlbum(uid, album_name):
    query = "INSERT INTO ALBUM (name,uid)""VALUES ('{0}','{1}')".format(album_name, uid)
    print(query.format(uid))  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(uid))
    conn.commit()
    return

@app.route("/login/", methods = ["GET","POST"])
def login():
    if flask.request.method == 'GET':
        return render_template("login.html")
    email = flask.request.form['email']
    cursor = conn.cursor()
    query = "SELECT password FROM User WHERE email = '{0}'".format(email)
    # check if email is registered
    if cursor.execute(query):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('index'))

    # information did not match
    return "<a href='/login'>Try again</a>\
    			</br><a href='/register'>or make an account</a>"


@app.route('/friendship', methods=['POST'])
@flask_login.login_required
def friend_add():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    friend_uid = request.form.get('friend_id')
    cursor = conn.cursor()

    query = "INSERT INTO FRIENDSHIP (uid1,uid2)""VALUES ('{0}','{1}')".format(uid, friend_uid)
    cursor.execute(query)
    conn.commit()
    print("Added friend successfully")
    return flask.redirect(flask.url_for('index'))


@app.route('/friendship', methods=['GET'])
@flask_login.login_required
def friend():
    cursor = conn.cursor()
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor.execute("select email from user where uid in(select uid2 from friendship where uid1 = '{0}')".format(uid))
    friends_list = cursor.fetchall()
    return render_template("friendship.html",friends_list = friends_list)








@app.route('/upload/', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        #cursor.execute(
        #    "INSERT INTO Photo (imgdata, user_id, caption) VALUES ('photo_data', 'uid', 'caption')")
        cursor.execute("INSERT INTO Photo (data, uid, caption) VALUES (%s, %s, %s)",
                       (photo_data, uid, caption))
        #cursor.execute("INSERT INTO Photo (imgdata, user_id, caption) VALUES (?, ?, ?)", (photo_data, uid, caption))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')



def getUsersPhotos(uid):
    cursor = conn.cursor()

    cursor.execute("SELECT data, aid, caption FROM Photo WHERE user_id = 'uid'")
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT UID FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

@app.route('/Logout')
def logout():
    flask_login.logout_user()
    return render_template('index.html')






if __name__ == '__main__':
    app.run()
