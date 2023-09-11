from datetime import datetime
from myapp.models import Class, Teacher, ClassSchedule
import pandas as pd
from openpyxl import load_workbook

def add_class_schedule(date_str, module, class_name, trainer_name, class_total):
    # Convert the date string to a Python datetime object
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')

    # Get or create Class and Teacher instances
    class_instance = Class.objects.filter(class_name=class_name).first()
    if not class_instance:
        # If it doesn't exist, create a new Class instance
        class_instance = Class(class_name=class_name)
        class_instance.save()
    
    # Check if a Teacher instance with the given teacher name exists
    teacher_instance = Teacher.objects.filter(teacher_name=trainer_name).first()
    if not teacher_instance:
        # If it doesn't exist, create a new Teacher instance
        teacher_instance = Teacher(teacher_name=trainer_name)
        teacher_instance.save()

    existing_schedule = ClassSchedule.objects.filter(date=date_obj, class_info=class_instance).first()
    if existing_schedule:
        print("Class schedule already exists for this date and class.")
        return  # Return without creating a new record

    # Create a ClassSchedule instance
    class_schedule = ClassSchedule(
        date=date_obj,
        module=module,
        class_info=class_instance,
        trainer=teacher_instance,
        class_total=class_total
    )

    # Save the ClassSchedule instance to the database
    class_schedule.save()


def add_data_after_reading_csv_file(wb, excel_file_path):

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
                        print('Invalid data format')
            print(metadata)
            add_class_schedule(metadata['date'],metadata['module'],metadata['class'],metadata['trainer'],metadata['class total'])