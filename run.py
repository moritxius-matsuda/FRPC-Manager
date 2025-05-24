from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Check if we're running as root (needed for service management)
    if os.geteuid() != 0:
        print("Warning: Not running as root. Some features may not work properly.")
    
    # Default to port 5000, but allow override via environment variable
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app - in production, we'll use the systemd service
    # For development, we can run this directly
    app.run(host='0.0.0.0', port=port)