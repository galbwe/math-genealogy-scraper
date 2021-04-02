import logging
import reprlib
from typing import Callable, List, Union, Iterable, Optional
import sqlalchemy


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

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
        return PydanticMathematician(**self.as_dict)

    @classmethod
    def from_pydantic(cls, pydantic_model) -> "Mathematician":
        return cls(**pydantic_model.dict())


class StudentAdvisor(BaseModel):
    __tablename__ = 'student_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('mathematician.id'))
    student = relationship("Mathematician", foreign_keys=[student_id])
    advisor_id = Column(Integer, ForeignKey('mathematician.id'))
    advisor = relationship("Mathematician", foreign_keys=[advisor_id])


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# DATA ACCESS
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


engine = create_engine(CONFIG.db_connection)


Session = sessionmaker(bind=engine)


def get_mathematician_by_id(session: Session, id_: int) -> Optional[PydanticMathematician]:
    try:
        q = session.query(Mathematician).filter(Mathematician.id == id_)
        return q.one_or_none()
    except Exception as e:
        session.rollback()
        raise e


def insert_mathematician(session: Session, mathematician: PydanticMathematician) -> PydanticMathematician:
    sqlalchemy_mathematician = Mathematician.from_pydantic(mathematician)
    try:
        session.add(sqlalchemy_mathematician)
    except Exception as e:
        session.rollback()
        raise e
    session.commit()
    return mathematician
