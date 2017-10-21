from flask import Flask, render_template
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'war0623'
app.config['MYSQL_DATABASE_DB'] = 'CS660_PA'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config["DEBUG"] = True
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
query = 'select * from USER'
cursor.execute(query)
data = []
for item in cursor:
    data.append(item)

print(data)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
