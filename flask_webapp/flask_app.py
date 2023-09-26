from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
Session = sessionmaker(bind=engine)
session = Session()

# Define your SQLAlchemy models
Base = declarative_base()

class Class(Base):
    __tablename__ = 'class'
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100))

class Teacher(Base):
    __tablename__ = 'teacher'
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_name = Column(String(100), unique=True)
    password = Column(String(100), default='teacher_login')

class ClassSchedule(Base):
    __tablename__ = 'class_schedule'
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    module = Column(String(100))
    class_name = Column(String(100), ForeignKey('class.class_name'), nullable=False)
    trainer_name = Column(String(100), ForeignKey('teacher.teacher_name'), nullable=False)
    class_total = Column(Integer)

class Student(Base):
    __tablename__ = 'student'
    student_id = Column(String(100), primary_key=True)
    password = Column(String(100), default='student_login')
    course_enrolled = Column(String(100))
    attendance = Column(Integer)
    last_name = Column(String(100))
    first_name = Column(String(100))
    preferred_name = Column(String(100))

class StudentClass(Base):
    __tablename__ = 'student_class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(100), ForeignKey('student.student_id'), nullable=False)
    notes = Column(String, nullable=True)
    date = Column(Date)
    class_name = Column(String(100), ForeignKey('class.class_name'), nullable=False)
    trainer_name = Column(String(100), ForeignKey('teacher.teacher_name'), nullable=False)
    morning_break_status = Column(String(20))
    morning_break_hours = Column(Float)
    lunch_break_status = Column(String(20))
    lunch_break_hours = Column(Float)
    tea_break_status = Column(String(20))
    tea_break_hours = Column(Float)
    final_session_status = Column(String(20))
    final_session_hours = Column(Float)
    total_class_hours = Column(Float)


# Create the database tables
Base.metadata.create_all(engine)
