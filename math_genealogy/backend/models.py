from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey


Base = declarative_base()


class Mathematician(Base):
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


class StudentAdvisor(Base):
    __tablename__ = 'student_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('mathematician.id'))
    student = relationship("Mathematician", foreign_keys=[student_id])
    advisor_id = Column(Integer, ForeignKey('mathematician.id'))
    advisor = relationship("Mathematician", foreign_keys=[advisor_id])