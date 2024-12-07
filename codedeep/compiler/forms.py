from django import forms
from compiler.models import codeSubmission

languageChoices = [
    {'Python','py'},
    {'C','c'},
    {'C++','cpp'},
]

class codeSubmissionForm(forms.ModelForm):
    language = forms.ChoiceField(choices=languageChoices)

    class Meta:
        model = codeSubmission
        fields = ["language","code","inputData"]