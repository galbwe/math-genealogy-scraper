import logging
import re
import reprlib
from datetime import date
from typing import List, Union, Dict, Optional
from pydantic.networks import url_regex

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import or_, Column, Integer, String, ForeignKey, create_engine, Date

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


MATHEMATICIAN_FIELDS = {
    'id': Mathematician.id,
    'name': Mathematician.name,
    'school': Mathematician.school,
    'graduated': Mathematician.graduated,
    'thesis': Mathematician.thesis,
    'country': Mathematician.country,
    'subject': Mathematician.subject,
    'math_genealogy_url': Mathematician.math_genealogy_url,
    'math_sci_net_url': Mathematician.math_sci_net_url,
    'publications': Mathematician.publications,
    'citations': Mathematician.citations,
}


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


def update_mathematician(id_: int, mathematician: PydanticMathematician) -> Optional[PydanticMathematician]:
    mathematician.id = id_
    session = Session()
    update_data = Mathematician.from_pydantic(mathematician).as_dict
    db_mathematician = session.query(Mathematician).filter(Mathematician.id == id_).one_or_none()
    if not db_mathematician:
        return None
    try:
        for key, value in update_data.items():
            setattr(db_mathematician, key, value)
        session.commit()
        return db_mathematician.as_pydantic
    except Exception as e:
        session.rollback()
        raise e


def delete_mathematician(id_: int) -> Optional[Mathematician]:
    session = Session()
    db_mathematician = session.query(Mathematician).filter(Mathematician.id == id_).one_or_none()
    if not db_mathematician:
        return None
    deleted = db_mathematician.as_pydantic
    student_advisor_relationships = (
        session.query(StudentAdvisor)
        .filter(or_(
            StudentAdvisor.student_id == id_,
            StudentAdvisor.advisor_id == id_,
        ))
    )
    try:
        for rel in student_advisor_relationships:
            session.delete(rel)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    try:
        session.delete(db_mathematician)
        session.commit()
        return deleted
    except Exception as e:
        session.rollback()
        for rel in student_advisor_relationships:
            session.add(rel)
        session.commit()
        raise e


def get_students(id_: int) -> List[Mathematician]:
    session = Session()
    student_ids = session.query(StudentAdvisor.student_id).filter(StudentAdvisor.advisor_id == id_)
    students = session.query(Mathematician).filter(Mathematician.id.in_(student_ids))
    return [
        student.as_pydantic
        for student in students
    ]


def get_advisors(id_: int) -> List[Mathematician]:
    session = Session()
    advisor_ids = session.query(StudentAdvisor.advisor_id).filter(StudentAdvisor.student_id == id_)
    advisors = session.query(Mathematician).filter(Mathematician.id.in_(advisor_ids))
    return [
        advisor.as_pydantic
        for advisor in advisors
    ]


def get_mathematicians(page: int, perpage: int, fields: List[str]) -> List[Dict]:
    session = Session()
    # TODO: validate inputs
    columns = (MATHEMATICIAN_FIELDS.get(field) for field in fields)
    query = session.query(*[column for column in columns if column is not None])
    start_idx = (page - 1) * perpage
    end_idx = start_idx + perpage
    records = query[start_idx:end_idx]
    return [
        dict(record)
        for record in records
    ]