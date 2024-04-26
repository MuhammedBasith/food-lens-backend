"""
Firebase Image Analysis and Diet Logging API

Author: Basith
Description: This Flask application provides an API for uploading and analyzing food images using Firebase
             Firestore and LogMeal API. It also allows logging food items to a diet log collection.

This script implements the following endpoints:
- /api/upload-image: Uploads an image, preprocesses it, sends it to LogMeal API for analysis,
                     and stores the nutritional data in Firebase.
- /api/add-to-diet: Adds a meal with nutritional data to the diet log collection in Firestore.
- /api/get-scanned-items: Retrieves scanned food items history from Firestore.
- /api/calendar/diet-logs: Retrieves diet log items for a user calendar from Firestore.
- /api/chatbot: Implements a simple chatbot using GenerativeAI to respond to user messages.

Requirements:
- Flask
- firebase-admin
- PIL (Pillow)
- requests
- google.generativeai (Google LLM Library)

Environment Variables:
- API_TOKEN: LogMeal API token
- GEMINI_API_KEY: Gemini API key for GenerativeAI

Usage:
1. Run this script to start the Flask server.
2. Use the provided API endpoints to interact with the application.

"""

from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import google.generativeai as genai
from dotenv import load_dotenv
import firebase_admin
from PIL import Image
import datetime
import requests
import os


flask_app = Flask(__name__)
CORS(flask_app)
load_dotenv()

api_token = os.getenv('API_TOKEN')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if api_token is None or gemini_api_key is None:
    raise ValueError("API_TOKEN environment variable is not set")


genai.configure(api_key=gemini_api_key)

# Initialize Firebase
cred = credentials.Certificate("food-lens-firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def preprocess_and_send_image(image_path):
    im = Image.open(image_path)
    rgb_im = im.convert('RGB')
    # print(im.info)
    # exif_dict = piexif.load(im.info["exif"])
    # exif_bytes = piexif.dump(exif_dict)
    # rgb_im = im.convert('RGB')
    #
    # width, height = rgb_im.size
    #
    # size_mb = os.path.getsize(image_path) >> 20
    # while size_mb >= 1:
    #     size = int(width * 0.75), int(height * 0.75)
    #     resized_image = rgb_im.resize(size, Image.ANTIALIAS)
    #     resized_image.save(image_path, 'JPEG', quality=95, exif=exif_bytes)
    #     size_mb = os.path.getsize(image_path) >> 20
    rgb_im.save(image_path, quality=20, optimize=True)
    return image_path


def send_to_log_meal_api(image_path):
    img = image_path
    api_user_token = api_token
    headers = {'Authorization': 'Bearer ' + api_user_token}

    url = 'https://api.logmeal.com/v2/image/segmentation/complete'
    resp = requests.post(url, files={'image': open(img, 'rb')}, headers=headers)
    print(resp)

    # Nutritional information
    url = 'https://api.logmeal.com/v2/recipe/nutritionalInfo'
    resp = requests.post(url, json={'imageId': resp.json()['imageId']}, headers=headers)
    return resp.json()


@flask_app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image_file = request.files['image']

        temp_image_path = 'uploads/image.jpg'
        image_file.save(temp_image_path)

        preprocessed_image_path = preprocess_and_send_image(temp_image_path)
        nutrition_data = send_to_log_meal_api(preprocessed_image_path)

        scanned_item = {
            'foodNames': nutrition_data['foodName'],
            'wholeData': nutrition_data,
            'captured_at': datetime.datetime.now()
        }

        try:
            doc_ref = db.collection('scanned_items').add(scanned_item)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        os.remove(temp_image_path)
        return jsonify(scanned_item), 200
    else:
        return 'No image provided', 400


@flask_app.route('/api/add-to-diet', methods=['POST'])
def add_to_diet():
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        meal_type = data.get('mealType')
        nutrition_data = data.get('nutritionData')
        timestamp = data.get('timestamp')

        if not meal_type or not nutrition_data:
            return jsonify({'error': 'Meal type or nutrition data missing'}), 400

        if meal_type not in ['breakfast', 'lunch', 'dinner', 'other']:
            return jsonify({'error': 'Invalid meal type'}), 400

        # Construct meal log document
        meal_log = {
            'meal_type': meal_type,
            'nutrition_data': nutrition_data,
            'timestamp': timestamp
        }

        db.collection('DietLogs').add(meal_log)

        return jsonify({'message': 'Meal added to diet logs successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# This API is designed to retrieve data to display the complete history of scanned items.
@flask_app.route('/api/get-scanned-items', methods=['GET'])
def get_scanned_items():
    try:
        scanned_items_ref = db.collection('scanned_items')

        scanned_items = scanned_items_ref.stream()

        scanned_items_data = []

        for item in scanned_items:
            item_data = item.to_dict()
            scanned_items_data.append(item_data)

        return jsonify({'success': True, 'scanned_items': scanned_items_data}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# This API is designed to retrieve data to display the complete history of diet logged items for user calendar.
@flask_app.route('/api/calendar/diet-logs', methods=['GET'])
def get_diet_logs():
    try:
        diet_logs = db.collection('DietLogs')

        items = diet_logs.stream()

        diet_log_data = []

        for item in items:
            item_data = item.to_dict()
            diet_log_data.append(item_data)

        return jsonify({'success': True, 'scanned_items': diet_log_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flask_app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        user_message = request.json['message']

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(user_message)

        return jsonify({'response': response.text}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)

