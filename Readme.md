# Firebase Image Analysis and Diet Logging API

Author: Basith

## Description

This Flask application provides an API for uploading and analyzing food images using Firebase Firestore and LogMeal API. It also allows logging food items to a diet log collection.

## Features

- **Image Upload and Analysis**
    - Upload images of food items for nutritional analysis.
    - Preprocess images and send them to LogMeal API to retrieve nutritional data.

- **Diet Logging**
    - Add meals with nutritional data to a diet log collection.
    - Retrieve and display the history of scanned food items and diet logs.

- **Chatbot Integration**
    - Implement a chatbot using GenerativeAI to respond to user messages.

## Requirements

- Flask
- firebase-admin
- Pillow (PIL)
- requests
- google.generativeai (Google LLM Library)

## Environment Variables

Ensure the following environment variables are set:

- `API_TOKEN`: LogMeal API token
- `GEMINI_API_KEY`: Gemini API key for GenerativeAI

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/MuhammedBasith/food-lens-backend.git
   cd food-lens-backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
    - Create a `.env` file and define `API_TOKEN` and `GEMINI_API_KEY`.

4. Start the Flask server:
   ```bash
   python server.py
   ```

## API Endpoints

- **Upload Image**
    - `POST /api/upload-image`: Upload and analyze an image of a food item.

- **Add to Diet Log**
    - `POST /api/add-to-diet`: Log a meal with nutritional data to the diet log.

- **Get Scanned Items History**
    - `GET /api/get-scanned-items`: Retrieve the history of scanned food items.

- **Get Diet Logs for Calendar**
    - `GET /api/calendar/diet-logs`: Retrieve diet logs for display on a user calendar.

- **Chatbot Interaction**
    - `POST /api/chatbot`: Interact with a chatbot to generate responses using GenerativeAI.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

