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

# Make sure the ChromeDriver directory exists
mkdir -p chromedriver

echo ""
echo "===== Setup Complete ====="
echo "To start the service, run: sudo systemctl start instagram-api"
echo "To check service status: sudo systemctl status instagram-api"
echo "To view logs: sudo journalctl -u instagram-api -f"
echo ""
echo "The API will be available at: http://your-ec2-ip:5000"
