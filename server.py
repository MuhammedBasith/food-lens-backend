from flask import Flask
import firebase_admin
from firebase_admin import credentials


flask_app = Flask(__name__)
cred = credentials.Certificate("food-lens-firebase.json")
firebase_admin.initialize_app(cred)


@flask_app.route('/')
def hello():
    return 'Welcome to Food Lens Backend!'


if __name__ == '__main__':
    flask_app.run(debug=True)
