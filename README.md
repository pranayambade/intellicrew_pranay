# IntelliCrew

An internal HR web app for employees to manage their skills profile, combined with an AI-powered Text-to-SQL chatbot for querying employee data in natural language.

---

## Features

- **Employee Login** — authenticate with your email and a shared password
- **Skills Dashboard** — select and save your skills from a checkbox dropdown
- **AI Chatbot** — ask natural-language questions about the employee database (powered by LangGraph + Gemini)
- **REST API** — FastAPI backend with session-based auth

---

## Project Structure

```
IntelliCrew-Capstone/
├── app.py                  # FastAPI app entry point
├── config.py               # App configuration
├── requirements.txt        # Python dependencies
├── seed_data.py            # Seed the SQLite database
│
├── api/                    # API route handlers
│   ├── auth.py             # POST /api/login, POST /api/logout
│   ├── skills.py           # GET /api/skills, POST /api/skills/select
│   └── employee.py         # GET/POST /api/employee/skills
│
├── db_chatbot/             # AI chatbot module
│   ├── db.py               # SQLAlchemy engine + run_query() helper
│   ├── agent.py            # LangGraph agent (Text-to-SQL)
│   └── tools.py            # DB schema tool for the agent
│
├── frontend/
│   ├── static/             # CSS files
│   └── templates/          # Jinja2 HTML templates
│       ├── index.html      # AI chatbot UI (home page)
│       ├── login.html      # Login page
│       ├── dashboard.html  # Employee skills dashboard
│       └── skills.html     # Standalone skills page
│
└── data/                   # SQLite database files (gitignored)
```

---

## How It Works

### User Flow

```
/login  →  enter email + password
   ↓
/dashboard  →  view profile, select skills, save to DB
   ↓
/  (home)  →  AI chatbot — ask questions about employees
```

### API Flow

```
POST /api/login          ← { email, password }
                         → saves employee info to session

GET  /api/skills         → list of all skill names from DB
POST /api/employee/skills ← { skill_names: [...] }
                          → saves skills to employees table + skills table

POST /api/query          ← { question: "How many employees are in Engineering?" }
                         → LangGraph agent generates SQL → runs it → returns answer

GET  /api/me             → current logged-in employee info
POST /api/logout         → clears session
```

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/pranayambade/intellicrew_pranay.git
cd intellicrew_pranay
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install itsdangerous langgraph
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Seed the database

```bash
python seed_data.py
```

### 6. Run the app

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**

---

## Login

All employees use the password: `password`

Find an employee email from the database, then log in at `/login`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn |
| Templates | Jinja2 |
| Database | SQLite via SQLAlchemy |
| Sessions | Starlette SessionMiddleware |
| AI Agent | LangGraph + Google Gemini |
| Language | Python 3.12 |
