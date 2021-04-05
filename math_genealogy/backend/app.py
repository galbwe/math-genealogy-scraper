import logging
from typing import List

from fastapi import FastAPI, HTTPException

import math_genealogy.backend.db as db
from .models import PydanticMathematician as Mathematician


# TODO: set up logging config
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# TODO: pagination
# TODO: filter
# TODO: sorting
# TODO: search


@app.get("/mathematicians/{mathematician_id}")
def read_mathematician(mathematician_id: int) -> Mathematician:
    mathematician = db.get_mathematician_by_id(mathematician_id)
    if mathematician:
        return mathematician
    raise HTTPException(status_code=404, detail="Item not found")


# TODO: inserts, fix pg8000 error
@app.post("/mathematicians")
def insert_mathematician(mathematician: Mathematician) -> Mathematician:
    if db.get_mathematician_by_id(mathematician.id):
        raise HTTPException(status_code=409, detail="Item already exists.")
    inserted = db.insert_mathematician(mathematician)
    return inserted


# TODO: updates
@app.put("/mathematicians/{id}")
def update_mathematician(id: int, mathematician: Mathematician) -> Mathematician:
    pass


# TODO: deletes
@app.delete("/mathematicians/{id}")
def delete_mathematician(id: int, mathematician: Mathematician) -> Mathematician:
    pass


@app.get("/mathematicians")
def query_mathematicians() -> List[Mathematician]:
    pass

# relationships
@app.get("/mathematicians/{id}/students")
def get_mathematician_students() -> List[Mathematician]:
    pass


@app.get("/mathematicians/{id}/advisors")
def get_mathematician_advisors() -> List[Mathematician]:
    pass
