from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^AutoCard/$', views.AutoCardInit, name='SMS'),
    url(r'^AutoMRC/$', views.AutoMRCInit, name='MRC'),
    url(r'^sendSMS/$', views.sendSMS, name='sendSMS'),
    ]