# FRPC Manager

A web-based management interface for [frp](https://github.com/fatedier/frp) client (frpc) on Linux systems.

## Features

- Darkmode
- Web UI for managing FRPC endpoints
- Automatic download and installation of FRPC during setup
- Systemd service setup for both FRPC and the web UI
- Easy configuration of FRPC endpoints
- One-click restart of FRPC service
- Support for various Linux distributions

## Installation

### Automatic Installation

1. Clone this repository:
   ```
   git clone https://github.com/moritxius-matsuda/FRPC-Manager.git
   cd FRPC-Manager
   ```

2. Run the installation script as root:
   ```
   sudo bash install.sh
   ```

3. Access the web interface at `http://your-server-ip:5000` and complete the setup.

The installation script automatically:
- Downloads and installs the FRPC binary
- Creates a basic configuration file
- Sets up systemd services for both FRPC and the web UI

### Troubleshooting

If you encounter any issues during installation:

1. If the FRPC binary is not automatically downloaded, you can run the download script:
   ```
   sudo bash download_frpc.sh
   ```

2. If the FRPC service is not automatically set up, you can run the service setup script:
   ```
   sudo bash setup_frpc_service.sh
   ```

See [SERVICE_SETUP.md](SERVICE_SETUP.md) for more details on service management.

### Manual Installation

1. Clone this repository:
   ```
   git clone https://github.com/moritxius-matsuda/FRPC-Manager.git
   cd FRPC-Manager
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   sudo python run.py
   ```

4. Access the web interface at `http://your-server-ip:5000` and complete the setup.

## Usage

### Initial Setup

On first run, you'll be prompted to enter:
- FRPS server IP address
- FRPS server port (default: 7000)
- Authentication token (if required)

The setup will:
1. Download the latest version of FRPC
2. Create the initial configuration
3. Set up systemd services for both FRPC and the web UI

### Managing Endpoints

After setup, you can:
- Add new endpoints (TCP, UDP, HTTP, HTTPS)
- Delete existing endpoints
- Restart the FRPC service to apply changes

### Common Settings

You can update the common settings at any time:
- FRPS server address
- FRPS server port
- Authentication token

## System Requirements

- Linux operating system with systemd
- Python 3.6 or higher
- Root access (for service management)

## Security Considerations

The web interface does not include authentication by default. It is recommended to:
- Run the service on a private network
- Set up a reverse proxy with authentication
- Use a firewall to restrict access to the web UI port

## License

This project is licensed under the MIT License - see the LICENSE file for details.
