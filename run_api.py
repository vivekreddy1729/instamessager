import os
import platform
import subprocess
import signal
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_server():
    """Run the API server using Gunicorn on Unix-like systems or Flask on Windows"""
    # Get port from environment or use default
    port = os.getenv("PORT", "5000")

    # Check if we're on Windows
    if platform.system() == "Windows":
        # On Windows, use Flask's built-in server
        print(f"Starting Instagram Message API on port {port} using Flask (Windows mode)...")

        # Import the Flask app
        from instagram_api import app

        # Run the Flask app
        app.run(host='0.0.0.0', port=int(port), debug=False)
    else:
        # On Unix-like systems, use Gunicorn
        # Set number of workers (adjust based on your system)
        workers = os.getenv("GUNICORN_WORKERS", "1")

        # Build the Gunicorn command
        cmd = [
            "gunicorn",
            "--workers", workers,
            "--timeout", "120",
            "--bind", f"0.0.0.0:{port}",
            "instagram_api:app"
        ]

        print(f"Starting Instagram Message API on port {port} with {workers} worker(s)...")

        # Run Gunicorn
        process = subprocess.Popen(cmd)

        # Handle signals to gracefully shut down
        def signal_handler(sig, frame):
            print("\nShutting down Instagram Message API...")
            process.terminate()
            process.wait()
            sys.exit(0)

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Wait for the process to complete
        process.wait()

if __name__ == "__main__":
    run_server()
