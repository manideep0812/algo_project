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
            with open(inputFilePath, "r") as inputText:
                runResult = subprocess.run(
                    ["python", str(codeFilePath)],
                    stdin=inputText,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                outputData = runResult.stdout if runResult.returncode == 0 else runResult.stderr
    except Exception as e:
        outputData = f"Unexpected error: {str(e)}"
    print(f"Subprocess STDOUT: {runResult.stdout}")
    print(f"Subprocess STDERR: {runResult.stderr}")
    print(f"Subprocess Return Code: {runResult.returncode}")

    with open(outputFilePath, "w") as outputFile:
        outputFile.write(outputData)

    return outputData
