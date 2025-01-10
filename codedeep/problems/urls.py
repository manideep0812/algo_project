'''from django.urls import path,include
from problems.views import all_problems,problem_detail,home_page,contests
urlpatterns = [
    path('',home_page),
    path('contests/',contests),
    path('problems/',all_problems),
    path('problems/<int:id>/',problem_detail),
]'''
from django.urls import path
from problems.views import all_problems, problem_detail, home_page, contests

urlpatterns = [
    path('', home_page, name='home'),
    path('contests/', contests, name='contests'),
    path('problems/', all_problems, name='all_problems'),
    path('problems/<int:id>/', problem_detail, name='problem_detail'),
]
