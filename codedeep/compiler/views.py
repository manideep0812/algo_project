from django.shortcuts import render
from compiler.forms import codeSubmissionForm
from django.conf import settings
import uuid
import subprocess
from pathlib import Path
from django.contrib.auth.decorators import login_required
from compiler.models import codeSubmission
from problems.models import problem
import re

# Create your views here.
def submit(request):
    if request.method == "POST":
        form = codeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            
            # Set user if authenticated
            if request.user.is_authenticated:
                submission.user = request.user
            
            problem_id = request.POST.get('problem_id')
            if problem_id:
                try:
                    submission.problem = problem.objects.get(id=problem_id)
                except problem.DoesNotExist:
                    pass
            
            # Save the submission
            submission.save()
            
            output = runCode(submission.language, submission.code, submission.inputData)
            submission.outputData = output
            
            if "Error:" in output or "error" in output.lower():
                if "compilation" in output.lower():
                    submission.verdict = "CE"
                elif "timeout" in output.lower():
                    submission.verdict = "TLE"
                else:
                    submission.verdict = "RE"
            else:
                if submission.problem:
                    expected_output = ""
                    if submission.problem.solution_code:
                        expected_output = runCode("py", submission.problem.solution_code, submission.inputData)
                    else:
                        # Fallback to testcase1 if no solution code
                        expected_output = submission.problem.testcase1
                        print("No solution code found, using testcase1 as expected output")
                    
                    submission.expectedOutput = expected_output
                    
                    print("=" * 50)
                    print("ACTUAL OUTPUT:")
                    print(output)
                    print("=" * 50)
                    print("EXPECTED OUTPUT:")
                    print(expected_output)
                    print("=" * 50)
                    
                    # Compare output with expected output
                    if compare_outputs(output, expected_output):
                        print("OUTPUTS MATCH - ACCEPTED")
                        submission.verdict = "AC"
                    else:
                        print("OUTPUTS DON'T MATCH - WRONG ANSWER")
                        submission.verdict = "WA"
                else:
                    submission.verdict = "AC"
            
            submission.save()
            context = {"submission": submission}
            return render(request, "result.html", context)
    else:
        form = codeSubmissionForm()
        context = {"form": form}
        return render(request, "index.html", context)

@login_required
def submissions(request):
    user_submissions = codeSubmission.objects.filter(user=request.user).order_by('-timestamp')
    context = {"submissions": user_submissions}
    return render(request, "submissions.html", context)

def compare_outputs(actual_output, expected_output):
    """
    Compare actual output with expected output, handling whitespace and formatting differences.
    Returns True if outputs match, False otherwise.
    """
    # Normalize line endings
    actual_output = actual_output.replace('\r\n', '\n').replace('\r', '\n')
    expected_output = expected_output.replace('\r\n', '\n').replace('\r', '\n')

    if "Input:" in expected_output and "Output:" in expected_output:
        output_section = expected_output.split("Output:", 1)[1].strip()
        expected_output = output_section.split('\n')[0].strip()
        print(f"Extracted expected answer: '{expected_output}'")
    
    actual_lines = [line.rstrip() for line in actual_output.split('\n')]
    expected_lines = [line.rstrip() for line in expected_output.split('\n')]
    
    while actual_lines and not actual_lines[-1]:
        actual_lines.pop()
    while expected_lines and not expected_lines[-1]:
        expected_lines.pop()
    
    if len(actual_lines) != len(expected_lines):
        print(f"Line count mismatch: Actual has {len(actual_lines)} lines, Expected has {len(expected_lines)} lines")
        return False
    
    for i, (actual_line, expected_line) in enumerate(zip(actual_lines, expected_lines)):
        actual_parts = re.split(r'\s+', actual_line.strip())
        expected_parts = re.split(r'\s+', expected_line.strip())
        
        if actual_parts != expected_parts:
            print(f"Mismatch at line {i+1}:")
            print(f"  Actual:   '{actual_line}'")
            print(f"  Expected: '{expected_line}'")
            print(f"  Actual parts:   {actual_parts}")
            print(f"  Expected parts: {expected_parts}")
            return False
    
    return True

def runCode(language, code, inputData):
    projectPath = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]
    for directory in directories:
        dirPath = projectPath / directory
        if not dirPath.exists():
            dirPath.mkdir(parents=True, exist_ok=True)
    codesDir = projectPath / "codes"
    inputsDir = projectPath / "inputs"
    outputsDir = projectPath / "outputs"

    unique = str(uuid.uuid4())

    codeFileName = f"{unique}.{language}"
    inputFileName = f"in_{unique}.txt"
    outputFileName = f"out_{unique}.txt"

    codeFilePath = codesDir / codeFileName
    inputFilePath = inputsDir / inputFileName
    outputFilePath = outputsDir / outputFileName

    with open(codeFilePath, "w") as codeFile:
        codeFile.write(code)
    with open(inputFilePath, "w") as inputFile:
        inputFile.write(inputData)

    outputData = ""
    try:
        if language == "cpp":
            executablePath = codesDir / unique
            compileResult = subprocess.run(
                ["g++", str(codeFilePath), "-o", str(executablePath), "-lstdc++"],
                capture_output=True,
                text=True,
            )
            if compileResult.returncode != 0:
                outputData = compileResult.stderr  # Capture compilation errors
            else:
                with open(inputFilePath, "r") as inputText:
                    runResult = subprocess.run(
                        [str(executablePath)],
                        stdin=inputText,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    outputData = runResult.stdout if runResult.returncode == 0 else runResult.stderr
        elif language == "c":
            executablePath = codesDir / unique
            compileResult = subprocess.run(
                ["gcc", str(codeFilePath), "-o", str(executablePath)],
                capture_output=True,
                text=True,
            )
            if compileResult.returncode != 0:
                outputData = compileResult.stderr  # Capture compilation errors
            else:
                with open(inputFilePath, "r") as inputText:
                    runResult = subprocess.run(
                        [str(executablePath)],
                        stdin=inputText,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    outputData = runResult.stdout if runResult.returncode == 0 else runResult.stderr

        elif language == "py":
            print(f"Input Data Provided: {inputData}")
            try:
                # Normalize line endings and clean input data
                inputData = inputData.replace('\r\n', '\n').replace('\r', '\n')
                
                # Remove any trailing whitespace from each line while preserving empty lines
                input_lines = inputData.split('\n')
                input_lines = [line.rstrip() for line in input_lines]
                inputData = '\n'.join(input_lines)
                
                # Ensure input data ends with exactly one newline
                if inputData and not inputData.endswith('\n'):
                    inputData += '\n'
                
                # Create a process with pipe for input/output
                process = subprocess.Popen(
                    ["python", str(codeFilePath)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'  # Handle any invalid characters gracefully
                )
                
                # Send input data and get output
                try:
                    print(f"Sending input data: {repr(inputData)}")  # Debug print
                    stdout, stderr = process.communicate(input=inputData, timeout=10)
                    
                    # Clean up output data
                    if stdout:
                        stdout = stdout.rstrip()  # Remove trailing whitespace
                    if stderr:
                        stderr = stderr.rstrip()  # Remove trailing whitespace
                    
                    if process.returncode == 0:
                        outputData = stdout if stdout else "Program executed successfully with no output."
                    else:
                        outputData = f"Error:\n{stderr}" if stderr else "Program failed with no error message."
                except subprocess.TimeoutExpired:
                    process.kill()
                    outputData = "Error: Code execution timed out (10 seconds limit)"
                except Exception as e:
                    outputData = f"Error during execution: {str(e)}"
            except Exception as e:
                outputData = f"Unexpected error: {str(e)}"
    except Exception as e:
        outputData = f"Unexpected error: {str(e)}"
    print(f"Output Data: {outputData}")
    print(f"Process Return Code: {process.returncode if 'process' in locals() else 'N/A'}")

    with open(outputFilePath, "w") as outputFile:
        outputFile.write(outputData)

    return outputData
