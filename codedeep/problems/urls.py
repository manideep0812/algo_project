from django.urls import path,include
from problems.views import all_problems,problem_detail
urlpatterns = [
    path('',all_problems),
    path('<int:id>/',problem_detail),
]