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

    for subject in subjects:
        grades = Grade.objects.filter(student=student, subject=subject).order_by('created_at')
        total_grade = grades.aggregate(total_grade=Sum('grade'))['total_grade']
        if total_grade is None:
            total_grade = 0
        avg_grade = grades.aggregate(avg_grade=Avg('grade'))['avg_grade']
        if avg_grade is None:
            avg_grade = 0
        avg_grade = round(avg_grade, 1)
        purpose = Purpose.objects.filter(student=student, subject=subject).first()
        if purpose is None:
            remaining_points = 0
        else:
            remaining_points = purpose.value - total_grade

        subject_grades.append({
            'subject': subject,
            'total_grade': total_grade,
            'avg_grade': avg_grade,
            'remaining_points': remaining_points
        })

    context = {
        'student': student,
        'subject_grades': subject_grades,
        'subjects': student.subjects.all()
    }

    return render(request, 'grades/profile.html', context)

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