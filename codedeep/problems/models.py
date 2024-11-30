from django.db import models

# Create your models here.
class problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    testcase1 = models.TextField()
    testcase2 = models.TextField()

    def __str__(self):
        return self.name
