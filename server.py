from flask import Flask

flask_app = Flask(__name__)


@flask_app.route('/')
def hello():
    return 'Welcome to Food Lens Backend!'


if __name__ == '__main__':
    flask_app.run(debug=True)
