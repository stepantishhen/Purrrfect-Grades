from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.db.models import Avg, Sum, F


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Предмет")
    teacher = models.CharField(max_length=100, verbose_name="Преподаватель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

class WorkType(models.Model):
    name = models.CharField(max_length=50)
    weight = models.FloatField()

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Имя")
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    institution = models.CharField(max_length=100, verbose_name="Институт")
    group = models.CharField(max_length=100, verbose_name="Номер группы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    subjects = models.ManyToManyField(Subject, verbose_name="Дисциплины", blank=True)

    def __str__(self):
        return f'{self.user}'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Student.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.student.save()

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE, related_name='grades')
    grade = models.IntegerField()
    receipt_at = models.DateField(auto_now_add=False, verbose_name="Дата получения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f'{self.subject} - {self.grade}'

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

class Purpose(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return f'{self.subject} - {self.value}'

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"