from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'Homepage/', views.Dashboard, name='QADash'),
    url(r'UserPermission/', views.UserPermission, name='UserPermission'),
    url(r'TaskAllocation/', views.TaskAllocation, name='TaskAllocation'),
    url(r'TeamManagement/', views.TeamManagement, name='TeamManagement'),
    url(r'loadOperator/', views.LoadOperatorByTeam, name='loadOperator'),
    ]