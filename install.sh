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
    apt-get install -y python3 python3-pip python3-venv python3-flask
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y python3 python3-pip
    pip3 install flask requests
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y python3 python3-pip
    pip3 install flask requests
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
# Make sure pip is up to date
pip install --upgrade pip
# Install required packages
pip install flask requests
# Verify flask is installed
if ! pip show flask > /dev/null; then
    echo "Flask installation failed. Installing again..."
    pip install flask
fi

# Create systemd service for FRPC Manager
echo "Creating systemd service..."
cat > /etc/systemd/system/frpc-manager.service << EOF
[Unit]
Description=FRPC Manager Web UI
After=network.target

[Service]
Type=simple
ExecStart=/opt/frpc-manager/venv/bin/python3 /opt/frpc-manager/run.py
WorkingDirectory=/opt/frpc-manager
Environment="PATH=/opt/frpc-manager/venv/bin:/usr/local/bin:/usr/bin:/bin"
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
EOF

# Create FRPC service
echo "Creating FRPC service..."
cat > /etc/systemd/system/frpc.service << EOF
[Unit]
Description=frpc service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/frpc -c /etc/frpc/frpc.toml
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the services
echo "Enabling and starting services..."
systemctl daemon-reload
systemctl enable frpc-manager.service
systemctl enable frpc.service
systemctl start frpc-manager.service
# Note: frpc service will be started after setup is completed via the web UI

echo "=== Installation Complete ==="
echo "FRPC Manager is now installed and running on http://localhost:5000"
echo "Please visit this URL to complete the FRPC setup."