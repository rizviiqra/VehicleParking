
The Vehicle Parking Management System is an academic/demo web-based application designed to manage vehicle parking records efficiently.

🛠 Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, Bootstrap, Jinja2

Database: SQLite

Visualization: Chart.js

APIs: Used for handling data operations

📌Roles & Functionalities

📌Admin (Superuser)

Root access (no registration required, created with DB initialization)

Create, edit, and delete parking lots

Define maximum parking spots in a lot (spots are auto-generated)

Assign different pricing for each lot

View real-time status of all parking spots (available/occupied)

View details of parked vehicles

View and manage all registered users

Summary dashboards & charts for parking usage

📌User

Register & login

Choose an available parking lot

Automatically allocated the first available parking spot (users cannot select spots manually)

Reserve and release spots (updates spot status between Available ↔ Occupied)

Timestamps for parking in/out are recorded

View personal parking history & cost summary

Access charts summarizing their parking activity

📌Core Features

Multi-role login (Admin/User)

Parking lot & spot management system

Automatic parking spot allocation

Parking reservation with entry/exit timestamps

Dynamic dashboards for Admin and Users

Summary charts for insights (powered by Chart.js)

Fully responsive UI with Bootstrap

Database created and initialized programmatically

📌Extended Features

API resources for interaction with lots, spots, or users (Flask-RESTful / JSON responses)

Frontend + backend form validations

Secure login (Flask-Login/Flask-Security integration)

Enhanced styling and user experience

