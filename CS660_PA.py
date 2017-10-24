from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

app = Flask(__name__)
app.secret_key = "bakakitty"
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'war0623'
app.config['MYSQL_DATABASE_DB'] = 'CS660_PA'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config["DEBUG"] = True
mysql.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass



conn = mysql.connect()
cursor = conn.cursor()
# query = 'select * from USER'
# cursor.execute(query)
# data = []
# for item in cursor:
#     data.append(item)

# print(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods = ["GET"])
def register():
    print("get!")
    return render_template("register.html")

@app.route("/register", methods = ["POST"])
def register_post():
    registerUserName = request.form.get('username')
    registerPassword = request.form.get('password')
    cursor = conn.cursor()
    #Need to add some more information
    query = "Insert into User (email,password,FNAME,LNAME)" "VALUES ('{0}','{1}','WAR1','WAR2')".format(registerUserName,registerPassword)
    #Need to add some more information
    # query = "Insert into User (email,password) VALUES (%s,%s)", (registerUserName, registerPassword)
    print(query)
    cursor.execute(query)
    conn.commit()
    print("finished!")
    return render_template("index.html")

@app.route("/login", methods = ["GET"])
def login():
    return render_template("index.html")










if __name__ == '__main__':
    app.run()
