#!/bin/bash

# Wrapper script to start the Instagram API with the virtual environment

# Set the working directory
cd /home/ubuntu/instagram-api

# Activate the virtual environment
source /home/ubuntu/instagram-api/venv/bin/activate

# Start the API
python /home/ubuntu/instagram-api/run_api.py
