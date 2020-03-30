from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/main')
def main_page():
    return render_template('base.html', title='pih-poh.online')


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')