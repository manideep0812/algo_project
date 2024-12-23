from django.urls import path,include
from problems.views import all_problems,problem_detail,home_page,contests
urlpatterns = [
    path('',home_page),
    path('contests/',contests),
    path('problems/',all_problems),
    path('problems/<int:id>/',problem_detail),
]