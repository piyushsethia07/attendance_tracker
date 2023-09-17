import streamlit as st
import os
from django.core.wsgi import get_wsgi_application
from django.db import IntegrityError
from django.db.models import Q
from myapp.models import Teacher, Class, ClassSchedule
import django

import sys
from pathlib import Path


PROJECT_ROOT_DIR = Path(os.path.abspath(__file__)).parents[1]
DJANGO_ROOT_DIR = PROJECT_ROOT_DIR / "admin_dashboard"

def django_setup() -> None:
    """
    Allows to setup Django if it's not already running on a server. Should be called before any Django imports.
    """
    # Add the project base directory to the sys.path
    sys.path.append(DJANGO_ROOT_DIR.as_posix())

    # The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "admin_dashboard.admin_dashboard.settings"
    )

    # This is for setting up django
    django.setup()

django.setup()

# Create Streamlit app title
st.title("Django and Streamlit Integration")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Home", "Add Teacher", "Add Class", "Add Class Schedule"])

# Define functions to handle database operations

def add_teacher(teacher_name, password):
    try:
        teacher = Teacher(teacher_name=teacher_name, password=password)
        teacher.save()
        st.success("Teacher added successfully!")
    except IntegrityError:
        st.error("Teacher already exists!")

def add_class(class_name):
    try:
        class_obj = Class(class_name=class_name)
        class_obj.save()
        st.success("Class added successfully!")
    except IntegrityError:
        st.error("Class already exists!")

def add_class_schedule(date, module, class_name, trainer_name, class_total):
    try:
        class_obj = Class.objects.get(class_name=class_name)
        teacher = Teacher.objects.get(teacher_name=trainer_name)
        schedule = ClassSchedule(date=date, module=module, class_info=class_obj, trainer=teacher, class_total=class_total)
        schedule.save()
        st.success("Class schedule added successfully!")
    except (Class.DoesNotExist, Teacher.DoesNotExist):
        st.error("Class or teacher not found!")

def display_teachers():
    teachers = Teacher.objects.all()
    if teachers:
        st.write("Teachers:")
        for teacher in teachers:
            st.write(f"Name: {teacher.teacher_name}, Password: {teacher.password}")
    else:
        st.warning("No teachers found!")

def display_classes():
    classes = Class.objects.all()
    if classes:
        st.write("Classes:")
        for class_obj in classes:
            st.write(f"Name: {class_obj.class_name}")
    else:
        st.warning("No classes found!")

def display_class_schedules():
    class_schedules = ClassSchedule.objects.all()
    if class_schedules:
        st.write("Class Schedules:")
        for schedule in class_schedules:
            st.write(f"Date: {schedule.date}, Module: {schedule.module}, Class: {schedule.class_info.class_name}, Trainer: {schedule.trainer.teacher_name}, Total Students: {schedule.class_total}")
    else:
        st.warning("No class schedules found!")

# Streamlit UI based on menu selection

if menu == "Home":
    st.write("Welcome to the Django and Streamlit Integration App!")
    st.write("Use the sidebar to navigate and interact with the database.")

elif menu == "Add Teacher":
    st.header("Add Teacher")
    teacher_name = st.text_input("Teacher Name")
    password = st.text_input("Password")
    if st.button("Add"):
        add_teacher(teacher_name, password)

elif menu == "Add Class":
    st.header("Add Class")
    class_name = st.text_input("Class Name")
    if st.button("Add"):
        add_class(class_name)

elif menu == "Add Class Schedule":
    st.header("Add Class Schedule")
    date = st.date_input("Date")
    module = st.text_input("Module")
    class_name = st.selectbox("Class", Class.objects.all().values_list("class_name", flat=True))
    trainer_name = st.selectbox("Trainer", Teacher.objects.all().values_list("teacher_name", flat=True))
    class_total = st.number_input("Total Students", min_value=0, step=1)
    if st.button("Add"):
        add_class_schedule(date, module, class_name, trainer_name, class_total)

elif menu == "Display Teachers":
    st.header("Display Teachers")
    display_teachers()

elif menu == "Display Classes":
    st.header("Display Classes")
    display_classes()

elif menu == "Display Class Schedules":
    st.header("Display Class Schedules")
    display_class_schedules()
