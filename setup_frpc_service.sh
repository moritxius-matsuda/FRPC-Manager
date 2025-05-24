#!/bin/bash

# Script to set up FRPC as a systemd service
# Run this script as root

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "=== Setting up FRPC as a systemd service ==="

# Make sure the config directory exists
mkdir -p /etc/frpc

# Check if frpc binary exists
if [ ! -f "/usr/local/bin/frpc" ]; then
  echo "FRPC binary not found at /usr/local/bin/frpc"
  echo "Please run the setup process first or manually install FRPC"
  exit 1
fi

# Create the systemd service file
echo "Creating systemd service file..."
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

# Reload systemd, enable and start the service
echo "Enabling and starting FRPC service..."
systemctl daemon-reload
systemctl enable frpc.service
systemctl start frpc.service

# Check service status
echo "FRPC service status:"
systemctl status frpc.service

echo "=== FRPC service setup complete ==="
echo "You can check the service status anytime with: systemctl status frpc.service"
echo "You can view logs with: journalctl -u frpc.service"