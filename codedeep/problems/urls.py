from django.urls import path,include
from problems.views import all_problems,problem_detail,home_page
urlpatterns = [
    path('',home_page),
    path('problems/',all_problems),
    path('<int:id>/',problem_detail),
]