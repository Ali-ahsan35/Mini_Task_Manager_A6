# TaskFlow — Task Manager (Flask + SQLite)

TaskFlow is a simple and practical task management system built with **Flask**, **SQLite**, and **SQLAlchemy**.  
It provides a REST API for creating and managing tasks and a clean web interface to view tasks.

---

## Features

- Create, read, update, and delete tasks (CRUD)
- Task fields: **title**, **description**, **status**, **due_date**
- Status workflow: **todo → in_progress → done**
- API supports:
  - Filter by status
  - Search by keyword (title/description)
  - Sort by `created_at` or `due_date`
  - Order by `asc` / `desc`
- Web UI:
  - View tasks
  - Filter + sort + order
  - Move tasks between statuses

---

## Tech Stack

- Python 3.x
- Flask
- Flask-SQLAlchemy
- SQLite
- Logging (Rotating file logs)

---

## Project Structure (recommended)

```
task_manager/
├── app.py
├── requirements.txt
├── instance/
│ └── task_manager.db # auto-created at runtime
├── logs/
│ ├── init.py
│ ├── logger.py
│ └── app.log         # auto-created at runtime
├── templates/
│ ├── home.html
│ └── tasks.html
└── static/
└── style.css
```

---

## Requirements

- Python 3.10+ recommended
- `pip` installed

---

## Setup Instructions

### 1) Clone the project
```bash
git clone <YOUR_REPO_URL>
cd task_manager
```

### 2) Create and activate a virtual environment
#### Linux / macOS
```
python3 -m venv .venv
source .venv/bin/activate
```
#### Windows (PowerShell)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
```
pip install -r requirements.txt
```
### 4) Run the application
```
python app.py
```
#### You should see output like:
- Database tables created
- Server running on http://127.0.0.1:5000
---
### Running the App
### Web Interface
- Home: http://127.0.0.1:5000/
- Tasks: http://127.0.0.1:5000/tasks

### API Base URL
- http://127.0.0.1:5000/api

---
### Database (SQLite)
#### SQLite database file is stored here:
```
instance/task_manager.db
```
### The database and tables are created automatically when you run:
```
python app.py
```
---
### Logging
#### Logs are witten to :
```
logs/app.log
```
#### The logger uses rotating logs to prevent the file from growing too large.
---
### API Documentation (Postman Testing Guide)
#### Important Postman Setup
#### For requests with a JSON body, set:
- Header: Content-Type: application/json
- Body: raw → JSON
---
### 1) Create a Task
#### Endpoint
```
POST /api/tasks
```
### Example (Postman)
#### URL
```
http://127.0.0.1:5000/api/tasks
```
### Body (raw JSON)
```
{
  "title": "Complete Assignment",
  "description": "Finish Flask TaskFlow project",
  "status": "todo",
  "due_date": "2026-02-10"
}
```
### Response
- 201 Created
- returns created task object with id
---
### 2) List All Tasks
#### Endpoint
```
GET /api/tasks
```
### URL
```
http://127.0.0.1:5000/api/tasks
```
### Response
- 200 OK
- returns an array of tasks
---
### 3) Filter Tasks by Status
#### Endpoint
```
GET /api/tasks?status=<status>
```
#### Valid statuses:
- todo
- in_progress
- done

#### Example
```
http://127.0.0.1:5000/api/tasks?status=todo
```
---
### 4) Search Tasks (title + description)
#### Endpoint
```
GET /api/tasks?q=<keyword>
```
#### Example
```
http://127.0.0.1:5000/api/tasks?q=Flask
``
---
### 3) Sort Tasks
#### Endpoint
```
GET /api/tasks?sort=<field>&order=<asc|desc>
```
#### Valid sort fields:
- created_at
- due_date

#### Example
```
http://127.0.0.1:5000/api/tasks?status=todo
```
### Valid order values:

- asc

- desc
---