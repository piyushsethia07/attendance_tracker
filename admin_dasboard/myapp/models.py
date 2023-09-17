from django.db import models

# Create your models here.
class Class(models.Model):
    class_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.class_name
    
    @classmethod
    def all_classes(cls):
        return cls.objects.all()
    

class Teacher(models.Model):
    teacher_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100, default='teacher_login')

    def __str__(self):
        return self.teacher_name
    
    @classmethod
    def all_teachers(cls):
        return cls.objects.all()
    

class ClassSchedule(models.Model):
    date = models.DateField()
    module = models.CharField(max_length=100)
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE, null=False)
    trainer = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False)
    class_total = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.date} - {self.class_info.class_name}"
    
    @classmethod
    def classes_taken_by_teacher(cls, teacher_name):
        return cls.objects.filter(trainer__teacher_name=teacher_name)
    
    @classmethod
    def classes_on_date(cls, date):
        return cls.objects.filter(date=date)
    
    class Meta:
        # Define a unique constraint for class_info and trainer
        unique_together = ('class_info', 'trainer')

class Student(models.Model):
    student_id = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100, default='student_login')
    course_enrolled = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class StudentClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE, null=False)
    trainer = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False)
    start_time = models.TimeField()
    # 1
    morning_break_status = models.CharField(max_length=20)  # e.g., "Present", "Late 30mins", etc.
    morning_break_hours = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 2.00
    # 2
    lunch_break_status = models.CharField(max_length=20)
    lunch_break_hours = models.DecimalField(max_digits=4, decimal_places=2)
    # 3
    tea_break_status = models.CharField(max_length=20)
    tea_break_hours = models.DecimalField(max_digits=4, decimal_places=2)
    # 4
    final_session_status = models.CharField(max_length=20)
    final_session_hours = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 2.00
    total_class_hours = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 8.00

    def __str__(self):
        return f"{self.student} - {self.class_schedule.class_info.class_name}"
    
    class Meta:
        # Define a unique constraint for class_info and trainer
        unique_together = ('student', 'class_info', 'trainer')


class UploadFile(models.Model):
    file = models.FileField(upload_to='')