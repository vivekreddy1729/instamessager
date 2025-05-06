import os
import time
import logging
import threading
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from instagram_message_sender import InstagramMessageSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global variables
instagram_sender = None
sender_lock = threading.Lock()
is_initialized = False

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def initialize_sender():
    """Initialize the Instagram Message Sender and login"""
    global instagram_sender, is_initialized

    # Get Instagram credentials from environment variables
    instagram_username = os.getenv("INSTAGRAM_USERNAME")
    instagram_password = os.getenv("INSTAGRAM_PASSWORD")

    # Check if credentials are provided
    if not instagram_username or not instagram_password:
        logger.error("Instagram credentials not found in .env file")
        return False

    try:
        # Create Instagram Message Sender instance (headless mode)
        instagram_sender = InstagramMessageSender(headless=True)

        # Login to Instagram
        logger.info(f"Logging in as {instagram_username}...")
        if instagram_sender.login(instagram_username, instagram_password):
            logger.info("Login successful!")
            is_initialized = True
            return True
        else:
            logger.error("Login failed. Check credentials and try again.")
            return False
    except Exception as e:
        logger.error(f"Error initializing Instagram sender: {e}")
        return False

@app.route('/', methods=['GET'])
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global is_initialized
    return jsonify({
        "status": "ok",
        "initialized": is_initialized
    })

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send a message to an Instagram user"""
    global instagram_sender, is_initialized, sender_lock

    # Check if sender is initialized
    if not is_initialized:
        return jsonify({
            "success": False,
            "error": "Instagram sender not initialized. Please restart the server."
        }), 500

    # Get request data
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400

    # Get recipient and message from request
    recipient = data.get('recipient')
    message = data.get('message')

    # Validate request data
    if not recipient:
        return jsonify({
            "success": False,
            "error": "Recipient username is required"
        }), 400

    if not message:
        return jsonify({
            "success": False,
            "error": "Message is required"
        }), 400

    # Acquire lock to ensure only one thread uses the sender at a time
    with sender_lock:
        try:
            # Send message
            logger.info(f"Sending message to {recipient}...")
            result = instagram_sender.send_message(recipient, message)

            if result:
                logger.info(f"Message sent to {recipient} successfully!")
                return jsonify({
                    "success": True,
                    "message": f"Message sent to {recipient} successfully!"
                })
            else:
                logger.error(f"Failed to send message to {recipient}")
                return jsonify({
                    "success": False,
                    "error": f"Failed to send message to {recipient}"
                }), 500
        except Exception as e:
            logger.error(f"Error sending message: {e}")

            # Check if we need to reinitialize the sender
            if "Send button not found" in str(e):
                logger.info("Attempting to refresh the session...")
                try:
                    # Navigate to Instagram home to refresh the session
                    instagram_sender.driver.get("https://www.instagram.com/")
                    time.sleep(2)
                    logger.info("Session refreshed")
                except Exception as refresh_error:
                    logger.error(f"Error refreshing session: {refresh_error}")

            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

@app.route('/restart', methods=['POST'])
def restart_sender():
    """Restart the Instagram sender (re-login)"""
    global instagram_sender, is_initialized, sender_lock

    with sender_lock:
        try:
            # Close existing sender if it exists
            if instagram_sender:
                try:
                    instagram_sender.close()
                except:
                    pass

            # Reinitialize the sender
            is_initialized = False
            success = initialize_sender()

            if success:
                return jsonify({
                    "success": True,
                    "message": "Instagram sender restarted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to restart Instagram sender"
                }), 500
        except Exception as e:
            logger.error(f"Error restarting Instagram sender: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {e}")
    return jsonify({
        "success": False,
        "error": str(e)
    }), 500

def shutdown_handler():
    """Clean up resources when shutting down"""
    global instagram_sender
    if instagram_sender:
        try:
            instagram_sender.close()
            logger.info("Instagram sender closed")
        except:
            pass

# Initialize the sender when the module is imported
if __name__ != '__main__':
    # Initialize in a separate thread to not block the app startup
    threading.Thread(target=initialize_sender).start()

if __name__ == '__main__':
    # Initialize the sender
    initialize_success = initialize_sender()
    if initialize_success:
        logger.info("Instagram sender initialized successfully")
    else:
        logger.warning("Failed to initialize Instagram sender. API will be available but sending messages will fail.")

    # Register shutdown handler
    import atexit
    atexit.register(shutdown_handler)

    # Run the Flask app
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
