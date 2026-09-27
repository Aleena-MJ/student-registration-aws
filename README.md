# Student Registration System

A lightweight, beginner-friendly, and modern web application built with **Python 3**, **Flask**, and **SQLite**. The system enables educational administrators and staff to register, view, search, update, and manage student academic records through an intuitive, responsive user interface.

This project is built without unnecessary dependencies or complex frameworks, making it easy to understand, document, and deploy directly to cloud environments like **AWS EC2 (Linux)**.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Local Installation & Setup](#local-installation--setup)
   - [Windows Instructions](#windows-instructions)
   - [macOS / Linux Instructions](#macos--linux-instructions)
6. [Running the Application](#running-the-application)
7. [Accessing in a Web Browser](#accessing-in-a-web-browser)
8. [Database Information](#database-information)
9. [Configuration & Environment Variables](#configuration--environment-variables)
10. [AWS EC2 Linux Deployment Guide](#aws-ec2-linux-deployment-guide)
11. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Features

- **Dashboard / Home**: Real-time summary statistics displaying total registered students, active academic programs, database status, and a list of recently enrolled students.
- **Student Registration**: Add new students with field validation for:
  - Student ID (unique institutional identifier)
  - Full Name
  - Email Address (format & uniqueness validated)
  - Phone Number (length & digits validated)
  - Date of Birth
  - Gender (dropdown selection)
  - Course / Department
  - Year of Study (1st Year through Post-Graduate)
  - Residential / Campus Address
- **Student Directory & Table**: Clean tabular view of all enrolled students with quick action buttons.
- **Instant Search**: Search through student records dynamically by **Student ID**, **Name**, or **Email Address**.
- **Student Profile View**: Dedicated card view showing full personal and academic information, including the registration timestamp.
- **Edit & Update**: Safely modify student information with conflict-detection preventing duplicate ID or email clashes.
- **Delete with Confirmation**: Modal confirmation dialog preventing accidental deletions.
- **Automatic Database Initialization**: Automatically creates `database.db` and the `students` table on initial run—zero manual SQL setup needed.
- **Responsive Interface**: Built with mobile-friendly Bootstrap 5 and custom CSS for smooth performance on desktop, tablet, and mobile browsers.

---

## Technologies Used

- **Backend**: Python 3, Flask
- **Database**: SQLite (via standard Python `sqlite3` module)
- **Frontend / Templates**: HTML5, CSS3, Jinja2 template engine
- **Styling**: Bootstrap 5.3 (CDN), Bootstrap Icons, Custom CSS
- **WSGI / Server**: Flask built-in development server (deployment-ready with host `0.0.0.0` or standard WSGI servers like Gunicorn)

---

## Project Structure

```text
student-registration/
│
├── app.py                  # Main Flask application and routing logic
├── requirements.txt        # Python package dependencies
├── database.db             # SQLite database file (auto-generated on first run)
├── README.md               # Complete setup, usage, and EC2 deployment guide
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with responsive navbar, alerts, footer
│   ├── index.html          # Dashboard with overview metrics & recent students
│   ├── register.html       # Student registration form
│   ├── students.html       # Student directory table with search & delete modal
│   ├── student_details.html# Comprehensive single-student profile view
│   └── edit_student.html   # Student edit form with pre-populated values
│
└── static/
    └── style.css           # Custom styling for cards, tables, and responsiveness
```

---

## Prerequisites

- **Python 3.8+** installed on your system.
- `pip` (Python package manager).

Verify your installation in a terminal:
```bash
python --version
# or on Linux/macOS
python3 --version
```

---

## Local Installation & Setup

### Windows Instructions

1. **Open PowerShell or Command Prompt** and navigate to the project directory:
   ```powershell
   cd path\to\student-registration
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - In PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - In Command Prompt (`cmd`):
     ```cmd
     .\.venv\Scripts\activate.bat
     ```

4. **Install required dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

---

### macOS / Linux Instructions

1. **Open your terminal** and navigate to the project folder:
   ```bash
   cd path/to/student-registration
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

4. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

Once your virtual environment is active, start the application:

```bash
python app.py
```

You should see terminal output similar to:
```text
Starting Student Registration App on http://0.0.0.0:5000 (Debug: False)
 * Serving Flask app 'app'
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://<local-ip>:5000
```

---

## Accessing in a Web Browser

Open your favorite web browser and navigate to:
```text
http://localhost:5000
```
or
```text
http://127.0.0.1:5000
```

---

## Database Information

- **Database Engine**: SQLite 3.
- **Database File**: `database.db` located in the root of the project.
- **Automatic Setup**: The function `init_db()` runs automatically on startup. If `database.db` does not exist, it will create it and execute the table schema.
- **Table Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS students (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id TEXT UNIQUE NOT NULL,
      full_name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      phone TEXT NOT NULL,
      dob TEXT NOT NULL,
      gender TEXT NOT NULL,
      course TEXT NOT NULL,
      year TEXT NOT NULL,
      address TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
- **Security**: All SQL operations use parameterized queries (`?` parameter markers) to protect against SQL Injection.

---

## Configuration & Environment Variables

The application comes with sensible defaults for development and deployment, which can be overridden via environment variables if desired:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PORT` | Network port for the Flask server | `5000` |
| `FLASK_HOST` | Network interface to bind to | `0.0.0.0` |
| `FLASK_DEBUG` | Enable debug mode (`True` / `False`) | `False` |
| `SECRET_KEY` | Secret key for Flask session & flash messages | Built-in default |

Example of running on port 8080:
```bash
# Linux/macOS
PORT=8080 python app.py

# Windows PowerShell
$env:PORT="8080"; python app.py
```

---

## AWS EC2 Linux Deployment Guide

Follow these steps to deploy this application to an **AWS EC2 Linux instance** (such as Amazon Linux 2023 or Ubuntu 22.04 LTS, `t3.micro` instance in `eu-north-1`):

### Step 1: Configure AWS Security Group
Before launching or connecting, ensure your EC2 instance's **Security Group** permits inbound traffic on the port your application will run on:
1. In the AWS Management Console, navigate to **EC2** > **Security Groups**.
2. Select the Security Group attached to your EC2 instance.
3. Under **Inbound rules**, click **Edit inbound rules**.
4. Add the following rules:
   - **SSH**: Type `SSH`, Port `22`, Source `My IP` (for secure administration).
   - **Flask Port**: Type `Custom TCP`, Port `5000`, Source `Anywhere-IPv4` (`0.0.0.0/0`) or specific IP range.
   - *(Optional if using Nginx reverse proxy)*: Type `HTTP`, Port `80`, Source `0.0.0.0/0`.
5. Click **Save rules**.

---

### Step 2: Transfer Files to EC2 Instance
You can upload the project files using `scp` (Secure Copy Protocol) from your local computer:

```bash
# From your local machine terminal:
scp -i /path/to/your-key.pem -r student-registration ec2-user@<EC2-PUBLIC-IP>:~/
# (Replace ec2-user with ubuntu if using an Ubuntu AMI)
```

Alternatively, you can push the project to a private Git repository (e.g. GitHub/GitLab) and run `git clone <repo-url>` on the EC2 instance.

---

### Step 3: Connect to Your EC2 Instance
```bash
ssh -i /path/to/your-key.pem ec2-user@<EC2-PUBLIC-IP>
```

---

### Step 4: Install Python & Setup Environment on EC2
On Amazon Linux 2023:
```bash
# Update packages
sudo dnf update -y

# Install Python 3 and pip
sudo dnf install -y python3 python3-pip

# Navigate into the project folder
cd ~/student-registration

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

*(If using Ubuntu, use `sudo apt update && sudo apt install -y python3 python3-pip python3-venv`)*.

---

### Step 5: Run the Application on EC2

#### Option A: Quick Test / Background Execution with `nohup`
```bash
# Start Flask in the background
nohup python app.py > app.log 2>&1 &

# Verify it is running
ps aux | grep app.py
```

#### Option B: Production Service with `systemd` (Recommended)
Creating a systemd service ensures the app starts automatically upon server reboots:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/student-registration.service
   ```
2. Paste the following configuration:
   ```ini
   [Unit]
   Description=Flask Student Registration System
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/student-registration
   Environment="PATH=/home/ec2-user/student-registration/.venv/bin"
   ExecStart=/home/ec2-user/student-registration/.venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   *(Adjust username `/home/ec2-user` if running as `ubuntu`).*

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start student-registration
   sudo systemctl enable student-registration
   ```

4. Check status:
   ```bash
   sudo systemctl status student-registration
   ```

---

### Step 6: Access Your Live Application
In any web browser, visit:
```text
http://<YOUR-EC2-PUBLIC-IP>:5000
```
*(Example: `http://13.51.100.25:5000`)*

---

## Troubleshooting & FAQ

- **Cannot access `http://<EC2-PUBLIC-IP>:5000` from browser**:
  Check AWS EC2 **Security Group** inbound rules. Ensure Custom TCP port 5000 is open to `0.0.0.0/0`.
- **Database Permission Errors on Linux**:
  Ensure the directory and `database.db` are owned by the active user running the app (`chown -R ec2-user:ec2-user ~/student-registration`).
- **Reset Database**:
  Simply delete `database.db` and restart the application. The system will create a fresh, clean database automatically.
