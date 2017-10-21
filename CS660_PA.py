from flask import Flask, render_template
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
