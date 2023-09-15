# RaspiTFTServerStatus - System Animator for Raspberry Pi

## Description

System Animator for Raspberry Pi is a real-time system monitoring tool that displays key metrics for both local and remote Raspberry Pi systems. Designed for the console interface, it provides a visually rich experience through ASCII-based animations and color-coding.

---

## Features

- **Real-Time Monitoring**: Monitor CPU usage, RAM usage, Disk space, and more.
- **Remote Monitoring**: SSH into a remote Raspberry Pi to retrieve and display its system metrics.
- **Service Status Checks**: Determine the status of important system services like SMB.
- **Networking**: Keep an eye on active SSH connections and your internet status.
- **Cool Animations**: Offers ASCII animated text for that hacker aesthetic.
- **Alerts and Warnings**: Receive warnings for local under-voltage and CPU throttling.

---

## Prerequisites

- Python 3.x
- psutil
- paramiko
- Raspberry Pi (for local and optional for remote system)

---

## Installation and Usage

1. **Clone the Repository**
    ```bash
    git clone https://github.com/PKHarsimran/RaspiTFTServerStatus
    ```

2. **Navigate to the Directory**
    ```bash
    cd RaspiTFTServerStatus
    ```

3. **Install Required Packages**
    ```bash
    pip3 install psutil paramiko
    ```

4. **Run the Script**
    ```bash
    python3 main.py
    ```

---

## Contributions

Contributions, issues, and feature requests are welcome. Feel free to open an issue or create a pull request.

