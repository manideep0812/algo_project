from django.db import models

# Create your models here.
class problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(help_text="Enter the problem description. Use newlines to format the text.")
    testcase1 = models.TextField(help_text="Enter the first test case. Use newlines to format the input and output.")
    testcase2 = models.TextField(help_text="Enter the second test case. Use newlines to format the input and output.")
    solution_code = models.TextField(blank=True, null=True, help_text="Python solution code for this problem")

    def __str__(self):
        return self.name
