from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.loadReports, name='Reports'),
    url(r'^add_report/$', views.addReport, name='addReport'),
    url(r'^del_report/$', views.deleteReport, name='delReport'),
    url(r'^load_col/$', views.loadReportColumns, name='loadCol'),
    url(r'^export_report/$', views.executeReport, name='execute'),
    url(r'^check_view/$', views.checkExistView, name='checkView'),
]