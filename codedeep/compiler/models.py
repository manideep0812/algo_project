from django.db import models
from django.contrib.auth.models import User
from problems.models import problem

# Create your models here.
class codeSubmission(models.Model):
    VERDICT_CHOICES = [
        ('AC', 'Accepted - Your solution is correct'),
        ('WA', 'Wrong Answer - Your solution produced incorrect output'),
        ('TLE', 'Time Limit Exceeded - Your solution took too long to execute'),
        ('MLE', 'Memory Limit Exceeded - Your solution used too much memory'),
        ('RE', 'Runtime Error - Your solution crashed during execution'),
        ('CE', 'Compilation Error - Your code couldn\'t be compiled'),
        ('SE', 'System Error - An unexpected error occurred in the system'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(problem, on_delete=models.CASCADE, null=True, blank=True)
    language = models.CharField(max_length=100)
    code = models.TextField()
    inputData = models.TextField(null=True, blank=True)
    outputData = models.TextField(null=True, blank=True)
    expectedOutput = models.TextField(null=True, blank=True)
    verdict = models.CharField(max_length=10, choices=VERDICT_CHOICES, default='SE')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.problem.name if self.problem else 'Custom'} - {self.verdict}"
