from contextlib import contextmanager
from datetime import datetime

from pydantic import BaseModel as PydanticBase, HttpUrl


class PydanticMathematician(PydanticBase):
    id: int
    name: str
    school: str
    graduated: datetime
    thesis: str
    country: str
    subject: str
    math_genealogy_url: HttpUrl
    math_sci_net_url: HttpUrl
    publications: int
    citations: int
