#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from testMS.utils import *
from django.contrib.auth.models import User
from django.db import transaction
import requests, os, json, cx_Oracle, unicodedata, uuid, xlsxwriter


proxies = {
    "http": "cacheproxy.hcnet.vn:8080",
    "https": "cacheproxy.hcnet.vn:8080",
}

# @login_required
def AutoCardInit(request):
    count = getNumOfRecord()
    connectToAPIAndInsertToDb(count)
    updateNumOfRecord()
    
    dataList = getAutoCardData()
    return render(request, 'IndexCard.html', {
        'data' : dataList
    })


def AutoMRCInit(request):
    count = getNumOfRecord()
    connectToAPIAndInsertToDb(count)
    updateNumOfRecord()

    dataList = getAutoMRCData()
    return render(request, 'IndexMRC.html', {
        'data' : dataList
    })


def getAutoMRCData():
    db_conn = connections['oracle']
    finalResult = []
    cursor = db_conn.cursor()
    try:  
        query = "SELECT * FROM V_OPS_MIS_AUTO_MRC"     
        cursor.execute(query)
        finalResult = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    
    return finalResult



def getAutoCardData():
    db_conn = connections['oracle']
    finalResult = []
    cursor = db_conn.cursor()
    try:  
        query = "SELECT * FROM V_OPS_MIS_AUTO_CARD"     
        cursor.execute(query)
        finalResult = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    
    return finalResult


#@transaction.atomic
@csrf_exempt
def sendSMS(request):
    if request.is_ajax():
        data = json.loads(request.body)
        records = data['Data']
        sms_type = data['Type']
        records = records.replace("&#39;", "\"")
        records = json.loads(records)

        xml = prepareXMLString(records, sms_type)  

        headers = {'Content-Type': 'application/xml'}
        response = requests.post("http://smtsend-uat.hcnet.vn/SmtSend.svc/xml", data=xml, headers=headers)

        msg = response.content
        msg = msg.decode("utf-8")
        username = request.session['displayName']
        # if 'success' in msg:
        #     print('dung roi nha')
        saveSMSHistory(msg, records, username, sms_type)
        #markSentSMS(records, sms_type)
        return HttpResponse(msg)



def prepareXMLString(sendList, sms_type):
    xml = ''
    # xml = "<request>"
    # xml += "<sms>"
    # xml += "<phone>01269984162</phone>"
    # xml += "<content>Buu dien khong phat duoc Giay Chung nhan Dang Ky Xe May. Ma buu pham cua KH la:  LOL!. Vui long lien he so 1900545481 de nhan</content>"
    # xml += "<group>OPS-CP</group>"
    # xml += "<messagecode>MRC_FINISH_CONTRACT</messagecode>"
    # xml += "</sms>"
    # xml += "</request>"

    if sms_type == 'CARD':
        xml = "<request>"
        for i in range(len(sendList)): 
            record = sendList[i]    
            xml += "<sms>"
            # xml += "<phone>{0}</phone>".format(record["PHONE_NUMBER"])
            xml += "<phone>01269984162</phone>"
            xml += "<content>Buu dien khong phat duoc The tin dung cua Quy khach. Ma buu pham cua KH la: {0}. Vui long lien he so (024) 38165018 - 0915233199 de nhan</content>".format(record["ITEM_CODE"])
            xml += "<group>OPS-CP</group>"
            xml += "<messagecode>CC_VNPOST_CANNOT_DELIVER_CARD</messagecode>"
            xml += "</sms>"
        xml += "</request>"
    
    if sms_type == 'MRC':
        xml = "<request>"
        for i in range(len(sendList)): 
            record = sendList[i]    
            xml += "<sms>"
            # xml += "<phone>{0}</phone>".format(record["PHONE_NUMBER"])
            xml += "<phone>01269984162</phone>"
            xml += "<content>Buu dien khong phat duoc Giay Chung nhan Dang Ky Xe May. Ma buu pham cua KH la:  {0}. Vui long lien he so 1900545481 de nhan</content>".format(record["ITEM_CODE"])
            xml += "<group>OPS-CP</group>"
            xml += "<messagecode>MRC_FINISH_CONTRACT</messagecode>"
            xml += "</sms>"
        xml += "</request>"
    return xml


def markSentSMS(itemList, sms_type):
    db_conn = connections['oracle']
    cursor = db_conn.cursor()

    try:
        for i in range(len(itemList)):
            item = itemList[i]  
            cursor.callproc('PROC_OPS_MIS_SMS_SENT', [item["CONTRACT_NUMBER"], item["PHONE_NUMBER"], item["ITEM_CODE"], sms_type])
            db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e  
    finally:
        cursor.close()


def saveSMSHistory(msg, itemList, username, sms_type):
    db_conn = connections['default']
    cursor = db_conn.cursor()
    # summaryId = str(uuid.uuid4())
    content = str(msg)
    date_time = timezone.now()
    fmt = "%d-%m-%Y %H:%M:%S"
    date_time = date_time.strftime(fmt)
    try:
        #save to  summary table
        cursor.callproc('PROC_OPS_MIS_T_SMS_SUMMARY', ['', content, username, sms_type, date_time])
        db_conn.commit()

        # get summary id
        cursor.execute("SELECT s.ID FROM T_OPS_MIS_SMS_SUMMARY s JOIN (SELECT MAX(INSERT_TIMESTAMP) INSERT_TIMESTAMP FROM T_OPS_MIS_SMS_SUMMARY) t ON t.INSERT_TIMESTAMP = s.INSERT_TIMESTAMP")
        summary = cursor.fetchone()
        summary_id = summary[0]

        # save to detail table
        for i in range(len(itemList)):
            item = itemList[i]  
            # detailId = str(uuid.uuid4())
            msg = "Buu dien khong phat duoc The tin dung cua Quy khach. Ma buu pham cua KH la: {0}. Vui long lien he so (024) 38165018 - 0915233199 de nhan".format(item["ITEM_CODE"])
            insert_dt = timezone.now()
            insert_dt = insert_dt.strftime(fmt)
            cursor.callproc('PROC_OPS_MIS_T_SMS_DETAILS', ['', summary_id, item["CONTRACT_NUMBER"], item["ITEM_CODE"], item["PHONE_NUMBER"], msg, insert_dt])
            db_conn.commit()

    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e       
    finally:
        cursor.close()


#@transaction.atomic
def connectToAPIAndInsertToDb(start):
    response = requests.get(f'https://ctt.vnpost.vn/serviceApi/v1/getDelivery?token=ca608900-02a0-4a0d-aefa-6ad4ae9a5793&fromRecord={start}',proxies=proxies)
    vnpAPI = response.json()
    if 'Deliverys' in vnpAPI:
        totalRecord = vnpAPI['TotalRecord']
        delivery = vnpAPI['Deliverys']

        insertToDb(vnpAPI['Deliverys'])
        if totalRecord == 20000:
            connectToAPIAndInsertToDb(start + 20000)


def getNumOfRecord(): 
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM T_OPS_MIS_VNP_NUM_OF_RECORD")
        row = cursor.fetchone()
        count = row[0]
        return count
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()


def updateNumOfRecord(): 
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute("UPDATE T_OPS_MIS_VNP_NUM_OF_RECORD SET NUM_OF_RECORD = (SELECT COUNT(*) FROM T_OPS_MIS_VNPOST_API)")
        db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e
    finally:
        cursor.close()


def insertToDb(insertDict):
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        for i in range(len(insertDict)):
            DeliveryID = insertDict[i]['DeliveryID']
            ItemCode = insertDict[i]['ItemCode']
            CustomerCode = insertDict[i]['CustomerCode']
            AcceptancePOSCode = insertDict[i]['AcceptancePOSCode']
            ToPOSCode = insertDict[i]['ToPOSCode']
            SendingTime = insertDict[i]['SendingTime']
            DeliveryTime = insertDict[i]['DeliveryTime']
            DeliveryTimes = insertDict[i]['DeliveryTimes']
            ReceiverName = insertDict[i]['ReceiverName']
            if ReceiverName != '':
                ReceiverName = str(ReceiverName).replace("'","")
            else: 
                ReceiverName = 'None'
            InputTime = insertDict[i]['InputTime']
            CreateTime = insertDict[i]['CreateTime']
            LastUpdateTime = insertDict[i]['LastUpdateTime']
            IsDeliverable = insertDict[i]['IsDeliverable']
            if IsDeliverable:
                IsDeliverable = 1
            else:
                IsDeliverable = 0
            IsReturn = insertDict[i]['IsReturn']
            if IsReturn:
                IsReturn = 1
            else:
                IsReturn = 0
            DeliveryNote = insertDict[i]['DeliveryNote']
            if DeliveryNote != '':
                DeliveryNote = str(DeliveryNote).replace("'","")
            else: 
                DeliveryNote = 'None'
            CauseCode = insertDict[i]['CauseCode']
            CauseName = insertDict[i]['CauseName']
            if CauseName != '':
                CauseName = str(CauseName).replace("'","")
            else: 
                CauseName = 'None'
            SolutionCode = insertDict[i]['SolutionCode']
            SolutionName = insertDict[i]['SolutionName']
            if SolutionName != '':
                SolutionName = str(SolutionName).replace("'","")
            else: 
                SolutionName = 'None'
            DataCode = insertDict[i]['DataCode']

            cursor.callproc('PROC_OPS_MIS_VNP_INSERT', [DeliveryID, ItemCode, CustomerCode, AcceptancePOSCode, ToPOSCode, SendingTime, DeliveryTime, DeliveryTimes, ReceiverName, InputTime, CreateTime, LastUpdateTime, IsDeliverable, IsReturn, DeliveryNote, CauseCode, CauseName, SolutionCode, SolutionName, DataCode])
            # query = f"INSERT INTO T_OPS_MIS_VNPOST_API VALUES('{DeliveryID}', '{ItemCode}', '{CustomerCode}', '{AcceptancePOSCode}', '{ToPOSCode}', '{SendingTime}', '{DeliveryTime}', '{DeliveryTimes}', N'{ReceiverName}', '{InputTime}', '{CreateTime}', '{LastUpdateTime}', '{IsDeliverable}', '{IsReturn}', N'{DeliveryNote}', '{CauseCode}', N'{CauseName}', '{SolutionCode}', N'{SolutionName}', N'{DataCode}')"
            # cursor.execute(query)
            
            db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e      
    finally:
        cursor.close()






