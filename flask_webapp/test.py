from sqlalchemy import create_engine
from flask_app import Class, ClassSchedule, Teacher
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook


def add_data_after_reading_csv_file(excel_file_path):
    wb = load_workbook(excel_file_path, data_only=True)  # Use data_only=True to read evaluated values

    # Create an empty list to store the data
    data = []
    
    # Iterate through all sheets in the workbook
    for sheet in wb.sheetnames:
        # Read each sheet as a DataFrame
        df = pd.read_excel(excel_file_path, sheet_name=sheet, header=None)
        df = df.dropna(how='all')
        data.append(df)

    for df in data:
        if 'date' in df.iloc[0][0].lower():
            metadata = {}
            for index in range(len(df.iloc[0])):
                if pd.notna(df.iloc[0][index]):
                    try:
                        key = df.iloc[0][index].split(':')[0].strip().lower()
                        if key.lower() == 'class total':
                            value = df.iloc[0][index+1]
                        else:
                            value = df.iloc[0][index].split(':')[1].strip()
                        metadata[key] = value
                    except:
                        pass
                        # print('Invalid data format')
            return(metadata)

# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///myapp.db')  # Replace with your SQLite database URI
Session = sessionmaker(bind=engine)
session = Session()


def add_class(data):
    class_record = session.query(Class).filter_by(class_name=data['class']).first()
    if not class_record:
        new_class = Class(class_name=data['class'])
        session.add(new_class)
        session.commit()
        return f"{data['class']} added successfully"
    else:
        return f"Class with {data['class']}  already exists"

# Function to add data to the Teacher table

def add_teacher(data):
    new_teacher = session.query(Teacher).filter_by(teacher_name=data['trainer']).first()
    if not new_teacher:
        new_teacher = Teacher(teacher_name=data['trainer'])
        session.add(new_teacher)
        session.commit()
        return f"{data['trainer']} added successfully"
    else:
        return f"Teacher with {data['trainer']}  already exists"

# Function to add data to the ClassSchedule table
def add_class_schedule(data):
    class_name = data['class']
    trainer_name = data['trainer']
    parsed_date = datetime.strptime(data['date'], '%m/%d/%Y').date()
    # Query the Class and Teacher tables to get their corresponding IDs
    class_record = session.query(Class).filter_by(class_name=class_name).first()
    teacher_record = session.query(Teacher).filter_by(teacher_name=trainer_name).first()

    if class_record and teacher_record:
        new_class_schedule = ClassSchedule(
            date=parsed_date,
            module=data['module'],
            class_name=class_record.class_name,
            trainer_name=teacher_record.teacher_name,
            class_total=data['class total']
        )
        session.add(new_class_schedule)
        session.commit()
        return "Success"
    else:
        add_class(data)
        add_teacher(data)
        class_record = session.query(Class).filter_by(class_name=class_name).first()
        teacher_record = session.query(Teacher).filter_by(teacher_name=trainer_name).first()
        new_class_schedule = ClassSchedule(
            date=parsed_date,
            module=data['module'],
            class_name=class_record.class_name,
            trainer_name=teacher_record.teacher_name,
            class_total=data['class total']
        )
        session.add(new_class_schedule)
        session.commit()
        return ("Class or Teacher not found in the database. Added to database and then class schedule updated")
