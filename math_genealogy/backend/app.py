import logging
from typing import List, Dict

from fastapi import FastAPI, HTTPException

import math_genealogy.backend.db as db
from .models import PydanticMathematician as Mathematician


# TODO: set up logging config
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/mathematicians/{mathematician_id}")
def read_mathematician(mathematician_id: int) -> Mathematician:
    mathematician = db.get_mathematician_by_id(mathematician_id)
    if mathematician:
        return mathematician
    raise HTTPException(status_code=404, detail='Item not found')


# TODO: inserts, fix pg8000 error
@app.post("/mathematicians")
def insert_mathematician(mathematician: Mathematician) -> Mathematician:
    if db.get_mathematician_by_id(mathematician.id):
        raise HTTPException(status_code=409, detail="Item already exists.")
    inserted = db.insert_mathematician(mathematician)
    return inserted


# TODO: updates
@app.put("/mathematicians/{mathematician_id}")
def update_mathematician(mathematician_id: int, mathematician: Mathematician) -> Mathematician:
    updated = db.update_mathematician(mathematician_id, mathematician)
    if updated is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return updated


# TODO: deletes
@app.delete("/mathematicians/{mathematician_id}")
def delete_mathematician(mathematician_id: int) -> Mathematician:
    deleted = db.delete_mathematician(mathematician_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return deleted


@app.get("/fields/mathematicians")
def get_mathematician_field_names() -> List[str]:
    return list(db.MATHEMATICIAN_FIELDS)


# TODO: sorting
# TODO: search
@app.get("/mathematicians")
def query_mathematicians(page: int = 1, perpage: int = 100, fields: str = '*') -> List[Dict]:
    if fields != '*':
        fields = [field.strip() for field in fields.split(',')]
    return db.get_mathematicians(page, perpage, fields)


# relationships
@app.get("/mathematicians/{mathematician_id}/students")
def get_mathematician_students(mathematician_id: int) -> List[Mathematician]:
    if not db.get_mathematician_by_id(mathematician_id):
        raise HTTPException(status_code=404, detail='Item not found')
    return db.get_students(mathematician_id)


@app.get("/mathematicians/{mathematician_id}/advisors")
def get_mathematician_advisors(mathematician_id: int) -> List[Mathematician]:
    if not db.get_mathematician_by_id(mathematician_id):
        raise HTTPException(status_code=404, detail='Item not found')
    return db.get_advisors(mathematician_id)