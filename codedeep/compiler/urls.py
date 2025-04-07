from django.urls import path
from compiler.views import submit, submissions
urlpatterns = [
    path('submit/', submit),
    path('submissions/', submissions, name='submissions'),
]