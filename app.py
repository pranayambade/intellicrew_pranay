import secrets
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

from db_chatbot.agent import ask_agent
from db_chatbot.tools import schema_tool
from api.auth import router as auth_router
from api.skills import router as skills_router
from api.employee import router as employee_router

app = FastAPI(title="IntelliCrew")

app.add_middleware(SessionMiddleware, secret_key="intellicrew-secret-key")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(employee_router)


class QueryRequest(BaseModel):
    question: str


# ---------- Page routes ----------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if "employee_id" not in request.session:
        return RedirectResponse(url="/login")
    userType = request.session.get("employee_role", "employee")
    return templates.TemplateResponse(request, "index.html", {"userType": userType})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    if "employee_id" not in request.session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/skills", response_class=HTMLResponse)
def skills_page(request: Request):
    return templates.TemplateResponse(request, "skills.html")


# ---------- API routes ----------

@app.get("/api/me")
def me(request: Request):
    if "employee_id" not in request.session:
        return {"error": "Not logged in"}
    return {
        "id":    request.session["employee_id"],
        "name":  request.session.get("employee_name", ""),
        "email": request.session.get("employee_email", ""),
        "role":  request.session.get("employee_role", ""),
    }


@app.post("/api/query")
def query(req: QueryRequest):
    if not req.question.strip():
        return {"error": "Please enter a question."}
    return ask_agent(req.question)


@app.get("/api/schema")
def schema():
    return {"schema": schema_tool()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
