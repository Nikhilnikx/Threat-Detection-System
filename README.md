# 🛡️ Threat Detection System (SOC Monitoring Platform)

A Flask-based **Security Operations Center (SOC) threat detection platform** designed to analyze security logs, detect suspicious activities, generate alerts, and provide an interactive dashboard for security monitoring.

The system simulates a lightweight SIEM (Security Information and Event Management) platform with capabilities such as log ingestion, threat event analysis, risk scoring, alert management, and security investigation workflows.

---

# 🚀 Features Implemented

## 🔐 User Authentication

- Secure user registration and login
- Password hashing using Werkzeug security
- Session management using Flask-Login
- CSRF protection for API requests
- Login rate limiting to prevent brute-force attempts

---

# 📊 Security Dashboard

Interactive dashboard providing:

- Total security events
- Open alerts count
- Critical threat count
- Risk severity breakdown
- Recent security events
- Recent alerts

The dashboard automatically fetches updated security statistics using REST APIs.

---

# 📂 Security Log Upload & Processing

Supports uploading:

- `.log`
- `.txt`
- `.csv`

The system:

1. Accepts security log files
2. Parses raw log data
3. Normalizes events into structured records
4. Stores logs for investigation
5. Generates threat events

Supported extracted fields:

- Timestamp
- Source IP address
- Username
- Action
- Status
- Raw log information

---

# 🔍 Log Parsing Engine

The parser supports:

### CSV Logs

Automatically detects columns such as:

- timestamp
- source_ip / ip
- username / user
- action
- status


### Text Logs

Supports:

- Apache-style logs
- Syslog-style logs
- Generic authentication logs


Unrecognized logs are still stored to maintain an audit trail.

---

# ⚠️ Threat Detection Engine

Implemented detection capabilities:

## Brute Force Attack Detection

Detects multiple failed login attempts from the same IP address.

Example:

```
10.0.0.55
Failed login
Failed login
Failed login
Failed login
```

Detection result:

```
Threat:
Brute Force Attack

Risk Score:
90/100

Severity:
High
```

---

# 🎯 Risk Scoring System

Every threat event receives a risk score.

Risk levels:

| Risk Score | Severity |
|------------|----------|
| 0-30 | Low |
| 31-60 | Medium |
| 61-90 | High |
| 91-100 | Critical |

High-risk events automatically generate alerts.

---

# 🚨 Alert Management System

The platform automatically creates alerts from detected threats.

Alert features:

- Alert creation
- Alert severity tracking
- Risk score display
- Alert investigation page
- Alert status updates


Supported statuses:

```
Open
Acknowledged
Resolved
```

Example workflow:

```
Threat Event
      |
      ↓
Detection Engine
      |
      ↓
Alert Generated
      |
      ↓
Investigation
      |
      ↓
Resolve Alert
```

---

# 🔎 Event Investigation

Each security event has a dedicated investigation page showing:

- Event type
- Source IP
- Severity
- Risk score
- Description
- Timestamp

---

# 🏗️ System Architecture

```
                 User
                  |
                  ↓
          Flask Web Application
                  |
     ----------------------------
     |            |             |
 Authentication  Dashboard   Upload System
                  |
                  ↓
           Log Parser Engine
                  |
                  ↓
          Threat Detection Engine
                  |
                  ↓
             Risk Scoring
                  |
                  ↓
              Alert System
                  |
                  ↓
            Investigation
```

---

# 🛠️ Technology Stack

## Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- REST APIs


## Database

- SQLite
- SQLAlchemy ORM


## Frontend

- HTML5
- CSS3
- JavaScript


## Security

- Password hashing
- CSRF protection
- Session authentication
- Rate limiting

---

# 📁 Project Structure

```
threat-detection-system/

│
├── app.py
├── monitoring.py
│
├── models/
│   ├── user.py
│   ├── alert.py
│   ├── event.py
│   └── log_entry.py
│
├── detector/
│   ├── parser.py
│   ├── analyzer.py
│   ├── alerts.py
│   └── rules.py
│
├── routes/
│   ├── auth_routes.py
│   ├── alert_routes.py
│   ├── event_routes.py
│   └── upload_routes.py
│
├── templates/
│
├── static/
│
└── instance/
```

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/Nikhilnikx/Threat-Detection-System.git
```

Move into project:

```bash
cd Threat-Detection-System
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Application

```bash
flask run
```

Application starts:

```
http://127.0.0.1:5000
```

---

# 👤 Login

Register a new account using:

```
/register
```

or use an existing user.

Login provides access to:

- Dashboard
- Log upload
- Events
- Alerts

---

# 📥 Testing Log Detection

Upload a CSV file containing failed login attempts.

Example:

```csv
timestamp,source_ip,username,action,status

2026-08-14 10:00:01,10.0.0.55,admin,login,failed
2026-08-14 10:00:02,10.0.0.55,admin,login,failed
2026-08-14 10:00:03,10.0.0.55,admin,login,failed
2026-08-14 10:00:04,10.0.0.55,admin,login,failed
```

Result:

```
Brute Force Attack Detected

Severity:
High

Risk:
90
```

An alert will automatically appear on the dashboard.

---

# 🧪 Current Development Status

## Completed

✅ Authentication System  
✅ Dashboard  
✅ Log Upload  
✅ Log Parser  
✅ Threat Events  
✅ Risk Scoring  
✅ Brute Force Detection  
✅ Alert Generation  
✅ Alert Investigation  
✅ Alert Resolution Workflow  


## Future Improvements

Planned:

- MITRE ATT&CK technique mapping
- Threat intelligence API integration
- IP reputation lookup
- Malware log detection
- Machine learning anomaly detection
- Email notifications
- PDF security reports
- Advanced analytics dashboard

---

# 📈 Project Goal

The goal of this project is to build a practical SOC monitoring platform that demonstrates:

- Security event monitoring
- Threat detection concepts
- Incident response workflow
- Blue Team operations
- SIEM fundamentals

---

# 👨‍💻 Author

**Nikhil Singh**

Computer Science Engineering Student

Cybersecurity | Blue Team | Security Operations
