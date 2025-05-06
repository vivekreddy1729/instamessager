import requests
import json
import time
import sys

def test_api(base_url, recipient, message):
    """Test the Instagram Message API"""
    # Check API health
    try:
        health_response = requests.get(f"{base_url}/health")
        health_data = health_response.json()
        
        print(f"API Health: {health_data}")
        
        if not health_data.get('initialized', False):
            print("Warning: API is not initialized yet. Waiting 10 seconds...")
            time.sleep(10)
            
            # Check again
            health_response = requests.get(f"{base_url}/health")
            health_data = health_response.json()
            
            if not health_data.get('initialized', False):
                print("Error: API failed to initialize. Please check the server logs.")
                return
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return
    
    # Send a message
    try:
        payload = {
            "recipient": recipient,
            "message": message
        }
        
        print(f"\nSending message to {recipient}...")
        response = requests.post(
            f"{base_url}/send-message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"Success: {result.get('message')}")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    # Get command line arguments
    if len(sys.argv) < 3:
        print("Usage: python test_api_client.py <recipient_username> <message>")
        print("Example: python test_api_client.py john_doe 'Hello, this is a test message!'")
        sys.exit(1)
    
    recipient = sys.argv[1]
    message = sys.argv[2]
    
    # API base URL (change if needed)
    base_url = "http://localhost:5000"
    
    # Test the API
    test_api(base_url, recipient, message)
