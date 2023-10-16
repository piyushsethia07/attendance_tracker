# test_app.py

from flask_app import Class, Teacher, Student, Module, ClassSchedule, StudentClass
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

# Fixture to create a session for each test
import pytest

@pytest.fixture
def session():
    engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
    Session = sessionmaker(bind=engine)
    return Session()

# Test Class model
def test_class_model(session):
    # Create a Class instance
    class_instance = Class(class_name="Test Class")
    session.add(class_instance)
    session.commit()
    
    # Retrieve and verify the class
    retrieved_class = session.query(Class).filter_by(class_name="Test Class").first()
    assert retrieved_class is not None
    assert retrieved_class.class_name == "Test Class"

# Test Teacher model
def test_teacher_model(session):
    # Create a Teacher instance
    teacher_instance = Teacher(teacher_name="Test Teacher")
    session.add(teacher_instance)
    session.commit()

    # Retrieve and verify the teacher
    retrieved_teacher = session.query(Teacher).filter_by(teacher_name="Test Teacher").first()
    assert retrieved_teacher is not None
    assert retrieved_teacher.teacher_name == "Test Teacher"

# Test Student model
def test_student_model(session):
    # Create a Student instance
    student_instance = Student(student_id="TestStudentID", first_name="John", last_name="Doe")
    session.add(student_instance)
    session.commit()

    # Retrieve and verify the student
    retrieved_student = session.query(Student).filter_by(student_id="TestStudentID").first()
    assert retrieved_student is not None
    assert retrieved_student.first_name == "John"
    assert retrieved_student.last_name == "Doe"

# Test Module model
def test_module_model(session):
    # Create a Module instance
    module_instance = Module(module_name="Test Module")
    session.add(module_instance)
    session.commit()

    # Retrieve and verify the module
    retrieved_module = session.query(Module).filter_by(module_name="Test Module").first()
    assert retrieved_module is not None
    assert retrieved_module.module_name == "Test Module"

# Test ClassSchedule model
def test_class_schedule_model(session):
    # Create a ClassSchedule instance
    date = datetime.strptime("2023-10-14", "%Y-%m-%d")
    class_schedule_instance = ClassSchedule(
        date=date,
        module="Test Module",
        class_name="Test Class",
        trainer_name="Test Teacher",
        class_total=20
    )
    session.add(class_schedule_instance)
    session.commit()

    # Retrieve and verify the class schedule
    retrieved_schedule = session.query(ClassSchedule).filter_by(module = "Test Module").first()
    assert retrieved_schedule is not None
    assert retrieved_schedule.module == "Test Module"
    assert retrieved_schedule.class_name == "Test Class"
    assert retrieved_schedule.trainer_name == "Test Teacher"
    assert retrieved_schedule.class_total == 20


def test_student_class_model(session):
    # Create a StudentClass instance
    student_class_instance = StudentClass(
        student_id="TestStudentID",
        notes="Test notes",
        date=datetime.strptime("2023-10-14", "%Y-%m-%d").date(),
        class_name="Test Class",
        trainer_name="Test Teacher",
        module_name="Test Module",
        morning_break_status="Present",
        morning_break_hours=1.5,
        lunch_break_status="Absent",
        lunch_break_hours=0.0,
        tea_break_status="Present",
        tea_break_hours=0.5,
        final_session_status="Present",
        final_session_hours=2.0,
        total_class_hours=4.0
    )
    session.add(student_class_instance)
    session.commit()

    # Retrieve and verify the student class
    retrieved_student_class = session.query(StudentClass).filter_by(student_id="TestStudentID").first()
    assert retrieved_student_class is not None
    assert retrieved_student_class.notes == "Test notes"
    assert retrieved_student_class.date == datetime.strptime("2023-10-14", "%Y-%m-%d").date()
    assert retrieved_student_class.class_name == "Test Class"
    assert retrieved_student_class.trainer_name == "Test Teacher"
    assert retrieved_student_class.module_name == "Test Module"
    assert retrieved_student_class.morning_break_status == "Present"
    assert retrieved_student_class.morning_break_hours == 1.5
    assert retrieved_student_class.lunch_break_status == "Absent"
    assert retrieved_student_class.lunch_break_hours == 0.0
    assert retrieved_student_class.tea_break_status == "Present"
    assert retrieved_student_class.tea_break_hours == 0.5
    assert retrieved_student_class.final_session_status == "Present"
    assert retrieved_student_class.final_session_hours == 2.0
    assert retrieved_student_class.total_class_hours == 4.0

