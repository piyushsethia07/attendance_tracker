import streamlit as st
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import streamlit.components.v1 as html
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
from flask_app import Class, Teacher, ClassSchedule, Student, StudentClass
from datetime import datetime
import pandas as pd
import os
import yaml
from yaml.loader import SafeLoader
from auth_help import login_user
from test import add_class_schedule, add_data_after_reading_csv_file, add_student, add_class_history, calculate_break_hours

UPLOAD_FOLDER = "uploads"

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Function to query data based on student name, class name, and trainer
def query_database(student_name, class_name, trainer_name, module_name):
    try:
        # Query the database based on the provided criteria
        student_class = session.query(StudentClass).filter_by(
            student_id=student_name,
            class_name=class_name,
            trainer_name=trainer_name,
            module_name=module_name
        ).first()
        
        return student_class
    except Exception as e:
        st.error(f"Error querying the database: {str(e)}")
        return None

# Function to update data in the database
def update_data_in_database(
    student_class,
    new_notes,
    new_morning_break_status,
    new_lunch_break_status,
    new_tea_break_status,
    new_final_session_status,
):
    try:
        if student_class:
            

            # Update the fields in the student_class object
            student_class.notes = new_notes
            student_class.morning_break_status = new_morning_break_status
            student_class.morning_break_hours = calculate_break_hours(new_morning_break_status)
            student_class.lunch_break_status = new_lunch_break_status
            student_class.lunch_break_hours = calculate_break_hours(new_lunch_break_status)
            student_class.tea_break_status = new_tea_break_status
            student_class.tea_break_hours = calculate_break_hours(new_tea_break_status)
            student_class.final_session_status = new_final_session_status
            student_class.final_session_hours = calculate_break_hours(new_final_session_status)
            student_class.total_class_hours = student_class.morning_break_hours + student_class.lunch_break_hours + student_class.tea_break_hours + student_class.final_session_hours

            # Commit the changes to the database
            session.commit()

            st.success("Data updated successfully.")
        else:
            st.warning("Data not found for the provided input.")
    except Exception as e:
        st.error(f"Error updating data in the database: {str(e)}")


# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
Session = sessionmaker(bind=engine)
session = Session()

def login():
  username = st.text_input('Username')
  password = st.text_input('Password', type='password')

  # Validate the user's credentials
  if username == 'alice' and password == 'password123':
    st.session_state['authentication_status'] = True
  else:
    st.error('Invalid username or password.')

if not st.session_state.get('authentication_status'):
  login()
else:

    # Streamlit UI
    st.sidebar.title("Admin Database Management")

    st.session_state['admin'] = True

    # Sidebar
    with st.sidebar:
        selected_option = option_menu("Main Menu", ["Add Teacher", "Add Class", "Upload Excel", "Add Students", "Class History", "Edit Class Details", "Teacher Dashboard"] , 
            icons=[], menu_icon="cast", default_index=1)
        

    if selected_option == 'Login':
        st.image("logo.jpeg", use_column_width=True)
        with st.form(key='Auth-form'):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username.lower() == 'admin' and password.lower() == 'admin_password':
                st.session_state['admin'] = True
                selected_option = "Upload Excel"
            else:
                if login_user(username, password) is not None:
                    selected_option = "Upload Excel"
                else:
                    st.warning('Wrong username or password')

    if selected_option == "Add Teacher":

        if st.session_state['admin'] == False:
            st.warning(''' Teachers can't access this page ''')
        
        else:
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
                teacher_data = []
                for teacher in teachers:
                    class_count = session.query(ClassSchedule).filter_by(trainer_name=teacher.teacher_name).count()
                    teacher_data.append({"Teacher Name": teacher.teacher_name, "Class Count": class_count})

                # Create a bar chart
                st.header("Classes per Teacher")
                data = pd.DataFrame(teacher_data)
                fig, ax = plt.subplots()
                ax.bar(data["Teacher Name"], data["Class Count"])
                plt.xticks(rotation=45)
                plt.xlabel("Teacher Name")
                plt.ylabel("Class Count")
                st.pyplot(fig)

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
            class_data = []
            for cls in class_schedule_data:
                student_count = session.query(StudentClass).filter_by(class_name=cls.class_name, trainer_name=cls.trainer_name).count()
                class_data.append({"Class Name": cls.class_name, "Student Count": student_count})

            # Create a bar chart
            st.header("Students per Class")
            data = pd.DataFrame(class_data)
            fig, ax = plt.subplots()
            ax.bar(data["Class Name"], data["Student Count"])
            plt.xticks(rotation=45)
            plt.xlabel("Class Name")
            plt.ylabel("Student Count")
            st.pyplot(fig)
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
        df = df.dropna(subset=['First Name'])
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
            'Module Name': [student_class.module_name for student_class in class_history_db],
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
            filter_option = st.selectbox("Filter by", [None, "Date", "Trainer", "Class", "Student Name", "Module Name"])

            if filter_option == "Date":
                selected_value = st.date_input("Select Date", min_value=df["Date"].min(), max_value=df["Date"].max())
                df = df[df["Date"] == selected_value]
            elif filter_option == "Trainer":
                selected_value = st.text_input("Enter Trainer Name")
                df = df[df["Trainer Name"].str.contains(selected_value, case=False, na=False)]
            elif filter_option == "Module Name":
                selected_value = st.text_input("Enter Module Name")
                df = df[df["Module Name"].str.contains(selected_value, case=False, na=False)]
            elif filter_option == "Class":
                selected_value = st.text_input("Enter Class Name")
                df = df[df["Class Name"].str.contains(selected_value, case=False, na=False)]
            elif filter_option == "Student Name":
                selected_value = st.text_input("Enter Student Name")
                df = df[df["Student ID"].str.contains(selected_value, case=False, na=False)]
        # Display the filtered DataFrame in Streamlit
        st.write(df)

    if selected_option == "Edit Class Details":
        st.title("Edit Data")

        # Create input fields for student name, class name, and trainer name
        student_name = st.text_input("Student ID")
        class_name = st.text_input("Class Name")
        trainer_name = st.text_input("Trainer Name")
        module_name = st.text_input("Module Name")

        if student_name and class_name and trainer_name:
            # Query the database based on user input
            student_class = query_database(student_name, class_name, trainer_name, module_name)

            data = {
                'Student ID': [student_class.student_id],
                'Notes': [student_class.notes],
                'Date': [student_class.date],
                'Class Name': [student_class.class_name],
                'Trainer Name': [student_class.trainer_name],
                'Module Name': [student_class.module_name],
                'Morning Break Status': [student_class.morning_break_status],
                'Morning Break Hours': [student_class.morning_break_hours],
                'Lunch Break Status': [student_class.lunch_break_status],
                'Lunch Break Hours': [student_class.lunch_break_hours],
                'Tea Break Status': [student_class.tea_break_status],
                'Tea Break Hours': [student_class.tea_break_hours],
                'Final Session Status': [student_class.final_session_status],
                'Final Session Hours': [student_class.final_session_hours],
                'Total Class Hours': [student_class.total_class_hours]
            }


            # Convert the list of dictionaries to a Pandas DataFrame
            df = pd.DataFrame(data)
            df = df.dropna(subset=['Total Class Hours'])
            st.write(df)

            if student_class:
                # Display the editable fields

                break_status_options = ["Present", "Absent", "Late_15_mins", "Late_30_mins", "Late_45_mins", "Late_60_mins"]


                st.header("Edit Fields")
                
                # Create input fields for various fields
                new_notes = st.text_input("Notes", student_class.notes)
                new_morning_break_status = st.selectbox(f"Morning Break Status", break_status_options)
                new_lunch_break_status = st.selectbox("Lunch Break Status", break_status_options)
                new_tea_break_status = st.selectbox("Tea Break Status", break_status_options)
                new_final_session_status = st.selectbox("Final Session Status", break_status_options)

                # Add a button to update data
                if st.button("Update Data"):
                    # Update the database with the new data
                    update_data_in_database(
                        student_class,
                        new_notes,
                        new_morning_break_status,
                        new_lunch_break_status,
                        new_tea_break_status,
                        new_final_session_status
                    )
                    student_class = query_database(student_name, class_name, trainer_name, module_name)

                    data = {
                        'Student ID': [student_class.student_id],
                        'Notes': [student_class.notes],
                        'Date': [student_class.date],
                        'Class Name': [student_class.class_name],
                        'Trainer Name': [student_class.trainer_name],
                        'Module Name': [student_class.module_name],
                        'Morning Break Status': [student_class.morning_break_status],
                        'Morning Break Hours': [student_class.morning_break_hours],
                        'Lunch Break Status': [student_class.lunch_break_status],
                        'Lunch Break Hours': [student_class.lunch_break_hours],
                        'Tea Break Status': [student_class.tea_break_status],
                        'Tea Break Hours': [student_class.tea_break_hours],
                        'Final Session Status': [student_class.final_session_status],
                        'Final Session Hours': [student_class.final_session_hours],
                        'Total Class Hours': [student_class.total_class_hours]
                    }


                    # Convert the list of dictionaries to a Pandas DataFrame
                    df = pd.DataFrame(data)
                    st.write(df)
            else:
                st.warning("Data not found for the provided input.")

    if selected_option == 'Teacher Dashboard':
        with st.form('filter_form'):
            teacher_name = st.text_input('Enter techer name','Adrian White')
            student_id = st.text_input('Enter student id','All Students')
            submitted_techer_dashboard = st.form_submit_button('Analyse')
        if submitted_techer_dashboard:
            total_classes = session.query(ClassSchedule).filter_by(trainer_name=teacher_name).count()
            today = datetime.today().date()
            upcoming_classes = session.query(ClassSchedule).filter_by(trainer_name=teacher_name).filter(ClassSchedule.date >= today).all()
            class_data = []
            for cls in upcoming_classes:
                student_count = session.query(StudentClass).filter_by(class_name=cls.class_name, trainer_name=cls.trainer_name).count()
                class_data.append({"Date": cls.date, "Module": cls.module, "Student Count": student_count})

            # Create a bar chart
            st.title("Teacher Dashboard")
            st.header("Upcoming Classes")
            data = pd.DataFrame(class_data)
            if data.shape[0] > 1:
                fig, ax = plt.subplots()
                ax.bar(data["Date"].astype(str), data["Student Count"])
                plt.xticks(rotation=45)
                plt.xlabel("Date")
                plt.ylabel("Student Count")
                st.pyplot(fig)
            else:
                st.write('No Upcoming classes')
            if student_id == 'All Students':
                all_students = session.query(Student).all()
                attendance_percentage_data = {"Student": [], "Present": [], "Absent": [], "Late_15_mins": [], "Late_30_mins": [], "Late_45_mins": [], "Late_60_mins": []}

                for student in all_students:
                    student_id = student.student_id
                    student_name = f"{student.first_name} {student.last_name}"
                    student_data = {
                        "Student": student_name,
                        "Present": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Present").count(),
                        "Absent": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Absent").count(),
                        "Late_15_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_15_mins").count(),
                        "Late_30_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_30_mins").count(),
                        "Late_45_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_45_mins").count(),
                        "Late_60_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_60_mins").count(),
                    }
                    attendance_percentage_data["Student"].append(student_name)
                    for key in student_data.keys():
                        if key == 'Student':
                            continue
                        attendance_percentage_data[key].append((student_data[key] / total_classes) * 100)

                # Create a bar chart for attendance percentages for all students
                st.subheader("Attendance Percentage for All Students")
                df_attendance_percentage = pd.DataFrame(attendance_percentage_data)
                df_attendance_percentage.set_index("Student", inplace=True)
                st.bar_chart(df_attendance_percentage)

            # Calculate the percentage of classes attended by the student
            attended_classes = session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name).count()
            if attended_classes>0 and student_id != 'All Students':

                # Calculate attendance status distribution
                attendance_data = {
                    "Present": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Present").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Present").count(),
                    "Absent": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Absent").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Absent").count(),
                    "Late_15_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_15_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_15_mins").count(),
                    "Late_30_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_30_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_30_mins").count(),
                    "Late_45_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_45_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_45_mins").count(),
                    "Late_60_mins": session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, morning_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, tea_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, lunch_break_status="Late_60_mins").count() + session.query(StudentClass).filter_by(student_id=student_id, trainer_name=teacher_name, final_session_status="Late_60_mins").count(),
                }

                # Create a pie chart for attendance status distribution
                st.subheader("Attendance Status Distribution")
                fig2, ax2 = plt.subplots()
                ax2.pie(attendance_data.values(), labels=attendance_data.keys(), autopct='%1.1f%%', startangle=90)
                ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig2)
