from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
from db_chatbot.db import run_query

router = APIRouter()


# GET /api/skills - returns list of all unique skill names
@router.get("/api/skills")
def get_skills():
    rows = run_query("SELECT DISTINCT skill_name FROM skills ORDER BY skill_name")
    skill_list = [row["skill_name"] for row in rows]
    return skill_list


# Pydantic model - defines what data the select form sends
class SkillSelectData(BaseModel):
    skill_names: List[str]


# POST /api/skills/select - receives selected skill names, returns their IDs from DB
@router.post("/api/skills/select")
def select_skill(data: SkillSelectData):
    if not data.skill_names:
        return {"error": "No skills selected"}

    # Build SQL: SELECT id, skill_name WHERE skill_name IN ('Python', 'Flask', ...)
    names_in_quotes = ", ".join([f"'{name}'" for name in data.skill_names])
    rows = run_query(f"SELECT id, skill_name FROM skills WHERE skill_name IN ({names_in_quotes})")

    # Map: skill_name -> first matching id
    id_map = {}
    for row in rows:
        if row["skill_name"] not in id_map:
            id_map[row["skill_name"]] = row["id"]

    result = [
        {"skill_id": id_map.get(name), "skill_name": name}
        for name in data.skill_names
    ]
    return {"skills": result}
