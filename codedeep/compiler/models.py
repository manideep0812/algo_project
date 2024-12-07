from django.db import models

# Create your models here.
class codeSubmission(models.Model):
    #user = models.CharField(max_length=75)
    #questionName = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    code = models.TextField()
    inputData = models.TextField(null=True,blank=True)
    outputData = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
