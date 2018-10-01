from django_auth_ldap.config import LDAPSearch
#from django_cron import CronJobBase, Schedule
from django.db import connections
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from testMS.dict import *
from testMS.utils import *
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.template import RequestContext
import requests, uuid, cx_Oracle, json 
import ldap, unicodedata, django.contrib.auth, datetime, celery
from django.conf import settings

print(settings.BASE_DIR)
print(settings.STATIC_ROOT)

def countDataInDb(): 
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM T_OPS_MIS_VNPOST_API")
        row = cursor.fetchone()
        return row
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()


def connectToAPIAndInsertToDb(start):
    response = requests.get(f'https://ctt.vnpost.vn/serviceApi/v1/getDelivery?token=ca608900-02a0-4a0d-aefa-6ad4ae9a5793&fromRecord={start}',proxies=proxies)
    vnpAPI = response.json()
    if 'Deliverys' in vnpAPI:
        insertToDb(vnpAPI['Deliverys'])
        toltalRecord = vnpAPI['TotalRecord']
        if toltalRecord == 20000:
            connectToAPIAndInsertToDb(toltalRecord + 20000)



def LoginLDAP (request):
    ldap.PORT = 8433
    con = ldap.initialize('LDAP://vnhqpdc03.hcnet.vn:389')

    if request.method == 'GET':
        return render(request, 'Login.html')

    if request.method == "POST":
        base = 'ou=hcnet_users,dc=hcnet,dc=vn'    
        search = ['displayName','mail','givenName','sn','sAMAccountName','description','mobile','department', 'userPrincipalName','name/cn']
        scope = ldap.SCOPE_SUBTREE
        username = request.POST.get('username')
        password = request.POST.get('password') 
        binddn = "%s\%s" % ('hcnet',username)
        try:
            con.bind_s(binddn, password)    
            result = con.search_s(base, int(scope),"sAMAccountName=%s" % username, search)

            # set default language
            if 'lang' not in request.session:
                content = languageContent("en")
                request.session['lang'] = "en"
                request.session['lang_content'] = content

            # store use info to session
            request.session['displayName'] = result[0][1]['sAMAccountName'][0].decode('utf-8')
            request.session['title'] = result[0][1]['description'][0].decode('utf-8')
            request.session['fullName'] = (result[0][1]['sn'][0].decode('utf-8')
                    + ' ' + result[0][1]['givenName'][0].decode('utf-8'))
            request.session['department'] = result[0][1]['department'][0].decode('utf-8')
            request.session.modified = True
            email = result[0][1]['mail'][0].decode('utf-8')

            if 'Operations' in result[0][1]['department'][0].decode('utf-8'):
                if User.objects.filter(username=username).count() == 0:
                    info = findUserGroup(email)
                    # get first name
                    firstname = info[0]
                    # get last name
                    lastname = info[1]
                    # get section name
                    section = info[3]
                    # get title
                    title = info[4]

                    User.objects.create_user(username=username, password=password,email=email, first_name = firstname, last_name = lastname)
                    created_user = User.objects.get(username=username)   

                    if section.lower() == 'customer service':
                        cs = Group.objects.get(name='CS') 
                        cs.user_set.add(created_user)
                    elif section.lower() == 'contract processing':
                        cp = Group.objects.get(name='CP') 
                        cp.user_set.add(created_user)                       
                    elif section.lower() == 'call center':
                        cc = Group.objects.get(name='CC') 
                        cc.user_set.add(created_user)
                    elif section.lower() == 'ops process and quality control':
                        qa = Group.objects.get(name='QA Process') 
                        qa.user_set.add(created_user)

                    if ('manager' in title.lower()) or ('supervisor' in title.lower()):
                            ops_manager = Group.objects.get(name='OPS Manager') 
                            ops_manager.user_set.add(created_user)

            # set permission
            groupList = []
            user = User.objects.get(username=username)
            group = list(user.groups.all())

            for i in range(len(group)):
                name = str(group[i])
                groupList.append(name)
            request.session['group'] = groupList

            # return render(request, 'Index.html')
            return redirect('Homepage')

        except ldap.INVALID_CREDENTIALS:
            return render(request, 'Login.html')
        except ldap.INVALID_DN_SYNTAX:
            return render(request, 'Login.html')
        except ldap.INVALID_SYNTAX:
            return render(request, 'Login.html')   


def Logout(request):
    request.session.flush()
    return render(request, 'Login.html')


@csrf_exempt
def changeLanguage(request):
    if request.is_ajax():
        data = json.loads(request.body)
        lang = data["lang"] 
        content = languageContent(lang)
        request.session['lang'] = lang
        request.session['lang_content'] = content 
        return HttpResponse(lang)


def findUserGroup(email):
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM V_OPS_MIS_USER_HR WHERE EMAIL LIKE '%{0}%' AND ROWNUM = 1".format(email))
        row = cursor.fetchone()
        return row
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()







