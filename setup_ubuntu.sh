#!/bin/bash

# Instagram Message Sender API - Ubuntu Setup Script
echo "Setting up Instagram Message Sender API for Ubuntu..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip

# Install Chrome dependencies
echo "Installing Chrome dependencies..."
sudo apt-get install -y wget unzip xvfb libxi6 libgconf-2-4 default-jdk

# Install Chrome
echo "Installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install selenium requests flask flask-cors python-dotenv gunicorn

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Instagram Credentials
INSTAGRAM_USERNAME=your_username_here
INSTAGRAM_PASSWORD=your_password_here

# Default recipient (optional)
DEFAULT_RECIPIENT=default_recipient_username

# Default message (optional)
DEFAULT_MESSAGE=Hello! This is a default message.

# Browser settings
HEADLESS=true  # Set to true for headless mode, false to see the browser

# API settings
PORT=5000
GUNICORN_WORKERS=1
EOL
    echo ".env file created. Please edit it with your credentials."
else
    echo ".env file already exists."
fi

# Make run_api.py executable
chmod +x run_api.py

echo "Setup complete! You can now run the API with: python3 run_api.py"
echo "Make sure to edit the .env file with your Instagram credentials first."
