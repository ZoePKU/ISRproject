from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)


def retrieve(query):
    res = [
        {'name': '0001.jpg', 'src_path': 'static/bqbSource/0001.jpg',
         'score': 78.8, 'description': 'it is a description'},
        {'name': '0002.jpg', 'src_path': 'static/bqbSource/0002.jpg',
         'score': 76.1, 'description': 'it is a description'},
        {'name': '0003.jpg', 'src_path': 'static/bqbSource/0003.jpg',
         'score': 76.1, 'description': 'it is a description'},
        {'name': '0004.jpg', 'src_path': 'static/bqbSource/0004.jpg',
         'score': 76.1, 'description': 'it is a description'},
        {'name': '0005.jpg', 'src_path': 'static/bqbSource/0005.jpg',
         'score': 76.1, 'description': 'it is a description'},
        {'name': '0006.jpg', 'src_path': 'static/bqbSource/0006.jpg',
         'score': 76.1, 'description': 'it is a description'}
    ]

    return res


@app.route('/')
def index():
    res = retrieve("熊猫头")
    return render_template('search_result.html', success=True, data=res,
                           length=len(res))


if __name__ == '__main__':
    app.run(debug=True, port=8080)
