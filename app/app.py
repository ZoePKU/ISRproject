from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('search_result.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
