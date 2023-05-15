import random

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from allauth.socialaccount.models import SocialAccount

from grades.forms import *
from grades.models import *


def index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Проблема с сайтом"
            body = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())
            try:
                send_mail(subject, message,
                          'admin@example.com',
                          ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Найден некорректный заголовок')
            return redirect("index")
    else:
        form = ContactForm()
    return render(request, "grades/index.html", context={'form': form})


def profile(request):
    # try:
    #     data = SocialAccount.objects.get(user=request.user).extra_data
    # except:
    #     data = request.user
    student = request.user.student
    subjects = student.subjects.all()

    subject_grades = []
    monthly_grades = {}  # словарь для хранения суммы оценок по месяцам

    for subject in subjects:
        grades = Grade.objects.filter(student=student, subject=subject).order_by('created_at')
        total_grade = grades.aggregate(total_grade=Sum('grade'))['total_grade']
        avg_grade = grades.aggregate(avg_grade=Avg('grade'))['avg_grade']
        remaining_points = Purpose.objects.filter(student=student, subject=subject).first().value - total_grade if Purpose.objects.filter(student=student, subject=subject).first() is not None else 0


        # вычисляем сумму оценок по месяцам
        for grade in grades:
            month = grade.receipt_at.strftime('%B %Y')
            if month not in monthly_grades.keys():
                monthly_grades[month] = dict()
                if subject not in monthly_grades[month].keys():
                    monthly_grades[month][subject.name] = 0
                    rand_color = f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.2)'
                    monthly_grades[month]["backgroundColor"] = rand_color
                    monthly_grades[month]["borderColor"] = rand_color
                    monthly_grades[month]["borderWidth"] = 1
                    monthly_grades[month][subject.name] += grade.grade
                else:
                    monthly_grades[month][subject.name] += grade.grade
            else:
                if subject not in monthly_grades[month].keys():
                    monthly_grades[month][subject.name] = 0
                    rand_color = f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.2)'
                    monthly_grades[month]["backgroundColor"] = rand_color
                    monthly_grades[month]["borderColor"] = rand_color
                    monthly_grades[month]["borderWidth"] = 1
                    monthly_grades[month][subject.name] += grade.grade
                else:
                    monthly_grades[month][subject.name] += grade.grade

        subject_grades.append({
            'subject': subject,
            'total_grade': total_grade,
            'avg_grade': round(avg_grade, 1),
            'remaining_points': remaining_points
        })

    context = {
        'student': student,
        'subject_grades': subject_grades,
        'monthly_grades': monthly_grades  # добавляем словарь в контекст
    }

    return render(request, 'grades/profile.html', context)
def calculator(request):
    student = request.user.student
    context = {
        'subjects': student.subjects.all()
    }
    return render(request, 'grades/calculator.html', context=context)

def edit_profile(request):
    if request.method == 'POST':
        form = EditStudentForm(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            return redirect('profile_edit')
    else:
        form = EditStudentForm(instance=request.user.student, initial={'subjects': request.user.student.subjects.all()})
    return render(request, 'grades/edit_profile.html', {'form': form})



def grades_add(request):
    current_user = request.user
    grades = Grade.objects.filter(student=current_user.pk)
    if request.method == 'POST':
        form = AddGradeForm(current_user, request=request, data=request.POST)
        if form.is_valid():
            student = current_user.student
            subject = form.cleaned_data['subject']
            total_grade = Grade.objects.filter(student=student, subject=subject).aggregate(Sum('grade'))['grade__sum'] or 0
            grade = form.cleaned_data['grade']
            if grade + total_grade > 100:
                form.add_error('grade', "Сумма оценок по предмету не может превышать 100")
            else:
                grade = Grade.objects.create(
                    grade=grade,
                    student=student,
                    subject=subject,
                    work_type=form.cleaned_data['work_type'],
                    receipt_at=form.cleaned_data['receipt_at']
                )
                return redirect('grades_add')
    else:
        form = AddGradeForm(current_user, request=request)
    return render(request, 'grades/grades_add.html', {'form': form, 'grades': grades})


def grade_delete(request, pk):
    Grade.objects.get(pk=pk).delete()
    return redirect('grades_add')