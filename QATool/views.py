from django.shortcuts import render
from django.db import connections
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from testMS.utils import *
from django.core.cache import cache
import cx_Oracle, json, datetime

# Create your views here.

def Dashboard(request):
    return render(request, 'HomepageQA.html')


def UserPermission(request):
    return render(request, 'UserPermission.html')


def TaskAllocation(request):
    return render(request, 'TaskAllocation.html')


def TeamManagement(request):
    teams = getAllTeam()
    operators = getAllOperator()
    # cache.set('operators', operators)
    return render(request, 'TeamManagement.html', {
        'operators' : operators 
    }) 


@csrf_exempt
def LoadOperatorByTeam(request):
    if request.is_ajax():
        operator = []
        data = json.loads(request.body)
        team_id = int(data['team_id'])
        operators = cache.get('operators', 'Empty')

        if operators == 'Empty':
            operator = getUserByTeam(team_id)
        else:
            for i in range(len(operators)):
                o = operators[i]
                if o['TEAM_ID'] == team_id:
                    o['START_WORKING_DATE'] = o['START_WORKING_DATE'].strftime('%d-%b-%Y')
                    if o['LAST_WORKING_DATE'] is not None:
                        o['LAST_WORKING_DATE'] = o['LAST_WORKING_DATE'].strftime('%d-%b-%Y')
                    else: 
                        o['LAST_WORKING_DATE'] = ''
                    operator.append(o)

        return HttpResponse(json.dumps(operator))


def getAllTeam():
    db_conn = connections['default']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM T_QA_TEAM")
        teams = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    return teams


def getAllOperator():
    db_conn = connections['default']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM V_QA_GET_USER_INFO ORDER BY START_WORKING_DATE DESC")
        operators = dictfetchall(cursor)
        for i in range(len(operators)):
            o = operators[i]
            o['START_WORKING_DATE'] = o['START_WORKING_DATE'].strftime('%d-%b-%Y')
            if o['LAST_WORKING_DATE'] is not None:
                o['LAST_WORKING_DATE'] = o['LAST_WORKING_DATE'].strftime('%d-%b-%Y')
            else: 
                o['LAST_WORKING_DATE'] = ''      
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    return operators


def getUserByTeam(team_id):
    db_conn = connections['default']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM V_QA_GET_USER_BY_TEAM WHERE TEAM_ID = {0}".format(team_id))
        users = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    return users
