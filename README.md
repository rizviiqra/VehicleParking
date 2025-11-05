![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![Chart.js](https://img.shields.io/badge/Chart.js-Data%20Viz-orange)
![HTML](https://img.shields.io/badge/HTML-5-red)
![CSS](https://img.shields.io/badge/CSS-3-blue)
![Jinja2](https://img.shields.io/badge/Jinja2-Template-yellow)
![REST-API](https://img.shields.io/badge/REST-API-brightgreen)


The Vehicle Parking Management System is a full-stack, academic/demo web application designed to efficiently manage vehicle parking workflows. It supports both Admin and User roles, enabling creation and monitoring of parking lots, automated spot allocation, and parking activity tracking. The system features secure authentication, dynamic dashboards, and interactive analytical charts to enhance usability and provide meaningful insights.

<img width="1897" height="901" alt="image" src="https://github.com/user-attachments/assets/3a4cdebf-c301-46e4-aef7-a7dc8fbb072e" />


# Installation and Setup

```bash
# Clone repository
git clone https://github.com/rizviiqra/VehicleParking
cd repo-name

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python db.py

# Run the application
python app.py
```

# 🛠 Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, Bootstrap, Jinja2

Database: SQLite

Visualization: Chart.js

APIs: Used for handling data operations

# Roles & Functionalities

### 📌Admin (Superuser)

Root access (no registration required, created with DB initialization)

Create, edit, and delete parking lots

Define maximum parking spots in a lot (spots are auto-generated)

Assign different pricing for each lot

View real-time status of all parking spots (available/occupied)

View details of parked vehicles

View and manage all registered users

Summary dashboards & charts for parking usage

### 📌User

Register & login

Choose an available parking lot

Automatically allocated the first available parking spot (users cannot select spots manually)

Reserve and release spots (updates spot status between Available ↔ Occupied)

Timestamps for parking in/out are recorded

View personal parking history & cost summary

Access charts summarizing their parking activity

### 📌Core Features

Multi-role login (Admin/User)

Parking lot & spot management system

Automatic parking spot allocation

Parking reservation with entry/exit timestamps

Dynamic dashboards for Admin and Users

Summary charts for insights (powered by Chart.js)

Fully responsive UI with Bootstrap

Database created and initialized programmatically

### 📌Extended Features

API resources for interaction with lots, spots, or users (Flask-RESTful / JSON responses)

Frontend + backend form validations

Secure login (Flask-Login/Flask-Security integration)

Enhanced styling and user experience

# Screenshots

<img width="1902" height="893" alt="image" src="https://github.com/user-attachments/assets/0f7fc547-14de-466a-90c1-0b5e0df449c6" />

<img width="1885" height="904" alt="image" src="https://github.com/user-attachments/assets/6e77ebd9-f238-45af-9a69-f54739b58fab" />

<img width="1853" height="926" alt="image" src="https://github.com/user-attachments/assets/c64944ff-0e74-411c-b1da-3ca0c28d06a8" />

<img width="1899" height="891" alt="image" src="https://github.com/user-attachments/assets/90a026a5-0773-4d4c-ab5d-1982d1e588aa" />

