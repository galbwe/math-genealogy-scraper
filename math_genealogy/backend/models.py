from typing import Optional
from contextlib import contextmanager

from pydantic import BaseModel as PydanticBase, HttpUrl, validator


class PydanticMathematician(PydanticBase):
    id: int
    name: Optional[str]
    school: Optional[str]
    graduated: Optional[int]
    thesis: Optional[str]
    country: Optional[str]
    subject: Optional[str]
    math_genealogy_url: Optional[HttpUrl]
    math_sci_net_url: Optional[HttpUrl]
    publications: Optional[int]
    citations: Optional[int]
