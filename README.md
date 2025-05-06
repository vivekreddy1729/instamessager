# Instagram Message Sender API

A Python API that uses Selenium for headless browser automation to send direct messages to Instagram users.

## Features

- **REST API**: Send Instagram messages via simple HTTP requests
- **Single Login**: Logs in once when the server starts, maintains the session
- **Headless Operation**: Runs in the background without a visible browser
- **Automated Following**: Automatically follows users if needed before sending messages
- **Robust Error Handling**: Detailed error reporting and automatic recovery
- **Scalable**: Can handle multiple message requests sequentially
- **Secure**: Credentials stored in environment variables, not in code

## Requirements

- Python 3.6+
- Selenium
- Requests (for downloading ChromeDriver)

## Installation

1. Clone or download this repository:
   ```
   git clone <repository-url>
   cd instagram-message-sender
   ```

2. Install the required packages:
   ```
   pip install selenium requests
   ```

## Usage

### Setting Up Environment Variables

The API uses a `.env` file to store your credentials and settings:

1. Edit the `.env` file in the project directory:
   ```
   # Instagram Credentials
   INSTAGRAM_USERNAME=your_username_here
   INSTAGRAM_PASSWORD=your_password_here

   # API settings
   PORT=5000
   GUNICORN_WORKERS=1
   ```

2. Replace the placeholder values with your actual credentials.

### Running the API Server

Start the API server using the provided script:

```bash
python run_api.py
```

The server will:
1. Read your credentials from the `.env` file
2. Log in to Instagram once at startup
3. Start listening for API requests
4. Handle message sending requests

### API Endpoints

#### 1. Send a Message

**Endpoint:** `/send-message`
**Method:** POST
**Content-Type:** application/json

**Request Body:**
```json
{
  "recipient": "username_to_message",
  "message": "Your message here"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Message sent to username_to_message successfully!"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

#### 2. Health Check

**Endpoint:** `/health`
**Method:** GET

**Response:**
```json
{
  "status": "ok",
  "initialized": true
}
```

#### 3. Restart Session

**Endpoint:** `/restart`
**Method:** POST

**Response:**
```json
{
  "success": true,
  "message": "Instagram sender restarted successfully"
}
```

### Testing the API

Use the provided test client:

```bash
python test_api_client.py recipient_username "Your message here"
```

### Using the API in Your Own Code

You can also make HTTP requests to the API from your own code:

```python
import requests

# API base URL
base_url = "http://localhost:5000"

# Send a message
response = requests.post(
    f"{base_url}/send-message",
    json={
        "recipient": "username_to_message",
        "message": "Your message here"
    },
    headers={"Content-Type": "application/json"}
)

# Check the result
result = response.json()
if result.get('success'):
    print(f"Success: {result.get('message')}")
else:
    print(f"Error: {result.get('error')}")
```

### API Integration Examples

#### Python
```python
import requests

def send_instagram_message(recipient, message):
    response = requests.post(
        "http://localhost:5000/send-message",
        json={"recipient": recipient, "message": message},
        headers={"Content-Type": "application/json"}
    )
    return response.json()
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

async function sendInstagramMessage(recipient, message) {
    try {
        const response = await axios.post('http://localhost:5000/send-message', {
            recipient: recipient,
            message: message
        });
        return response.data;
    } catch (error) {
        return error.response.data;
    }
}
```

#### cURL
```bash
curl -X POST http://localhost:5000/send-message \
  -H "Content-Type: application/json" \
  -d '{"recipient":"username_to_message","message":"Your message here"}'
```

### As a Module in Your Own Scripts

You can also use the `InstagramMessageSender` class in your own Python scripts:

```python
import os
from dotenv import load_dotenv
from instagram_message_sender import InstagramMessageSender

# Load credentials from .env file
load_dotenv()
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

# Create an instance (headless=False to see the browser)
sender = InstagramMessageSender(headless=True)

try:
    # Login to Instagram
    if sender.login(username, password):
        # Send message
        sender.send_message("recipient_username", "Your message here")
finally:
    # Close the WebDriver
    sender.close()
```

Or you can provide credentials directly:

```python
from instagram_message_sender import InstagramMessageSender

# Create an instance
sender = InstagramMessageSender(headless=False)  # Set to False to see the browser

try:
    # Login to Instagram
    if sender.login("your_username", "your_password"):
        # Send message
        sender.send_message("recipient_username", "Your message here")
finally:
    # Close the WebDriver
    sender.close()
```

## How It Works

1. **ChromeDriver Setup**: The tool automatically downloads the appropriate ChromeDriver for your system.
2. **Login Process**: Uses human-like typing and timing to avoid detection.
3. **Message Sending Process**:
   - First navigates to the recipient's profile
   - Follows the user if not already following (required to send messages to some users)
   - Waits for 3 seconds after following
   - Clicks on the message button on their profile
   - If that fails, tries the alternative method via the direct message inbox
   - Sends the message with human-like typing
4. **Screenshots**: Takes screenshots at key points for verification and troubleshooting.

## Troubleshooting

If you encounter issues:

1. **Check the Screenshots**: The tool saves screenshots at various stages in the current directory.
2. **Review the Logs**: Detailed logs are displayed in the console.
3. **Instagram Changes**: Instagram's web interface changes frequently. If the tool stops working, it may need updates.
4. **Security Verification**: If Instagram requires security verification, you may need to log in manually first.

## API Security Considerations

### Protecting Your Credentials

The API uses a `.env` file to store your credentials. To protect your credentials:

1. Never commit your `.env` file to version control
2. A `.gitignore` file is included that will prevent the `.env` file from being committed
3. Only run the API on systems you trust
4. Consider using a dedicated Instagram account for this API
5. Restrict access to the API server using a firewall or reverse proxy

### API Access Control

By default, the API has no authentication. For production use, consider:

1. Adding API key authentication
2. Running behind a reverse proxy with authentication
3. Restricting IP access to trusted clients
4. Using HTTPS for all API communication

### Rate Limiting

To avoid Instagram's rate limits and detection systems:

1. Add delays between message requests (at least 30-60 seconds)
2. Limit the number of messages sent per day
3. Monitor for error responses that might indicate rate limiting
4. Implement exponential backoff for retries

## Important Notes

- **Terms of Service**: Using automation tools with Instagram may violate their terms of service.
- **Rate Limiting**: Instagram may rate-limit or block accounts that send too many automated messages.
- **Following Users**: The API will automatically follow users if necessary to send them a message. Be aware that this will increase your "following" count.
- **Security**: Never share your Instagram credentials or run this API on untrusted systems.
- **Educational Purpose**: This tool is for educational purposes only.
- **Instagram Updates**: Instagram frequently updates its interface and security measures. If the API stops working, it may need to be updated.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
