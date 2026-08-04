from fastapi import APIRouter, Request
from pydantic import BaseModel
from db_chatbot.db import run_query

router = APIRouter()

# All employees use this password for now
PASSWORD = "password"


# Pydantic model - defines what data the login form sends
class LoginData(BaseModel):
    email: str
    password: str


# POST /api/login - check email + password, save employee info in session
@router.post("/api/login")
def login(data: LoginData, request: Request):
    email = data.email.strip().lower()

    if not email:
        return {"error": "Email is required"}

    if data.password != PASSWORD:
        return {"error": "Incorrect password"}

    # Find employee by email in the database
    rows = run_query(f"SELECT id, name, email, role FROM employees WHERE LOWER(email) = '{email}'")

    if not rows:
        return {"error": "Employee not found"}

    employee = rows[0]

    # Save employee details in session so other pages know who is logged in
    request.session["employee_id"]    = employee["id"]
    request.session["employee_name"]  = employee["name"]
    request.session["employee_email"] = employee["email"]
    request.session["employee_role"]  = employee["role"]

    return {"employee": employee}


# POST /api/logout - clear session
@router.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}
