from django.shortcuts import render
from django.db import connections
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from testMS.utils import *
import cx_Oracle, json, datetime

# Create your views here.

def InitPage(request):
    inquiries = getReasonList('Inquiry')
    complaints = getReasonList('Complaint')
    return render(request, 'OnlineChat.html', {
        'inquiries': inquiries,
        'complaints': complaints
    })


def getReasonList(reason_type):
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT replace(REASON, '''', '') REASON FROM AP_OPS.V_OPS_CC_ONLINE_CHAT WHERE REASON_TYPE = '{0}'".format(reason_type))
        reason = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    return reason


@csrf_exempt
def submitData(request):
    if request.is_ajax():
        data = json.loads(request.body)
        client = data["client"]
        contract = data["contract"]
        isNew = data["isNew"]
        reason = data["reason"]
        reason_type = data["reason_type"]

        user = request.session["displayName"]
        dt = datetime.datetime.now()
        dt_format = dt.strftime('%d-%b-%y %H:%M:%S')
        d1 = dt.strftime('%d-%b-%y')
        # print(d1)
        # print(type(dt_format))
        date = datetime.datetime.strptime(dt_format, '%d-%b-%y %H:%M:%S').date()
        # print(date)
        # print(type(date))
        time = datetime.datetime.strptime(dt_format, '%d-%b-%y %H:%M:%S').time()
        db_conn = connections['oracle']
        cursor = db_conn.cursor()
        query = "INSERT INTO T_OPS_CC_ONLINE_CHAT VALUES ('{0}', to_date('{1}', 'DD-MON-YY HH24:MI:SS'), '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(user, dt_format, time, client, isNew, contract, reason_type, reason)
        print(query)
        try:
            cursor.execute(query)
            db_conn.commit()
        except cx_Oracle.DatabaseError as e:
            db_conn.rollback()
            raise e
        finally:
            cursor.close()
        return HttpResponse('success')


