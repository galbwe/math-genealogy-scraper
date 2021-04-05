import logging
import re
import reprlib
from datetime import date
from typing import Callable, List, Union, Iterable, Optional
from pydantic.networks import url_regex

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Date

from .models import PydanticMathematician


logger = logging.getLogger(__name__)


from ..config import CONFIG


BaseModel = declarative_base()


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# TYPES
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


QueryResult = Union[BaseModel, List[BaseModel]]


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# DATA MODEL
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


class Mathematician(BaseModel):
    __tablename__ = 'mathematician'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    school = Column(String)
    graduated = Column(String)
    thesis = Column(String)
    country = Column(String)
    subject = Column(String)
    math_genealogy_url = Column(String)
    math_sci_net_url = Column(String)
    publications = Column(Integer)
    citations = Column(Integer)

    @property
    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            school=self.school,
            graduated=self.graduated,
            thesis=self.thesis,
            country=self.country,
            subject=self.subject,
            math_genealogy_url=self.math_genealogy_url,
            math_sci_net_url=self.math_sci_net_url,
            publications=self.publications,
            citations=self.citations,
        )

    @property
    def as_pydantic(self) -> PydanticMathematician:
        data = self.as_dict
        graduated = data.get('graduated')
        if graduated is None:
            data['graduated'] = graduated
        else:
            m = re.match(r'(^\d{4})-', graduated)
            if m:
                graduated = m.group(1)
            data['graduated'] = int(graduated)
        return PydanticMathematician(**data)

    @classmethod
    def from_pydantic(cls, pydantic_model) -> "Mathematician":
        data = pydantic_model.dict()

        graduated = data.get('graduated')
        data['graduated'] = graduated if graduated is None else str(graduated)

        data['math_genealogy_url'] = _convert_pydantic_http_url_to_string(
            data.get('math_genealogy_url')
        )

        data['math_sci_net_url'] = _convert_pydantic_http_url_to_string(
            data.get('math_sci_net_url')
        )

        return cls(**data)

    def __repr__(self):
        name = self.__class__.__name__
        args = ', '.join([f"{k}={v!r}" for (k, v) in self.as_dict.items()])
        return f"{name}({args})"


def _convert_pydantic_http_url_to_string(http_url):
    if http_url is None:
        return http_url
    return str(http_url)


class StudentAdvisor(BaseModel):
    __tablename__ = 'student_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('mathematician.id'))
    advisor_id = Column(Integer, ForeignKey('mathematician.id'))


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# DATA ACCESS
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


engine = create_engine(CONFIG.db_connection)


Session = sessionmaker(bind=engine)


def get_mathematician_by_id(id_: int) -> Optional[PydanticMathematician]:
    """
    Return a mathematician from the database with a given id.
    """
    session = Session()
    try:
        q = session.query(Mathematician).filter(Mathematician.id == id_)
        model = q.one_or_none()
        if model is None:
            return model
        return model.as_pydantic
    except Exception as e:
        session.rollback()
        raise e


def insert_mathematician(mathematician: PydanticMathematician) -> PydanticMathematician:
    session = Session()
    sqlalchemy_mathematician = Mathematician.from_pydantic(mathematician)
    try:
        session.add(sqlalchemy_mathematician)
        session.commit()
        return sqlalchemy_mathematician.as_pydantic
    except Exception as e:
        session.rollback()
        raise e
