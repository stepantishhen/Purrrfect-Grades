from django.shortcuts import render, redirect
from allauth.socialaccount.models import SocialAccount

from grades.forms import *
from grades.models import *


def index(request):
    return render(request, "grades/index.html")


def profile(request):
    try:
        data = SocialAccount.objects.get(user=request.user).extra_data
    except:
        data = request.user
    return render(request, "grades/profile.html", context={"data": data})

def edit_profile(request):
    if request.method == 'POST':
        form = EditStudentForm(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            return redirect('profile_edit')
    else:
        form = EditStudentForm(instance=request.user.student)
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
                )
                return redirect('grades_add')
    else:
        form = AddGradeForm(current_user, request=request)
    return render(request, 'grades/grades_add.html', {'form': form, 'grades': grades})


def statistic(request):
    current_user = request.user
    grades = Grade.objects.filter(student=current_user.pk)
    data = dict()
    for i in grades:
        if i.subject not in data.keys():
            data[i.subject] = i.grade
        else:
            data[i.subject] += i.grade
    return render(request, 'grades/statistic.html', {'data': data})


def grade_delete(request, pk):
    Grade.objects.get(pk=pk).delete()
    return redirect('grades_add')