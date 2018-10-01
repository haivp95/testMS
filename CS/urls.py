from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.loadPage, name='loadFeedbackPage'),
    url(r'^receiveData/$', views.receiveAjaxData, name='receiveData'),
    url(r'^feedback_report/$', views.reportPage, name='feedbackReport'),
    url(r'^show_report/$', views.showReport, name='showReport')
]