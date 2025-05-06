import argparse
import getpass
import os
import sys
from dotenv import load_dotenv
from instagram_message_sender import InstagramMessageSender

def main():
    """
    Command-line interface for the Instagram Message Sender
    """
    # Load environment variables
    load_dotenv()

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Send a direct message to an Instagram user')
    parser.add_argument('--username', '-u', help='Your Instagram username (defaults to INSTAGRAM_USERNAME from .env)')
    parser.add_argument('--password', '-p', help='Your Instagram password (defaults to INSTAGRAM_PASSWORD from .env)')
    parser.add_argument('--recipient', '-r', help='Recipient\'s Instagram username (defaults to DEFAULT_RECIPIENT from .env)')
    parser.add_argument('--message', '-m', help='Message to send (defaults to DEFAULT_MESSAGE from .env)')
    parser.add_argument('--visible', '-v', action='store_true', help='Run in visible mode (overrides HEADLESS from .env)')

    # Parse arguments
    args = parser.parse_args()

    # Get username from args or environment
    username = args.username or os.getenv("INSTAGRAM_USERNAME")
    if not username:
        print("Error: Instagram username not provided.")
        print("Please either specify it with -u/--username or set INSTAGRAM_USERNAME in your .env file.")
        sys.exit(1)

    # Get password from args or environment
    password = args.password or os.getenv("INSTAGRAM_PASSWORD")
    if not password:
        # If password is not in args or .env, prompt for it
        password = getpass.getpass("Enter your Instagram password: ")

    # Get recipient from args or environment
    recipient = args.recipient or os.getenv("DEFAULT_RECIPIENT")
    if not recipient:
        print("Error: Recipient username not provided.")
        print("Please either specify it with -r/--recipient or set DEFAULT_RECIPIENT in your .env file.")
        sys.exit(1)

    # Get message from args or environment
    message = args.message or os.getenv("DEFAULT_MESSAGE")
    if not message:
        print("Error: Message not provided.")
        print("Please either specify it with -m/--message or set DEFAULT_MESSAGE in your .env file.")
        sys.exit(1)

    # Determine headless mode
    headless_env = os.getenv("HEADLESS", "false").lower()
    headless = headless_env in ("true", "yes", "1", "t", "y")
    if args.visible:
        headless = False

    print(f"\nSending message to: {recipient}")
    print(f"Running in {'visible' if not headless else 'headless'} mode")

    # Create Instagram Message Sender instance
    sender = InstagramMessageSender(headless=headless)

    try:
        # Login to Instagram
        print(f"\nLogging in as {username}...")
        if sender.login(username, password):
            # Send message
            print(f"\nSending message to {recipient}...")
            success = sender.send_message(recipient, message)
            if success:
                print(f"\nMessage sent to {recipient} successfully!")
                print("Screenshots have been saved to the current directory for verification.")
            else:
                print(f"\nFailed to send message to {recipient}.")
                print("Check the log and screenshots for more details.")
        else:
            print("\nLogin failed. Please check your credentials.")
            print("If you're seeing security verification requests, you may need to log in manually first.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Close the WebDriver
        print("\nClosing the browser...")
        sender.close()
        print("\nDone!")

if __name__ == "__main__":
    main()
