from django.shortcuts import render
from problems.models import problem
# Create your views here.

#to show problems
def all_problems(request):
    questions = problem.objects.all()

    context = {
        "all_problems":questions,
    }
    return render(request,"all_problems.html",context)

#to show details of problem
def problem_detail(request,id):
    req_problem = problem.objects.get(id=id)
    context = {
        "req_problem" : req_problem,
    }
    return render(request,"problem_detail.html",context)
