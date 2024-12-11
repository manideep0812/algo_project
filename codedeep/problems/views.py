from django.shortcuts import render
from problems.models import problem
from compiler.views import runCode
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
    if request.method == "POST":
        language = request.POST.get('language')
        code = request.POST.get('code')
        print('manideep4',code)
        inputData = request.POST.get('input')
        outputData = runCode(language,code,inputData)
        print('mani',outputData)
        context = {
                    "language": language,
                    "code" : code,
                    "inputData" : inputData,
                    "outputData" : outputData,
                    "req_problem" : req_problem,
                    }
        return render(request,"problem_result.html",context)
    else:
        context = {
            "req_problem" : req_problem,
            }
        return render(request,"problem_detail.html",context)
    
