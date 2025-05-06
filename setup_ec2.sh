#!/bin/bash

# Instagram API Setup Script for Debian EC2
# This script installs all necessary dependencies for running the Instagram API

echo "===== Instagram API Setup for Debian EC2 ====="
echo "This script will install all necessary dependencies."
echo "It should be run from the instagram-api directory."
echo ""

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install Python and pip
echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome dependencies
echo "Installing Chrome and dependencies..."
sudo apt install -y wget gnupg
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm ./google-chrome-stable_current_amd64.deb

# Install Xvfb for headless browser
echo "Installing Xvfb for headless browser support..."
sudo apt install -y xvfb libxi6 libgconf-2-4

# Install additional dependencies
echo "Installing additional dependencies..."
sudo apt install -y unzip curl

# Download and install ChromeDriver
echo "Downloading and installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Detected Chrome version: $CHROME_VERSION"

# Download the latest ChromeDriver for the detected Chrome version
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.49/linux64/chromedriver-linux64.zip"
echo "Downloading ChromeDriver from: $CHROMEDRIVER_URL"

# Download and extract ChromeDriver
wget -O chromedriver_linux64.zip $CHROMEDRIVER_URL
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip

# Move ChromeDriver to the parent directory (root folder)
echo "Moving ChromeDriver to the parent directory..."
cp chromedriver-linux64/chromedriver ../chromedriver
chmod +x ../chromedriver

# Also keep a copy in the project directory
echo "Keeping a copy in the project directory..."
mkdir -p chromedriver
cp chromedriver-linux64/chromedriver chromedriver/
chmod +x chromedriver/chromedriver

# Clean up
rm -rf chromedriver-linux64

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set up systemd service
echo "Setting up systemd service..."
sudo cp instagram-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable instagram-api

echo ""
echo "===== Setup Complete ====="
echo "ChromeDriver has been installed in:"
echo "- $(pwd)/chromedriver/chromedriver"
echo "- $(dirname $(pwd))/chromedriver"
echo ""
echo "To start the service, run: sudo systemctl start instagram-api"
echo "To check service status: sudo systemctl status instagram-api"
echo "To view logs: sudo journalctl -u instagram-api -f"
echo ""
echo "The API will be available at: http://your-ec2-ip:5000"
