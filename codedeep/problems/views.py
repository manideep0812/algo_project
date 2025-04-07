from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from problems.models import problem
from compiler.views import runCode, compare_outputs
from compiler.models import codeSubmission

# Create your views here.

#to show problems
@login_required
def all_problems(request):
    questions = problem.objects.all()

    context = {
        "all_problems":questions,
    }
    return render(request,"all_problems.html",context)

def home_page(request):

    return render(request,'base.html')

@login_required
def contests(request):

    return render(request,'contests.html')

#to show details of problem
@login_required
def problem_detail(request,id):
    req_problem = problem.objects.get(id=id)
    if request.method == "POST":
        language = request.POST.get('language')
        code = request.POST.get('code')
        inputData = request.POST.get('input')
        
        # Create a submission with the problem
        submission = codeSubmission(
            user=request.user,
            problem=req_problem,
            language=language,
            code=code,
            inputData=inputData
        )
        submission.save()
        
        # Run the code
        outputData = runCode(language, code, inputData)
        submission.outputData = outputData
        
        # Determine verdict
        if "Error:" in outputData or "error" in outputData.lower():
            if "compilation" in outputData.lower():
                submission.verdict = "CE"
            elif "timeout" in outputData.lower():
                submission.verdict = "TLE"
            else:
                submission.verdict = "RE"
        else:
            expected_output = ""
            
            if req_problem.solution_code:
                expected_output = runCode("py", req_problem.solution_code, inputData)
            else:
                # Fallback to testcase1 if no solution code
                expected_output = req_problem.testcase1
                print("No solution code found, using testcase1 as expected output")
            
            # Store the expected output in the submission
            submission.expectedOutput = expected_output
            
            # Compare output with expected output
            if compare_outputs(outputData, expected_output):
                print("OUTPUTS MATCH - ACCEPTED")
                submission.verdict = "AC"
            else:
                print("OUTPUTS DON'T MATCH - WRONG ANSWER")
                submission.verdict = "WA"
        
        submission.save()
        
        context = {
            "language": language,
            "code": code,
            "inputData": inputData,
            "outputData": outputData,
            "req_problem": req_problem,
            "submission": submission,
        }
        return render(request, "problem_result.html", context)
    else:
        context = {
            "req_problem": req_problem,
        }
        return render(request, "problem_detail.html", context)
    
