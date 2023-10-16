# attendance_tracker

python3 should be installed on system

remember one thing open code in new browser window only

``` 
python3 -m venv venv

source venv/bin/activate (mac)
venv\Scripts\activate (windows)

pip install -r requirements.txt

cd flask_webapp

python flask_app.py

python dump_pass.py

streamlit run streamlit_ui.py

```

Admin creds
Admin
admin_password


```
streamlit run teachers_streamlit_ui.py
```
Teacher creds
teacher
teacher_password


I have added white_box_testing_database.py file for testing.
Command to run it 
```
pytest white_box_testing.py
```
Info:
Here's the documentation for the test functions in your test_app.py file:

### test_class_model(session)

This test function checks the Class model.
It creates a new Class instance, adds it to the database, and retrieves it.
Verifies that the retrieved Class has the correct name.
### test_teacher_model(session)

This test function checks the Teacher model.
It creates a new Teacher instance, adds it to the database, and retrieves it.
Verifies that the retrieved Teacher has the correct name.
### test_student_model(session)

This test function checks the Student model.
It creates a new Student instance, adds it to the database, and retrieves it.
Verifies that the retrieved Student has the correct student ID, first name, and last name.
### test_module_model(session)

This test function checks the Module model.
It creates a new Module instance, adds it to the database, and retrieves it.
Verifies that the retrieved Module has the correct module name.
### test_class_schedule_model(session)

This test function checks the ClassSchedule model.
It creates a new ClassSchedule instance, adds it to the database, and retrieves it.
Verifies that the retrieved ClassSchedule has the correct date, module, class name, trainer name, and class total.
### test_student_class_model(session)

This test function checks the StudentClass model.
It creates a new StudentClass instance, adds it to the database, and retrieves it.
Verifies that the retrieved StudentClass has the correct student ID, notes, date, class name, trainer name, module name, and other attributes.

Each test function follows a similar pattern: creating an instance, adding it to the database, retrieving it, and then making assertions to ensure that the retrieved data matches the expected values. These tests help ensure that your SQLAlchemy models and database operations are working correctly.


## Second white box testing file (this file to test backend)
```
pytest white_box_testing_backend.py
```

test_add_class
This test validates the add_class function. It verifies that the function correctly adds a new class to the database and returns a success message if the class is added successfully.

test_add_teacher
This test validates the add_teacher function. It ensures that the function correctly adds a new teacher to the database and returns a success message if the teacher is added successfully.

test_add_module
This test validates the add_module function. It verifies that the function correctly adds a new module to the database and returns a success message if the module is added successfully.

test_add_class_schedule
This test validates the add_class_schedule function. It checks if the function correctly adds a new class schedule entry to the database and returns "Success."

test_calculate_break_hours
This test validates the calculate_break_hours function. It checks the calculation of break hours based on the provided status (e.g., "Present," "Absent," or "Late_15_mins").

test_query_database
This test validates the query_database function. It tests whether the function can retrieve data from the database based on the provided student name, class name, teacher name, and module name.



