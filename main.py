from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/main')
def main_page():
    return render_template('base.html', title='pih-poh.online')

@app.route('/forum')
def forum():
    return render_template('base.html', title='Форум')

@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')

@app.route('/donat')
def donat():
    return render_template('base.html', title='Донат')

if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')