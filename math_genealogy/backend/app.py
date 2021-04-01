from typing import List

from fastapi import FastAPI

from .models import PydanticMathematician as Mathematician


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# TODO: pagination
# TODO: filter
# TODO: sorting
# TODO: search


@app.get("/mathematicians/{id}")
def read_mathematician(id: int) -> Mathematician:
    pass


# TODO: inserts
@app.post("/mathematicians/{id}")
def insert_mathematician(id: int, mathematician: Mathematician) -> Mathematician:
    pass


# TODO: updates
@app.update("/mathematicians/{id}")
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
