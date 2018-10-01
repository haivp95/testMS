from django.shortcuts import render
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponse
from testMS.utils import *
import cx_Oracle, json, xlsxwriter, datetime, csv, io


# ap_ops = cx_Oracle.connect('APP_REPORT_INT[AP_OPS]/Xcvert6uiopp@DBHDWVN-VIETTEL.PROD.ITC.HCNET.VN:1521/HDWVN.HOMECREDIT.VN', encoding = "UTF-8", nencoding = "UTF-8")
# app_ops = cx_Oracle.connect('APP_OPS/app_ops1test@vnvxdbtst01.hcnet.vn:1521/oratest.hcnet.vn', encoding = "UTF-8", nencoding = "UTF-8")

# Create your views here.
def loadReports(request): 
    reports = getAllReports()
    params = getAllReportParams()

    return render(request, 'Report.html', {
        'reports': reports,
        'params': params
    })


def executeReport(request):
    rp_id = request.POST['rp_id']
    rp_name = request.POST['rp_name']
    hasParam = request.POST['hasParam']
    query = 'SELECT * FROM {0}'.format(rp_name)

    if hasParam is '1':
        if 'param_value' in request.POST:        
            params = request.POST.getlist('param_value')
        else:
            params = {}

        if 'param_name' in request.POST:
            param_name = request.POST.getlist('param_name')
        else:
            param_name = {}

        if 'date_param_name' in request.POST:
            date_param = request.POST.getlist('date_param_name')
        else:
            date_param = {}

        if 'to_date' in request.POST:
            to_date = request.POST.getlist('to_date')
        else:
            to_date = {}
        
        if 'from_date' in request.POST:
            from_date = request.POST.getlist('from_date')
        else:
            from_date = {}
        
        query = query + ' WHERE'

        if len(params) > 0:
            for i in range(len(params)):
                value = params[i]
                name = param_name[i]
                query = query + ' {0} IN ({1})'.format(name, value)
                if i < (len(params) - 1):
                    query = query + ' AND'
        
        if len(date_param) > 0:
            if len(params) > 0:
                query = query + ' AND'
            for i in range(len(date_param)):
                date = date_param[i]
                fd = from_date[i]
                td = to_date[i]
                # fd_formatted = datetime.datetime.strptime(fd, '%d/%m/%Y').strftime('%d-%b-%y')
                # td_formatted = datetime.datetime.strptime(td, '%d/%m/%Y').strftime('%d-%b-%y')
                fd_formatted = datetime.datetime.strptime(fd, '%d/%m/%Y').strftime('%Y-%m-%d')
                td_formatted = datetime.datetime.strptime(td, '%d/%m/%Y').strftime('%Y-%m-%d')
                query = query + " {0} BETWEEN '{1}' AND '{2}'".format(date, fd_formatted, td_formatted)
                if i < (len(date_param) - 1):
                    query = query + ' AND'
    
    # query1 = "SELECT HR_CODE, FULL_NAME, START_DATE FROM T_OPS_CC_KPI_LIST WHERE START_DATE BETWEEN '{0}' AND '{1}'".format(fd_formatted, td_formatted)
    print(query)
    db_conn = connections['oracle']
    cursor = db_conn.cursor()
    try:
        cursor.execute(query)
        records = dictfetchall(cursor)
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()
    
    # create a workbook in memory
    output = io.BytesIO()

    # use xlsxwriter library to write to excel file
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})
    # date_format = workbook.add_format({'default_date_format': 'dd/mm/yy'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yy'})

    if len(records) > 0 :
        # write headers with bold format
        a = records[0]
        headers = list(a.keys())
        for i in range(len(headers)):
            worksheet.write(0, i, headers[i], bold)
            
        for i in range(len(records)):
            row = i + 1
            record = records[i]
            values = list(record.values())
            for j in range(len(values)):
                if type(values[j]) is datetime.datetime:
                    # worksheet.write(row, j, values[j], date_format)
                    worksheet.write_datetime(row, j, values[j], date_format)
                else:
                    worksheet.write(row, j, values[j])

        # autofilter(first_row, first_col, last_row, last_col)
        worksheet.autofilter(0, 0, len(records) - 1, len(headers) - 1)
        result = 'success'
    else:
        db_conn = connections['oracle']
        cursor1 = db_conn.cursor()
        try:
            cursor1.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{0}'".format(rp_name))
            columns = dictfetchall(cursor1)
        except cx_Oracle.DatabaseError as e:
            raise e
        finally:
            cursor1.close()
            
        for i in range(len(columns)):
            a = columns[i]
            header = a['COLUMN_NAME']
            worksheet.write(0, i, header, bold)

        worksheet.autofilter(0, 0, 0, len(columns) - 1)
        result = 'No Data'
    workbook.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + rp_name + ".xlsx"

    output.close()
    return response


def getAllReports():
    db_conn = connections['default']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT ID, NAME, SQLQUERY, DSC, HAS_PARAMETER FROM T_OPS_MIS_REPORT WHERE NAME is not null ORDER BY NAME")
        data = dictfetchall(cursor)
        return data
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()


def getAllReportParams():
    db_conn = connections['default']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT ID, REPORTID, NAME, DATATYPE, HINT FROM T_OPS_MIS_RP_PARAM")
        data = dictfetchall(cursor)
        return data
    except cx_Oracle.DatabaseError as e:
        raise e
    finally:
        cursor.close()


@csrf_exempt
def addReport(request):
    if request.is_ajax():
        data = json.loads(request.body)
        hasParam = data['hasParam']
        rp_name = data['rp_name']
        rp_dsc = data['rp_dsc']
        rp_query = data['rp_query']

        if hasParam is 0:
            saveReport(rp_name, rp_dsc, rp_query, hasParam);
        
        if hasParam is 1:           
            params = data['params']
            print(params)
            saveReport(rp_name, rp_dsc, rp_query, hasParam);

            db_conn = connections['default']
            cursor = db_conn.cursor()
            cursor.execute("SELECT s.ID FROM T_OPS_MIS_REPORT s JOIN (SELECT MAX(CREATED_TIME) CREATED_TIME FROM T_OPS_MIS_REPORT) t ON t.CREATED_TIME = s.CREATED_TIME")
            report = cursor.fetchone()
            report_id = report[0]

            for i in range(len(params)):
                param = params[i]
                cursor = db_conn.cursor()
                try:
                    cursor.callproc('PROC_OPS_MIS_T_REPORT_PARAM', ['', report_id, param['Name'], param['Hint'], param['Type']])
                    db_conn.commit()
                except cx_Oracle.DatabaseError as e:
                    db_conn.rollback()
                    raise e                    
                finally:
                    cursor.close()
        return HttpResponse('success')


def saveReport(rp_name, rp_dsc, rp_query, hasParam):
    db_conn = connections['default']
    datetime = timezone.now()
    fmt = "%d-%m-%Y %H:%M:%S"
    datetime = datetime.strftime(fmt)
    cursor = db_conn.cursor()
    try:
        cursor.callproc('PROC_OPS_MIS_T_ADD_REPORT', ['', rp_name, rp_dsc, rp_query, hasParam, 1, datetime])
        db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        db_conn.rollback()
        raise e       
    finally:
        cursor.close()


@csrf_exempt
def deleteReport(request):
        if request.is_ajax():
            data = json.loads(request.body)
            rp_id = data['report_id']

            db_conn = connections['default']
            cursor = db_conn.cursor()
            try:
                cursor.execute("DELETE FROM T_OPS_MIS_REPORT WHERE ID = '{0}'".format(rp_id))
                db_conn.commit()
            except cx_Oracle.DatabaseError as e:
                db_conn.rollback()
                raise e       
            finally:
                cursor.close()
        return HttpResponse('success')


@csrf_exempt    
def loadReportColumns(request):
    if request.is_ajax():
        cols = []
        data = json.loads(request.body)
        rp_name = data['rp_name']

        db_conn = connections['oracle']
        cursor = db_conn.cursor()
        try:
            cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{0}'".format(rp_name))
            columns = dictfetchall(cursor)

            for i in range(len(columns)):
                col = columns[i]
                col_name = col['COLUMN_NAME']
                cols.append(col_name)
        except cx_Oracle.DatabaseError as e:
            raise e       
        finally:
            cursor.close()
        return HttpResponse(json.dumps(cols))


@csrf_exempt
def checkExistView(request):
    if request.is_ajax():
        data = json.loads(request.body)
        rp_name = data['rp_name']

        db_conn = connections['oracle']
        cursor = db_conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM ALL_OBJECTS WHERE OBJECT_NAME = '{0}'".format(rp_name))
            result = cursor.fetchone()
            has_row = result[0]
        except cx_Oracle.DatabaseError as e:
            raise e
        finally:
            cursor.close()
        
        return HttpResponse(json.dumps(has_row))
