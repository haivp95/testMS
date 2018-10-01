from django.shortcuts import render
from django.db import connections
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from testMS.utils import *
import requests, cx_Oracle, uuid, json, io
# Create your views here.

# ap_ops = cx_Oracle.connect('APP_REPORT_INT[AP_OPS]/Xcvert6uiopp@DBHDWVN-VIETTEL.PROD.ITC.HCNET.VN:1521/HDWVN.HOMECREDIT.VN', encoding = "UTF-8", nencoding = "UTF-8")
# app_ops = cx_Oracle.connect('APP_OPS/app_ops1test@vnvxdbtst01.hcnet.vn:1521/oratest.hcnet.vn', encoding = "UTF-8", nencoding = "UTF-8")

# @login_required
def loadPage(request):
    return render(request, 'Customer_Feedback.html')

# @login_required
def reportPage(request):
    csEmployee = getAllCSEmployee()
    return render(request, 'Feedback_Report.html', {
        'csEmployee': csEmployee
    })

@csrf_exempt
def receiveAjaxData(request): 
    if request.is_ajax():
        data = json.loads(request.body)
        username = request.session['displayName']
        vote = data["vote"]
        savetoDB(username, vote)
        return HttpResponse('success')


@csrf_exempt
def showReport(request):
    if request.is_ajax():
        data = json.loads(request.body)
        user = data["user"]
        fromDate = data["from"]
        toDate = data["to"]
        returnList = getReport(user, fromDate, toDate)   
         
        return HttpResponse(json.dumps(returnList))


def getAllCSEmployee():
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT u.FULL_NAME, u.USERNAME, u.EMAIL FROM T_OPS_USER u WHERE LOWER(u.SECTIONEN) LIKE '%customer service%' AND STATUS = 1 ORDER BY u.EMAIL")
        returnList = dictfetchall(cursor)
        return returnList
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()


def getReport(user, fromDate, toDate):
    db_conn = connections['default']
    cursor = db_conn.cursor()
    returnList = []
    if user == 'empty':
        query = f"SELECT fb.USERNAME, fb.VOTE, fb.TIMESTAMP FROM T_OPS_MIS_CUSTOMER_FEEDBACK fb WHERE to_date(fb.TIMESTAMP, 'dd/mm/yyyy hh24:mi:ss') BETWEEN TO_DATE('{fromDate}', 'dd/mm/yyyy hh24:mi:ss') AND TO_DATE('{toDate}', 'dd/mm/yyyy hh24:mi:ss') + 1 ORDER BY fb.TIMESTAMP DESC"        
    else:
        query = f"SELECT fb.USERNAME, fb.VOTE, fb.TIMESTAMP FROM T_OPS_MIS_CUSTOMER_FEEDBACK fb WHERE fb.USERNAME LIKE '%{user}%' AND to_date(fb.TIMESTAMP, 'dd/mm/yyyy hh24:mi:ss') BETWEEN TO_DATE('{fromDate}', 'dd/mm/yyyy hh24:mi:ss') AND TO_DATE('{toDate}', 'dd/mm/yyyy hh24:mi:ss') + 1 ORDER BY fb.TIMESTAMP DESC"
    try:
        cursor.execute(query)  
        returnList = dictfetchall(cursor)
        return returnList
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()   


def savetoDB(user, point):
    db_conn = connections['default']
    cursor = db_conn.cursor()
    username = user
    vote = point
    datetime = timezone.now()
    fmt = "%d-%m-%Y %H:%M:%S"
    datetime = datetime.strftime(fmt)

    try:
        cursor.callproc('PROC_OPS_MIS_T_CUST_FEEDBACK', ['', username, vote, datetime])
        db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e       
    finally:
        cursor.close() 







