from django.db import models

# Create your models here.
class Class(models.Model):
    class_id = models.AutoField(primary_key=True, unique=True)
    class_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.class_name
    
    @classmethod
    def all_classes(cls):
        return cls.objects.all()
    

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return self.teacher_name
    
    @classmethod
    def all_teachers(cls):
        return cls.objects.all()
    

class ClassSchedule(models.Model):
    date = models.DateField(primary_key=True)
    module = models.CharField(max_length=100)
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_total = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.date} - {self.class_info.class_name}"
    
    @classmethod
    def classes_taken_by_teacher(cls, teacher_name):
        return cls.objects.filter(trainer__teacher_name=teacher_name)
    
    @classmethod
    def classes_on_date(cls, date):
        return cls.objects.filter(date=date)
    

class UploadFile(models.Model):
    file = models.FileField(upload_to='')