import logging
from typing import List

from fastapi import FastAPI, HTTPException

from .models import PydanticMathematician as Mathematician
from .db import get_mathematician_by_id, Session


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
    session = Session()
    mathematician = get_mathematician_by_id(session, mathematician_id)
    if mathematician:
        return mathematician
    raise HTTPException(status_code=404, detail="Item not found")


# TODO: inserts, fix pg8000 error
@app.post("/mathematicians/{mathematician_id}")
def insert_mathematician(mathematician_id: int, mathematician: Mathematician) -> Mathematician:
    session = Session()
    if get_mathematician_by_id(session, mathematician_id):
        raise HTTPException(status_code=409, detail="Item already exists.")
    if mathematician_id != mathematician.id:
        logger.warning("Path id %s was not equal to id %s found in object. Using path id and discarding object id.", mathematician_id, mathematician.id)
        mathematician.id = mathematician_id
    inserted = insert_mathematician(session, mathematician)
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
