from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from .models import Exam, Question, Choice, ExamResult
from courses.models import Course
from random import sample

# Create your views here.

@login_required
def exam_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    exam = get_object_or_404(Exam, course=course)
    
    # بررسی درصد پیشرفت دوره
    progress = course.get_progress_for_user(request.user)
    if progress < 75:
        messages.error(request, "برای شرکت در آزمون باید حداقل 75% دوره را تکمیل کرده باشید.")
        return redirect('courses:course_detail', slug=course.slug)

    # Get a random selection of questions
    questions = list(exam.questions.all())
    if len(questions) > exam.question_count:
        questions = sample(questions, exam.question_count)
    
    context = {
        'course': course,
        'exam': exam,
        'questions': questions,
    }
    return render(request, 'exams/exam_detail.html', context)

@login_required
def submit_exam(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        exam = get_object_or_404(Exam, course=course)
        
        # Calculate score
        total_questions = exam.question_count
        correct_answers = 0
        
        for question_id, answer_id in request.POST.items():
            if question_id.startswith('question_'):
                question_id = question_id.replace('question_', '')
                question = get_object_or_404(Question, id=question_id)
                if question.correct_choice_id == int(answer_id):
                    correct_answers += 1
        
        score = (correct_answers / total_questions) * 100
        passed = score >= exam.passing_score
        
        # Create exam result
        result = ExamResult.objects.create(
            user=request.user,
            exam=exam,
            score=score,
            passed=passed
        )
        
        return redirect('exams:exam_result', result_id=result.id)
    
    return redirect('exams:exam_detail', course_id=course_id)

@login_required
def exam_result(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id)
    context = {
        'result': result,
        'course': result.exam.course,
    }
    return render(request, 'exams/exam_result.html', context)

@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    exam = get_object_or_404(Exam, course=course)
    
    # Get the latest passing result
    result = ExamResult.objects.filter(
        user=request.user,
        exam=exam,
        passed=True
    ).order_by('-completed_at').first()
    
    if not result:
        messages.error(request, "شما هنوز در آزمون این دوره قبول نشده‌اید.")
        return redirect('courses:course_detail', slug=course.slug)
    
    context = {
        'course': course,
        'result': result,
    }
    return render(request, 'exams/certificate.html', context)
