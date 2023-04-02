from django import forms
from django.db.models import Sum

from grades.models import *


class AddGradeForm(forms.Form):
    def __init__(self, user, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.fields['subject'] = forms.ModelChoiceField(
            queryset=user.student.subjects.all(),
            label="Предмет", help_text="Выберите дисциплину"
        )
        self.fields['grade'] = forms.IntegerField(label="Оценка", help_text="Введите оценку")
        self.fields['work_type'] = forms.ModelChoiceField(
            queryset=WorkType.objects.all(),
            label="Тип работы", help_text="Выберите тип работы"
        )
    def clean(self):
        cleaned_data = super().clean()
        grade = cleaned_data.get('grade')
        subject = cleaned_data.get('subject')
        if grade and subject:
            student = self.request.user.student
            total_grade = Grade.objects.filter(student=student, subject=subject).aggregate(Sum('grade'))['grade__sum'] or 0
            if grade + total_grade > 100:
                raise forms.ValidationError("Сумма оценок по предмету не может превышать 100")
        return cleaned_data

class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "surname","institution", "group", "subjects", "purpose"]
        widgets = {
            'subjects': forms.CheckboxSelectMultiple,
        }