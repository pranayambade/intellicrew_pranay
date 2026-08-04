from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
from db_chatbot.db import engine, run_query
from sqlalchemy import text

router = APIRouter()


# Pydantic model - defines what data the skills save form sends
class SaveSkillsData(BaseModel):
    skill_names: List[str]


# POST /api/employee/skills - save selected skills for the logged-in employee
@router.post("/api/employee/skills")
def save_employee_skills(data: SaveSkillsData, request: Request):
    # Check if user is logged in
    if "employee_id" not in request.session:
        return {"error": "Not logged in"}

    if not data.skill_names:
        return {"error": "No skills selected"}

    emp_id = request.session["employee_id"]

    # Step 1: Get IDs of selected skills from the skills table
    names_in_quotes = ", ".join([f"'{name}'" for name in data.skill_names])
    rows = run_query(f"SELECT id, skill_name FROM skills WHERE skill_name IN ({names_in_quotes})")

    id_map = {}
    for row in rows:
        if row["skill_name"] not in id_map:
            id_map[row["skill_name"]] = row["id"]

    skills_with_ids = [
        {"skill_id": id_map.get(name), "skill_name": name}
        for name in data.skill_names
    ]

    # Step 2: Save skill IDs as comma-separated string in employees table
    skill_ids_str = ",".join(str(s["skill_id"]) for s in skills_with_ids if s["skill_id"])

    with engine.connect() as conn:
        conn.execute(
            text("UPDATE employees SET selected_skill_ids = :ids WHERE id = :emp_id"),
            {"ids": skill_ids_str, "emp_id": emp_id}
        )

        # Step 3: Add a row in skills table linking this employee to each skill (if not already there)
        for s in skills_with_ids:
            if s["skill_id"] is None:
                continue
            already_exists = conn.execute(
                text("SELECT id FROM skills WHERE employee_id = :eid AND skill_name = :sname"),
                {"eid": emp_id, "sname": s["skill_name"]}
            ).fetchone()

            if not already_exists:
                conn.execute(
                    text("INSERT INTO skills (employee_id, skill_name, proficiency) VALUES (:eid, :sname, 'Intermediate')"),
                    {"eid": emp_id, "sname": s["skill_name"]}
                )

        conn.commit()

    return {"message": "Skills saved", "skills": skills_with_ids}


# GET /api/employee/skills - get all skills for the logged-in employee
@router.get("/api/employee/skills")
def get_employee_skills(request: Request):
    if "employee_id" not in request.session:
        return {"error": "Not logged in"}

    emp_id = request.session["employee_id"]
    rows = run_query(f"SELECT id, skill_name, proficiency FROM skills WHERE employee_id = {emp_id} ORDER BY skill_name")
    return rows
