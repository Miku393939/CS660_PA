from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'war0623'
app.config['MYSQL_DATABASE_DB'] = 'CS660_PA'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config["DEBUG"] = True
mysql.init_app(app)

# conn = mysql.connect()
# cursor = conn.cursor()
# query = 'select * from USER'
# cursor.execute(query)
# data = []
# for item in cursor:
#     data.append(item)

# print(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register/', methods = ['POST','GET'])
def register():
    if request.method == 'GET':
        print("get~")
        return render_template('register.html')
    if request.method == 'POST':
        registerUserName = request.form['username']
        registerPassword = request.form['password']
        mysql.cursor.execute('Insert into USER (FNAME,PASSWORD) VALUES (%s,%s)',(registerUserName,registerPassword))
        mysql.cursor.commit()
        print("finished~")






if __name__ == '__main__':
    app.run()
