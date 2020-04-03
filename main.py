from flask import Flask, render_template
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'QeKT2gpT58HDBr0'


@app.route('/')
def main_page():
    return render_template('base.html', title='pih-poh.online')


@app.route('/newsline')
def newsline():
    return render_template('base.html', title='Лента')


@app.route('/forum')
def forum():
    return render_template('base.html', title='Форум')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/donat')
def donat():
    return render_template('base.html', title='Донат')


db_session.global_init("db/pihpoh_db.sqlite")
if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')