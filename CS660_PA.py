import flask
from flask import Flask,  flash, Response, request, render_template, redirect, url_for
from os.path import abspath, realpath
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from werkzeug.utils import secure_filename

# for image uploading
# from werkzeug import secure_filename
import os, base64

app = Flask(__name__)
app.secret_key = "bakakitty"
mysql = MySQL()



app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Helloworld108'
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

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    cursor = conn.cursor()
    cursor.execute("SELECT p.PID, p.DATA, p.CAPTION, u.email FROM album as a"
                   " join photo as p on a.aid = p.aid"
                   " join user as u on a.uid = u.uid")
    pics = cursor.fetchall()
    return render_template('index.html', pics=pics)


@app.route("/register/", methods=['GET'])
def register():
    print("get!")
    return render_template("register.html")


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
        album_name = "Default"   #set album name “default”
        flask_login.login_user(user)

        uid = getUserIdFromEmail(flask_login.current_user.id)
        createDefaultAlbum(uid,album_name)#auto create the default album when user register

        # cursor.execute("INSERT INTO ALBUM (name,uid)""VALUES ('{0}','{1}')".format(album_name, uid))

        return render_template('index.html', name=fname, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return render_template("error.html")


@app.route("/login/", methods=["GET","POST"])
def login():
    if flask.request.method == 'GET':
        return render_template("login.html", msg="")
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

    return render_template("login.html", msg="Invalid credentials!!!")


@app.route("/createAlbum/", methods=["GET", "POST"])
def create_album():
    if flask.request.method == 'GET':
        return render_template("Album.html")
    aname = flask.request.form['name']
    cursor = conn.cursor()
    uid = getUserIdFromEmail(flask_login.current_user.id)
    query = "INSERT INTO Album(name,uid) VALUES ('{0}','{1}')".format(aname, uid)
    cursor.execute(query)
    conn.commit()
    return flask.redirect(flask.url_for("my_photo"))


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
    return render_template("friendship.html", friends_list=friends_list)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            caption = request.form.get('caption')
            aid = request.form.get('album')
            path= "/static/upload/"+filename

            cursor = conn.cursor()
            query = "INSERT INTO photo (caption,data,aid)""VALUES ('{0}','{1}','{2}')".format(caption, path, aid)
            cursor.execute(query)
            conn.commit()

            return redirect(url_for('my_photo'))

    else:
        albumlist = getUsersAlbumsid(getUserIdFromEmail(flask_login.current_user.id))
        alist = []
        for i in range(len(albumlist)):
            alist.append(albumlist[i])
        return render_template('upload.html', alist=alist)


@app.route('/MyPhoto')
def my_photo():
    current_user = flask_login.current_user
    if current_user.is_authenticated:
        albumlist = getUsersAlbums(getUserIdFromEmail(current_user.id))
        alist = []
        for i in range(len(albumlist)):
            alist.append(albumlist[i][0])
        return render_template('Photo.html', alist=alist)
    else:
        return render_template('login.html')


@app.route('/MyProfile')
def my_profile():
    current_user = flask_login.current_user

    if current_user.is_authenticated:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USER Where uid = '{0}'".format(getUserIdFromEmail(current_user.id)))
        profile = cursor.fetchall()
        profile = profile[0]
        msg = "Hello "+profile[6]+" !!!"

        return render_template('MyProfile.html', loggedin=True, msg=msg, profile=profile)
    else:
        msg = "Hello, you are not logged in yet!"
        return render_template('MyProfile.html', loggedin=False, msg=msg)



@app.route('/Logout')
def logout():
    flask_login.logout_user()
    return index()


def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name From album where uid ='{0}'".format(uid))
    return cursor.fetchall()

def getUsersAlbumsid(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name,aid From album where uid ='{0}'".format(uid))
    return cursor.fetchall()


def getUsersPhotos(uid):
    cursor = conn.cursor()

    cursor.execute("SELECT data, aid, caption FROM Photo WHERE user_id = 'uid'")
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT UID FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def createDefaultAlbum(uid, album_name):
    query = "INSERT INTO ALBUM (name,uid)""VALUES ('{0}','{1}')".format(album_name, uid)
    print(query.format(uid))  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(uid))
    conn.commit()
    return


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


if __name__ == '__main__':
    app.run()
