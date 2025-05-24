from flask import Blueprint, render_template, request, flash, redirect, url_for
import os
import subprocess
import json
import requests
import platform
import shutil
from pathlib import Path

main = Blueprint('main', __name__)

# Configuration paths
CONFIG_DIR = '/etc/frpc'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'frpc.toml')
FRPC_BIN_DIR = '/usr/local/bin'
FRPC_BIN = os.path.join(FRPC_BIN_DIR, 'frpc')

def get_latest_frpc_version():
    """Get the latest frpc version from GitHub"""
    try:
        response = requests.get('https://api.github.com/repos/fatedier/frp/releases/latest')
        return response.json()['tag_name']
    except Exception as e:
        print(f"Error getting latest version: {e}")
        return "v0.51.3"  # Fallback to a known version

def download_frpc(version):
    """Download frpc binary for the current architecture"""
    arch = platform.machine()
    if arch == 'x86_64':
        arch = 'amd64'
    elif arch == 'aarch64':
        arch = 'arm64'
    
    os_type = 'linux'
    download_url = f"https://github.com/fatedier/frp/releases/download/{version}/frp_{version[1:]}_{os_type}_{arch}.tar.gz"
    
    try:
        # Download the tar.gz file
        response = requests.get(download_url, stream=True)
        tar_file = '/tmp/frpc.tar.gz'
        with open(tar_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the file
        extract_dir = '/tmp/frpc_extract'
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
        
        subprocess.run(['tar', '-xzf', tar_file, '-C', extract_dir])
        
        # Find the frpc binary in the extracted directory
        frpc_dirs = [d for d in os.listdir(extract_dir) if d.startswith('frp_')]
        if not frpc_dirs:
            return False
            
        frpc_dir = os.path.join(extract_dir, frpc_dirs[0])
        frpc_binary = os.path.join(frpc_dir, 'frpc')
        
        # Make sure the target directory exists
        os.makedirs(FRPC_BIN_DIR, exist_ok=True)
        
        # Copy the binary to the target location
        shutil.copy(frpc_binary, FRPC_BIN)
        os.chmod(FRPC_BIN, 0o755)
        
        # Clean up
        shutil.rmtree(extract_dir)
        os.remove(tar_file)
        
        return True
    except Exception as e:
        print(f"Error downloading frpc: {e}")
        return False

def create_config_file(server_ip, server_port, token=None):
    """Create the initial frpc.toml configuration file"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    config = f"""[common]
server_addr = {server_ip}
server_port = {server_port}
"""
    
    if token:
        config += f"token = {token}\n"
    
    with open(CONFIG_FILE, 'w') as f:
        f.write(config)

def create_systemd_service():
    """Create systemd service files for frpc and the web UI"""
    # FRPC service
    frpc_service = """[Unit]
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
"""
    
    with open('/etc/systemd/system/frpc.service', 'w') as f:
        f.write(frpc_service)
    
    # Web UI service
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    webui_service = f"""[Unit]
Description=FRPC Manager Web UI
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {parent_dir}/run.py
WorkingDirectory={parent_dir}
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
"""
    
    with open('/etc/systemd/system/frpc-manager.service', 'w') as f:
        f.write(webui_service)
    
    # Reload systemd
    subprocess.run(['systemctl', 'daemon-reload'])
    
    # Enable and start services
    subprocess.run(['systemctl', 'enable', 'frpc.service'])
    subprocess.run(['systemctl', 'enable', 'frpc-manager.service'])
    subprocess.run(['systemctl', 'start', 'frpc.service'])
    subprocess.run(['systemctl', 'start', 'frpc-manager.service'])

def read_config():
    """Read the current frpc configuration"""
    if not os.path.exists(CONFIG_FILE):
        return {"common": {}, "endpoints": {}}
    
    config = {"common": {}, "endpoints": {}}
    current_section = None
    
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section != 'common':
                    config["endpoints"][current_section] = {}
            elif current_section and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if current_section == 'common':
                    config["common"][key] = value
                else:
                    config["endpoints"][current_section][key] = value
    
    return config

def write_config(config):
    """Write the configuration back to frpc.toml"""
    # Make sure the directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        # Write common section
        f.write("[common]\n")
        for key, value in config["common"].items():
            f.write(f"{key} = {value}\n")
        f.write("\n")
        
        # Write endpoint sections
        for endpoint, settings in config["endpoints"].items():
            f.write(f"[{endpoint}]\n")
            for key, value in settings.items():
                f.write(f"{key} = {value}\n")
            f.write("\n")

def restart_frpc():
    """Restart the frpc service"""
    try:
        subprocess.run(['systemctl', 'restart', 'frpc.service'])
        return True
    except Exception as e:
        print(f"Error restarting frpc: {e}")
        return False

@main.route('/')
def index():
    """Main page showing current configuration"""
    config = read_config()
    return render_template('index.html', config=config)

@main.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup page"""
    if request.method == 'POST':
        server_ip = request.form.get('server_ip')
        server_port = request.form.get('server_port')
        token = request.form.get('token')
        
        if not server_ip or not server_port:
            flash('Server IP and port are required', 'error')
            return redirect(url_for('main.setup'))
        
        # Download frpc
        version = get_latest_frpc_version()
        if not download_frpc(version):
            flash('Failed to download frpc', 'error')
            return redirect(url_for('main.setup'))
        
        # Create initial config
        create_config_file(server_ip, server_port, token)
        
        # Create systemd services
        create_systemd_service()
        
        flash('Setup completed successfully', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('setup.html')

@main.route('/add_endpoint', methods=['POST'])
def add_endpoint():
    """Add a new endpoint to the configuration"""
    name = request.form.get('name')
    endpoint_type = request.form.get('type')
    local_ip = request.form.get('local_ip')
    local_port = request.form.get('local_port')
    remote_port = request.form.get('remote_port')
    
    if not all([name, endpoint_type, local_ip, local_port, remote_port]):
        flash('All fields are required', 'error')
        return redirect(url_for('main.index'))
    
    config = read_config()
    
    if name in config["endpoints"]:
        flash(f'Endpoint {name} already exists', 'error')
        return redirect(url_for('main.index'))
    
    config["endpoints"][name] = {
        'type': endpoint_type,
        'local_ip': local_ip,
        'local_port': local_port,
        'remote_port': remote_port
    }
    
    write_config(config)
    restart_frpc()
    
    flash(f'Endpoint {name} added successfully', 'success')
    return redirect(url_for('main.index'))

@main.route('/delete_endpoint/<name>')
def delete_endpoint(name):
    """Delete an endpoint from the configuration"""
    config = read_config()
    
    if name in config["endpoints"]:
        del config["endpoints"][name]
        write_config(config)
        restart_frpc()
        flash(f'Endpoint {name} deleted successfully', 'success')
    else:
        flash(f'Endpoint {name} not found', 'error')
    
    return redirect(url_for('main.index'))

@main.route('/edit_common', methods=['POST'])
def edit_common():
    """Edit common configuration settings"""
    server_addr = request.form.get('server_addr')
    server_port = request.form.get('server_port')
    token = request.form.get('token')
    
    if not server_addr or not server_port:
        flash('Server address and port are required', 'error')
        return redirect(url_for('main.index'))
    
    config = read_config()
    config["common"]["server_addr"] = server_addr
    config["common"]["server_port"] = server_port
    
    if token:
        config["common"]["token"] = token
    elif "token" in config["common"]:
        del config["common"]["token"]
    
    write_config(config)
    restart_frpc()
    
    flash('Common settings updated successfully', 'success')
    return redirect(url_for('main.index'))

@main.route('/restart')
def restart():
    """Restart the frpc service"""
    if restart_frpc():
        flash('FRPC restarted successfully', 'success')
    else:
        flash('Failed to restart FRPC', 'error')
    
    return redirect(url_for('main.index')