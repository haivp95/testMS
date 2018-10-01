from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<tableau>\d+)/', views.reportTableau, name='Tableau'),
    # url(r'Customer Services', views.reportTableau, name='CStableau'),
    # url(r'Customer Services', views.reportTableau, name='CStableau'),
    ]