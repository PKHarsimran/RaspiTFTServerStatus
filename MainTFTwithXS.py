import tkinter as tk
from tkinter import scrolledtext
import time
import subprocess
import psutil
import paramiko
import os

# Constants
PRIVATE_KEY_PATH = "/home/host/.ssh/id_rsa"
BYTES_IN_ONE_MIB = 1048576  # 1024 * 1024
ENABLE_DEBUG = False
os.environ['DISPLAY'] = ':0'

def debug_log(message):
    if ENABLE_DEBUG:
        print(f"[DEBUG] {message}")


def get_local_voltage():
    try:
        debug_log("Executing vcgencmd measure_volts to get voltage.")
        output = subprocess.check_output(['vcgencmd', 'measure_volts'], text=True)
        voltage = output.strip().replace('volt=', '').replace('V', ' V')
        return voltage
    except Exception as e:
        debug_log(f"Couldn't fetch voltage. Error: {e}")
        return "N/A"


def check_service_status(service_name):
    debug_log(f"Checking service status for {service_name}")
    try:
        subprocess.check_call(['systemctl', 'is-active', '--quiet', service_name])
        return True
    except Exception as e:
        debug_log(f"Exception occurred: {e}")
        return False


def check_internet_status():
    debug_log("Checking internet status")
    try:
        subprocess.check_output(['ping', '-c', '1', '8.8.8.8'])
        return True
    except Exception as e:
        debug_log(f"Exception occurred: {e}")
        return False


def get_ssh_connections():
    debug_log("Fetching SSH connections")
    try:
        output = subprocess.check_output(['netstat', '-tn'], text=True)
        debug_log(f"Raw netstat output: {output}")
        
        lines = output.strip().split('\n')
        ssh_connections = [line for line in lines if '22' in line.split()[3] and 'ESTABLISHED' in line.split()[5]]
        debug_log(f"Filtered SSH connections: {ssh_connections}")
        
        details = []
        for line in ssh_connections:
            elements = line.split()
            local_addr = elements[3]
            remote_addr = elements[4]
            details.append(f"{local_addr} <-> {remote_addr}")
        return len(ssh_connections), details
    except Exception as e:
        debug_log(f"Exception occurred: {e}")
        return "N/A", []


def get_remote_info(host, username, port=22):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        mykey = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
        client.connect(host, port, username=username, pkey=mykey)

        commands = {
            'Temperature': 'vcgencmd measure_temp',
            'CPU Load': "cat /proc/loadavg | awk '{print $1,$2,$3}'",
            'Free Disk Space': "df -h / | awk 'NR==2 {print $4}'",
            'Uptime': 'uptime -p',
            'Voltage and Throttle Status': 'vcgencmd get_throttled'
        }

        info = {}
        for key, command in commands.items():
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            info[key] = output

        client.close()
        return info

    except Exception as e:
        debug_log(f"Exception occurred: {e}")
        return None


def get_system_info():
    debug_log("Fetching system information")

    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    sent = net_io.bytes_sent / BYTES_IN_ONE_MIB
    received = net_io.bytes_recv / BYTES_IN_ONE_MIB
    local_voltage = get_local_voltage()
    local_volt_throttle_status = subprocess.check_output(['vcgencmd', 'get_throttled'], text=True).strip()
    remote_info = get_remote_info('192.168.4.114', 'pkvirus')

    smb_status = check_service_status('smbd')
    internet_status = check_internet_status()
    ssh_connection_count, ssh_connection_details = get_ssh_connections()

    output = f"===== Local System Status =====\n"
    output += f"CPU Usage: {cpu_percent}%\nRAM Usage: {ram.percent}%\nDisk Usage: {disk.percent}%\n"
    output += f"Voltage: {local_voltage}\nLocal Voltage and Throttle Status: {local_volt_throttle_status}\n"
    output += f"Data Sent: {sent:.2f} MiB\nData Received: {received:.2f} MiB\n"
    output += f"SMB Status: {'Up' if smb_status else 'Down'}\nInternet Status: {'Up' if internet_status else 'Down'}\n"
    output += f"SSH Connections: {ssh_connection_count}\n"
    for detail in ssh_connection_details:
        output += f"  - {detail}\n"
    output += "==================================\n"

    if remote_info is not None:
        output += "===== Remote System Status =====\n"
        output += f"Temperature: {remote_info.get('Temperature', 'N/A')}\n"
        output += f"CPU Load: {remote_info.get('CPU Load', 'N/A')}\n"
        output += f"Free Disk Space: {remote_info.get('Free Disk Space', 'N/A')}\n"
        output += f"Uptime: {remote_info.get('Uptime', 'N/A')}\n"
        output += f"Voltage and Throttle Status: {remote_info.get('Voltage and Throttle Status', 'N/A')}\n"
    else:
        output += "Could not fetch remote system information\n"

    if "0x00001" in local_volt_throttle_status:
        output += "WARNING: Local Under-voltage detected!\n"
    if "0x00004" in local_volt_throttle_status:
        output += "WARNING: Local Throttling active!\n"

    output += "=========================\n"

    return output


class SystemStatusMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Status Monitor")
        self.geometry("600x600")

        self.text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=30)
        self.text_widget.pack()

        self.refresh()

    def refresh(self):
        try:
            output = get_system_info()
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.INSERT, output)
            self.text_widget.config(state=tk.DISABLED)
            self.after(5000, self.refresh)
        except Exception as e:
            self.text_widget.insert(tk.INSERT, f"An error occurred: {e}")
            self.text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = SystemStatusMonitor()
    app.mainloop()
