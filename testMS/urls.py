
from django.contrib import admin
from . import views
from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    url(r'Home/', include('Homepage.urls')),
    url(r'Report/', include('Report.urls')),
    url(r'ContractProcessing/', include('CP.urls')),
    url(r'CustomerService/', include('CS.urls')),
    url(r'CallCenter/', include('CC.urls')),
    url(r'Tableau/', include('Tableau.urls')),
    url(r'QA/', include('QATool.urls')),
    url('admin', admin.site.urls),
    # url('', views.Login, name = 'loginPage'),
    url(r'logout/', views.Logout, name = 'Logout'),
    url(r'changeLanguage/', views.changeLanguage, name = 'language'),
    url(r'', views.LoginLDAP, name = 'loginLDAP'),
]
