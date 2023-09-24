import streamlit as st
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from sqlalchemy.orm import sessionmaker
from flask_app import Class, Teacher, ClassSchedule, Student, StudentClass
from datetime import datetime
import pandas as pd
import os
from test import add_class_schedule, add_data_after_reading_csv_file, add_student, add_class_history

UPLOAD_FOLDER = "uploads"

# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit UI
st.sidebar.title("Database Management")

# Sidebar
with st.sidebar:
    selected_option = option_menu("Main Menu", ["Add Teacher", "Add Class", "Upload Excel", "Add Students", "Class History"], 
        icons=[], menu_icon="cast", default_index=1)

if selected_option == "Add Teacher":

    with st.expander("Add Teacher"):

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

    with st.expander("Classes in the System"):

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

    with st.expander("Upload Excel File"):
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        
        if uploaded_file:
            file_name = os.path.join(UPLOAD_FOLDER, uploaded_file.name) 
            with open(file_name,"wb") as f:
                f.write(uploaded_file.getbuffer())
            metadata, temp_df = add_data_after_reading_csv_file(file_name)
            st.write(file_name)
            result = add_class_schedule(metadata)
            st.write(f"{result}")
            temp_df = temp_df.dropna(subset=['Student ID'])
            student_entry = add_student(temp_df)
            st.write(student_entry)

            class_history = add_class_history(metadata, temp_df)
            st.write(class_history)


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

if selected_option == "Add Students":

    students = session.query(Student).all()
    # Convert the queried data to a Pandas DataFrame
    data = {
        'Student ID': [student.student_id for student in students],
        'AC/IT': [student.course_enrolled for student in students],
        'Password': [student.password for student in students],
        'Att': [student.attendance for student in students],
        'Last Name': [student.last_name for student in students],
        'First Name': [student.first_name for student in students],
        'Preferred name': [student.preferred_name for student in students]
    }

    df = pd.DataFrame(data)

    # Display the DataFrame in Streamlit
    st.write(df)

if selected_option == "Class History":

    class_history_db = session.query(StudentClass).all()
    
    # Convert the queried data to a list of dictionaries
    data = {
        'Student ID': [student_class.student_id for student_class in class_history_db],
        'Notes': [student_class.notes for student_class in class_history_db],
        'Date': [student_class.date for student_class in class_history_db],
        'Class Name': [student_class.class_name for student_class in class_history_db],
        'Trainer Name': [student_class.trainer_name for student_class in class_history_db],
        'Morning Break Status': [student_class.morning_break_status for student_class in class_history_db],
        'Morning Break Hours': [student_class.morning_break_hours for student_class in class_history_db],
        'Lunch Break Status': [student_class.lunch_break_status for student_class in class_history_db],
        'Lunch Break Hours': [student_class.lunch_break_hours for student_class in class_history_db],
        'Tea Break Status': [student_class.tea_break_status for student_class in class_history_db],
        'Tea Break Hours': [student_class.tea_break_hours for student_class in class_history_db],
        'Final Session Status': [student_class.final_session_status for student_class in class_history_db],
        'Final Session Hours': [student_class.final_session_hours for student_class in class_history_db],
        'Total Class Hours': [student_class.total_class_hours for student_class in class_history_db]
    }


    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(data)

    with st.expander("Filter Options"):
        filter_option = st.selectbox("Filter by", [None, "Date", "Trainer", "Class", "Student Name"])

        if filter_option == "Date":
            selected_value = st.date_input("Select Date", min_value=df["Date"].min(), max_value=df["Date"].max())
            df = df[df["Date"] == selected_value]
        elif filter_option == "Trainer":
            selected_value = st.text_input("Enter Trainer Name")
            df = df[df["Trainer Name"].str.contains(selected_value, case=False, na=False)]
        elif filter_option == "Class":
            selected_value = st.text_input("Enter Class Name")
            df = df[df["Class Name"].str.contains(selected_value, case=False, na=False)]
        elif filter_option == "Student Name":
            selected_value = st.text_input("Enter Student Name")
            df = df[df["Student ID"].str.contains(selected_value, case=False, na=False)]

    # Display the filtered DataFrame in Streamlit
    st.write(df)


