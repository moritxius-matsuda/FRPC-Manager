#!/bin/bash

# FRPC Manager Installation Script
# This script installs the FRPC Manager and its dependencies

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "=== FRPC Manager Installation ==="
echo "This script will install FRPC Manager and its dependencies."

# Install required packages
echo "Installing dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y python3 python3-pip
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y python3 python3-pip
else
    echo "Unsupported package manager. Please install Python 3 and pip manually."
    exit 1
fi

# Create installation directory
INSTALL_DIR="/opt/frpc-manager"
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p $INSTALL_DIR

# Copy files to installation directory
echo "Copying files..."
cp -r ./* $INSTALL_DIR/

# Create virtual environment and install dependencies
echo "Setting up Python environment..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate
pip install flask requests

# Create systemd service for FRPC Manager
echo "Creating systemd service..."
cat > /etc/systemd/system/frpc-manager.service << EOF
[Unit]
Description=FRPC Manager Web UI
After=network.target

[Service]
Type=simple
ExecStart=/opt/frpc-manager/venv/bin/python /opt/frpc-manager/run.py
WorkingDirectory=/opt/frpc-manager
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "Enabling and starting FRPC Manager service..."
systemctl daemon-reload
systemctl enable frpc-manager.service
systemctl start frpc-manager.service

echo "=== Installation Complete ==="
echo "FRPC Manager is now installed and running on http://localhost:5000"
echo "Please visit this URL to complete the FRPC setup."