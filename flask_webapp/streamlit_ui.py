import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_app import Class, Teacher, ClassSchedule
from datetime import datetime
import pandas as pd
import os
from test import add_class_schedule, add_data_after_reading_csv_file

UPLOAD_FOLDER = "uploads"

# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit UI
st.sidebar.title("Database Management")

# Sidebar
selected_option = st.sidebar.selectbox("Select Option", ["Add Teacher", "Add Class", "Upload Excel"])

if selected_option == "Add Teacher":

    st.header("Add Teacher")

    teacher_name = st.text_input("Teacher Name")
    teacher_password = st.text_input("Teacher Password")
    
    if st.button("Add Teacher"):
        if teacher_name:
            teacher_record = session.query(Teacher).filter_by(teacher_name=teacher_name).first()
            if not teacher_record:
                new_teacher = Teacher(teacher_name=teacher_name, password=teacher_password)
                session.add(new_teacher)
                session.commit()
                st.success(f"Teacher '{teacher_name}' added successfully")
            else:
                st.warning(f"Teacher '{teacher_name}' already exists")
    teachers = session.query(Teacher).all()
    teacher_names = [teacher.teacher_name for teacher in teachers]
    teacher_passwords = [teacher.password for teacher in teachers]
    teacher_df = pd.DataFrame({'Teacher Name': teacher_names, 'Password': teacher_passwords})
    if teacher_df.shape[0] > 0:
        st.header("Teachers in the system:")
        st.dataframe(teacher_df)

elif selected_option == "Add Class":
    st.header("Classes in the System")

    class_name = st.text_input("Class Name")
    
    if st.button("Add Class"):
        if class_name:
            class_record = session.query(Class).filter_by(class_name=class_name).first()
            if not class_record:
                new_class = Class(class_name=class_name)
                session.add(new_class)
                session.commit()
                st.success(f"Class '{class_name}' added successfully")
            else:
                st.warning(f"Class '{class_name}' already exists")
    classes = session.query(Class).all()
    class_names = [class_.class_name for class_ in classes]
    class_df = pd.DataFrame({'Class Name': class_names})
    if class_df.shape[0] > 0:
        st.header("Courses in System")
        st.dataframe(class_df)

elif selected_option == "Upload Excel":
    st.header("Upload Excel File")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if uploaded_file:
        file_name = os.path.join(UPLOAD_FOLDER, uploaded_file.name) 
        with open(file_name,"wb") as f:
            f.write(uploaded_file.getbuffer())
        metadata = add_data_after_reading_csv_file(file_name)
        st.write(file_name)
        result = add_class_schedule(metadata)
        st.write(f"{result}")

    class_schedule_data = session.query(ClassSchedule).all()
    if class_schedule_data:
        class_schedule_df = pd.DataFrame({
            'Date': [entry.date for entry in class_schedule_data],
            'Module': [entry.module for entry in class_schedule_data],
            'Class Name': [entry.class_name for entry in class_schedule_data],
            'Trainer Name': [entry.trainer_name for entry in class_schedule_data],
            'Class Total': [entry.class_total for entry in class_schedule_data]
        })
        st.header("Class Schedule Data:")
        st.dataframe(class_schedule_df)
    else:
        st.warning("No data found in ClassSchedule table.")
