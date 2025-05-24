#!/bin/bash

# Script to download and install FRPC
# Run this script as root

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "=== Downloading and installing FRPC ==="

# Determine system architecture
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then
  ARCH="amd64"
elif [ "$ARCH" == "aarch64" ]; then
  ARCH="arm64"
fi

# Set FRPC version
VERSION="v0.51.3"  # You can change this to the latest version

# Create temporary directory
TMP_DIR="/tmp/frpc_download"
mkdir -p $TMP_DIR

# Download FRPC
echo "Downloading FRPC $VERSION for $ARCH..."
DOWNLOAD_URL="https://github.com/fatedier/frp/releases/download/$VERSION/frp_${VERSION#v}_linux_$ARCH.tar.gz"
echo "Download URL: $DOWNLOAD_URL"

wget -O $TMP_DIR/frpc.tar.gz $DOWNLOAD_URL

if [ $? -ne 0 ]; then
  echo "Failed to download FRPC. Please check your internet connection."
  exit 1
fi

# Extract the archive
echo "Extracting FRPC..."
tar -xzf $TMP_DIR/frpc.tar.gz -C $TMP_DIR

# Find the frpc binary
FRPC_DIR=$(find $TMP_DIR -type d -name "frp_*" | head -n 1)
if [ -z "$FRPC_DIR" ]; then
  echo "Failed to find FRPC directory in the extracted archive."
  exit 1
fi

# Copy the binary to /usr/local/bin
echo "Installing FRPC to /usr/local/bin..."
cp $FRPC_DIR/frpc /usr/local/bin/
chmod +x /usr/local/bin/frpc

# Create config directory if it doesn't exist
mkdir -p /etc/frpc

# Create a basic config file if it doesn't exist
if [ ! -f "/etc/frpc/frpc.toml" ]; then
  echo "Creating a basic config file at /etc/frpc/frpc.toml..."
  cat > /etc/frpc/frpc.toml << EOF
[common]
# Please configure these settings through the web interface
server_addr = 127.0.0.1
server_port = 7000
EOF
fi

# Clean up
echo "Cleaning up..."
rm -rf $TMP_DIR

echo "=== FRPC installation complete ==="
echo "FRPC binary installed at: /usr/local/bin/frpc"
echo "Config file location: /etc/frpc/frpc.toml"
echo "You can now start the FRPC service with: systemctl start frpc.service"
echo "Or configure it through the web interface at http://localhost:5000"