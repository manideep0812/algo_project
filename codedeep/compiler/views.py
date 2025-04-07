from django.shortcuts import render
from compiler.forms import codeSubmissionForm
from django.conf import settings
import uuid
import subprocess
from pathlib import Path

# Create your views here.
def submit(request):
    if request.method == "POST":
        form = codeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()
            output = runCode(submission.language,submission.code,submission.inputData)
            print(output)
            submission.outputData = output
            submission.save()
            context = {"submission":submission,}
            return render(request,"result.html",context)
    else:
        form=codeSubmissionForm()
        context = {"form" : form,}
        return render(request,"index.html",context)


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
        if language == "cpp" or language == "c":
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
