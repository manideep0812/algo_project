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

def runCode(language,code,inputData):
    projectPath = Path(settings.BASE_DIR)
    directories = ["codes","inputs","outputs"]
    for directory in directories:
        dirPath = projectPath/directory
        if not dirPath.exists():
            dirPath.mkdir(parents=True,exist_ok=True)
    codesDir = projectPath/"codes"
    inputsDir = projectPath/"inputs"
    outputsDir = projectPath/"outputs"

    unique = str(uuid.uuid4())

    codeFileName = f"{unique}.{language}"
    inputFileName = f"in_{unique}.txt"
    outputFileName = f"out_{unique}.txt"

    codeFilePath = codesDir / codeFileName
    inputFilePath = inputsDir / inputFileName
    outputFilePath = outputsDir / outputFileName

    with open(codeFilePath,"w") as codeFile:
        codeFile.write(code)
    with open(inputFilePath,'w') as inputFile:
        inputFile.write(inputData)
    with open(outputFilePath,"w") as outputFile:
        pass # here we are creating an empty file

    if language == "cpp" or language == "c":
        executablePath = codesDir/unique
        compileResult = subprocess.run(
            ["gcc",str(codeFilePath),"-o",str(executablePath)]
        )
        if compileResult.returncode == 0:
            with open(inputFilePath,'r') as inputText:
                with open(outputFilePath,"w") as outputText:
                    subprocess.run(
                        [str(executablePath)],
                        stdin=inputText,
                        stdout=outputText,
                    )
    elif language == "py":
        with open(inputFilePath,'r') as inputText:
            with open(outputFilePath,'w') as outputText:
                subprocess.run(
                    ["python3",str(codeFilePath)],
                    stdin=inputText,
                    stdout=outputText,
                )
    
    with open(outputFilePath,'r') as outputFile:
        outputData = outputFile.read()
    
    return outputData