from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^OnlineChat/$', views.InitPage, name='OnlineChat'),
    url(r'^Submit/$', views.submitData, name='submitData')
    ]