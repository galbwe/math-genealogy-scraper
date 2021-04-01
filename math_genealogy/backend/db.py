from typing import Callable, List, Union


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine


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


class SQLAlchemyMathematician(BaseModel):
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


class SQLAlchemyStudentAdvisor(BaseModel):
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


def query(q: Callable[..., QueryResult]):

    def _decorated(session: Session, *args, **kwargs):
        try:
            q(session, *args, **kwargs)
            session.commit()
        except Exception as e:
            session.rollback()

    return _decorated
